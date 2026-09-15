"""Shared machinery for the KPP tools: text comparison, PDF parsing, the
answer-key adapters and the question index.

Nothing here writes anything. The two drivers do:

    tools/lock-questions.py   CEM PDF   -> kpp/questions.js   (frozen)
    tools/build-answers.py    the keys  -> kpp/answers.js

Two rules everything here follows:
  - match questions by STEM TEXT, never by number  (numbering shifts per edition)
  - compare answers by CONTENT, never by letter    (option order shifts too)
"""
import sys, re, json, difflib, hashlib, pathlib, unicodedata

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pypdf import PdfReader

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
# Emitted as JS, not JSON: browsers block fetch() on file:// origins, so the
# page must be able to load its data with plain <script> tags to work when
# someone just double-clicks the file.
QUESTIONS_JS = ROOT / 'kpp' / 'questions.js'
ANSWERS_JS = ROOT / 'kpp' / 'answers.js'
CEM_PDF = DOCS / 'KPP2026-CEM-official.pdf'

# --------------------------------------------------------------- text helpers

# Vulgar fractions must survive normalisation: '¼ wymiaru przednio-tylnego' and
# '⅔ wymiaru przednio-tylnego' are different answers, and stripping the glyph
# makes them identical strings.
FRACTIONS = {'¼': ' 1/4 ', '½': ' 1/2 ', '¾': ' 3/4 ', '⅓': ' 1/3 ', '⅔': ' 2/3 ',
             '⅕': ' 1/5 ', '⅖': ' 2/5 ', '⅗': ' 3/5 ', '⅘': ' 4/5 ',
             '⅙': ' 1/6 ', '⅚': ' 5/6 ', '⅛': ' 1/8 ', '⅜': ' 3/8 ',
             '⅝': ' 5/8 ', '⅞': ' 7/8 '}


def norm(s):
    s = s.lower().replace('„', '"').replace('”', '"')
    for glyph, ascii_ in FRACTIONS.items():
        s = s.replace(glyph, ascii_)
    # digits, %, separators and comparators carry meaning in dosage answers
    s = re.sub(r'[^a-ząćęłńóśźż0-9%.,/<>= -]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def toks(s):
    return {w for w in norm(s).split() if len(w) > 3}


REF_RE = re.compile(r'\b(?:prawdziw\w*|poprawn\w*|prawidłow\w*|prawidlow\w*)\b')
META_RE = re.compile(r'^(wszystkie|wszystkich|żadne|zadne|żadna|zadna|'
                     r'prawdziwe|poprawne|prawidłowe|prawidlowe)\b')


def canon(text, options):
    """Reduce an answer to what it asserts: a set of pointed-at letters, a
    special token, or its own text."""
    n = norm(text)
    concrete = frozenset(o['letter'] for o in options if not META_RE.match(norm(o['text'])))

    if re.search(r'(wszystkie|wszystkich).{0,25}(fałszyw|falszyw)', n):
        return ('ALL_FALSE',)
    if re.match(r'^(żadne|zadne|żadna|zadna)\b', n):
        return ('NONE',)
    if re.match(r'^(wszystkie|wszystkich)\b', n) and not re.search(r'\b[a-e]\b', n):
        return ('LETTERS', concrete)
    if REF_RE.search(n):
        letters = {x.upper() for x in re.findall(r'\b([a-e])\b', REF_RE.split(n)[-1])}
        letters &= {o['letter'] for o in options}
        if letters:
            return ('LETTERS', frozenset(letters))
    return ('TEXT', n)


def aligned(o1, o2, floor=0.45):
    """Same options in the same positions? Guards letter-set comparison."""
    m1 = {o['letter']: norm(o['text']) for o in o1 if not META_RE.match(norm(o['text']))}
    m2 = {o['letter']: norm(o['text']) for o in o2 if not META_RE.match(norm(o['text']))}
    shared = set(m1) & set(m2)
    if not shared:
        return False
    return sum(sim(m1[L][:90], m2[L][:90]) for L in shared) / len(shared) >= floor


SPECIAL = ('LETTERS', 'NONE', 'ALL_FALSE')
NUM_RE = re.compile(r'\d+(?:[.,]\d+)?')


def numbers(s):
    return NUM_RE.findall(norm(s))


def same_answer(t1, o1, t2, o2):
    """An option that points at other options can only match another pointer.

    Never short-circuit pointers on raw text similarity: 'prawdziwe są
    odpowiedzi A i C' and '...A, B i C' score 0.967 while asserting different
    things.

    Answers here are mostly dosages, rates and depths, where the numbers are
    the whole content and the words are shared boilerplate — '10-20
    oddechów/minutę' and '25-50 oddechów/minutę' score 0.90 on the suffix
    alone. So differing numbers mean differing answers, whatever the prose
    similarity says.
    """
    c1, c2 = canon(t1, o1), canon(t2, o2)
    if c1[0] in SPECIAL or c2[0] in SPECIAL:
        if c1[0] != c2[0]:
            return False
        if c1[0] == 'LETTERS':
            return c1[1] == c2[1] and aligned(o1, o2)
        return True
    if numbers(t1) != numbers(t2):
        return False
    return sim(norm(t1), norm(t2)) >= 0.82


# ------------------------------------------------------------------ PDF input

def char_stream(path):
    runs = []

    def visitor(text, cm, tm, fd, fs):
        if text:
            runs.append(('Bold' in str(fd.get('/BaseFont', '') if fd else ''), text))

    for pg in PdfReader(str(path)).pages:
        pg.extract_text(visitor_text=visitor)

    chars, flags, prev_space = [], [], False
    for is_bold, text in runs:
        for ch in text:
            if ch.isspace():
                if not prev_space:
                    chars.append(' ')
                    flags.append(False)
                prev_space = True
            else:
                chars.append(ch)
                flags.append(is_bold)
                prev_space = False
    return ''.join(chars), flags


def parse_pdf(path, read_key):
    text, flags = char_stream(path)
    # The dot after the number is optional: the 2025 edition's PDF converter
    # drops it on the first question of each page ('Nr 175 U poszkodowanego'),
    # which silently cost 37 questions when the dot was required.
    starts = [(int(m.group(1)), m.start(), m.end())
              for m in re.finditer(r'Nr\.?\s*(\d+)\.?\s', text)]
    out = []
    for i, (nr, s, e) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        opts, expect = [], 'A'
        for m in re.finditer(r'(?<![A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż])([A-E])\.\s', text[e:end]):
            if m.group(1) != expect:
                continue
            opts.append((m.group(1), e + m.start(), e + m.end()))
            expect = chr(ord(expect) + 1)
            if expect > 'E':
                break
        if len(opts) < 2:
            continue
        options, correct = [], None
        for j, (letter, ls, le) in enumerate(opts):
            hi = opts[j + 1][1] if j + 1 < len(opts) else end
            options.append({'letter': letter, 'text': text[le:hi].strip(' .').strip()})
            if read_key:
                tot = b = 0
                for k in range(le, hi):
                    if not text[k].isspace():
                        tot += 1
                        b += flags[k]
                if tot and b / tot > 0.5:
                    correct = letter
        out.append({'nr': nr, 'stem': text[e:opts[0][1]].strip(),
                    'options': options, 'correct': correct})
    return out


# ------------------------------------------------------- answer-key adapters
# every adapter yields {'stem', 'answer', 'options'}

def load_quizlet(path):
    raw = json.load(open(path, encoding='utf-8'))
    return raw['responses'][0]['models']['studiableItem']


def sides(item):
    return {s['label']: ' '.join(m.get('plainText', '') for m in s['media'])
            for s in item['cardSides']}


def split_qa(blob):
    """'Nr N. stem\nA. ...\nB. ...' -> (stem, options)"""
    stem = re.sub(r'^\s*Nr\.?\s*\d+\.\s*', '', re.split(r'\n\s*A[.)]', blob)[0]).strip()
    options = [{'letter': m.group(1), 'text': m.group(2).strip()}
               for m in re.finditer(r'(?m)^\s*([A-E])[.)]\s*(.+)$', blob)]
    return stem, options


def src_quizlet_qa(path):
    """word = question+options, definition = the correct answer's text."""
    out = []
    for it in load_quizlet(path):
        s = sides(it)
        w, d = s.get('word', ''), s.get('definition', '')
        if not w.strip() or not d.strip():
            continue
        stem, options = split_qa(w)
        if stem:
            out.append({'stem': stem, 'options': options,
                        'answer': re.sub(r'^\s*[A-E]\s*[.)]?\s*', '', d.strip())})
    return out


def src_quizlet_reversed(path):
    """word = bare answer letter, definition = question+options."""
    out = []
    for it in load_quizlet(path):
        s = sides(it)
        letter, blob = s.get('word', '').strip(), s.get('definition', '')
        m = re.fullmatch(r'\s*([A-E])\s*\.?\s*', letter)
        if not m or not blob.strip():
            continue
        stem, options = split_qa(blob)
        hit = [o for o in options if o['letter'] == m.group(1)]
        if stem and hit:
            out.append({'stem': stem, 'options': options, 'answer': hit[0]['text']})
    return out


def src_feniks(path):
    raw = json.load(open(path, encoding='utf-8'))
    out = []
    for rec in raw.values():
        opts = rec.get('opts') or {}
        ans = rec.get('ans')
        if not ans or ans not in opts:
            continue
        out.append({'stem': rec.get('q', '').strip(),
                    'options': [{'letter': L, 'text': t} for L, t in sorted(opts.items())],
                    'answer': opts[ans]})
    return out


def src_pdf_bold(path, edition=None):
    out = []
    for q in parse_pdf(path, read_key=True):
        if not q['correct']:
            continue
        out.append({'stem': q['stem'], 'options': q['options'],
                    'edition': edition,
                    'answer': next(o['text'] for o in q['options']
                                   if o['letter'] == q['correct'])})
    return out


# ------------------------------------------------------------------ matching

class Index:
    """Question lookup scored on stem AND options.

    Stems alone are not enough: several questions share the stem 'Wskaż
    fałszywe stwierdzenie:' verbatim, and others differ only in the victim's
    age, so options carry most of the discriminating signal.
    """

    STEM_W, OPTS_W = 0.45, 0.55

    def __init__(self, entries):
        self.entries = entries
        self.stems = [norm(e['stem'])[:200] for e in entries]
        self.opts = [norm(' '.join(o['text'] for o in e['options']))[:400]
                     for e in entries]
        self.tok = [toks(e['stem'] + ' ' + ' '.join(o['text'] for o in e['options']))
                    for e in entries]

    # some decks store only the stem on the card front; with no options to
    # weigh, a combined score can never clear the normal floor, so those
    # entries are scored on the stem alone against a stricter bar
    STEM_ONLY_FLOOR = 0.90

    def find(self, stem, options, floor=0.78, margin=0.03):
        ns = norm(stem)[:200]
        no = norm(' '.join(o['text'] for o in options))[:400]
        nt = toks(stem + ' ' + ' '.join(o['text'] for o in options))

        scored = []
        for i, e in enumerate(self.entries):
            t = self.tok[i]
            if not t or len(nt & t) / max(len(nt | t), 1) < 0.20:
                continue
            ss = sim(ns, self.stems[i])
            if self.opts[i]:
                scored.append((self.STEM_W * ss + self.OPTS_W * sim(no, self.opts[i]),
                               ss, i, False))
            else:
                scored.append((ss, ss, i, True))
        if not scored:
            return None
        scored.sort(reverse=True)
        top = scored[0]
        bar = max(floor, self.STEM_ONLY_FLOOR) if top[3] else floor
        if top[0] < bar or top[1] < 0.50:
            return None
        # Ambiguous between near-identical questions. That only matters if the
        # candidates disagree about the answer: merging editions of one key
        # leaves entries differing by a trailing full stop, and abstaining on
        # those threw away real coverage (41 questions, when the three Quizlet
        # decks were merged) for no gain. Where the tied entries assert
        # different things — the near-duplicates that differ only by the
        # victim's age or a dosage — they still disagree here, and it still
        # abstains.
        best = self.entries[top[2]]
        for other in scored[1:]:
            if top[0] - other[0] >= margin:
                break
            rival = self.entries[other[2]]
            if 'answer' not in best or 'answer' not in rival:
                return None
            if not same_answer(best['answer'], best['options'],
                               rival['answer'], rival['options']):
                return None
        return best


def pdf_date(path):
    try:
        return str(PdfReader(str(path)).metadata.get('/CreationDate', ''))
    except Exception:
        return ''


def merge_keys(lists):
    """Concatenate keyed entries from editions of the same document, dropping
    questions already covered. Earlier lists win, so pass newest first.

    Text similarity alone cannot decide this: 'wartość oddechu u osoby
    dorosłej' and '...u niemowląt' score 0.88, so a similarity-only rule
    silently discards one of them. A true duplicate must also agree on the
    answer, which those two do not (10-20/min vs 25-50/min).
    """
    out = []
    for lst in lists:
        idx = Index(list(out)) if out else None   # snapshot: out grows below
        for e in lst:
            if idx:
                hit = idx.find(e['stem'], e['options'], floor=0.85, margin=0.0)
                if hit and same_answer(e['answer'], e['options'],
                                       hit['answer'], hit['options']):
                    continue
            out.append(e)
    return out


def vote_letter(entry, cem_options):
    """Which CEM option does this source's answer correspond to?

    Takes the BEST match, not the first: numeric ranges read as near-identical
    text ('80-100 razy/minutę' vs '100-120 razy/minutę' scores 0.84), so a
    first-match-wins scan silently picks the wrong option. Where two options
    are both plausible and similarly close, abstain rather than guess.
    """
    src_opts = entry['options'] or cem_options
    na = norm(entry['answer'])
    matches = []
    for o in cem_options:
        if same_answer(o['text'], cem_options, entry['answer'], src_opts):
            no = norm(o['text'])
            matches.append((sim(no, na), o['letter'], no == na))
    if not matches:
        return None
    # a single exact string match is decisive; two long options differing only
    # in a flow rate still score 0.98, so similarity alone cannot settle it
    exact = [m for m in matches if m[2]]
    if len(exact) == 1:
        return exact[0][1]
    matches.sort(reverse=True)
    if len(matches) == 1 or matches[0][0] - matches[1][0] >= 0.05:
        return matches[0][1]
    return None


# ------------------------------------------------------------------- the lock

def digest(questions):
    """Fingerprint of the question base: every id, stem, option letter and
    option text, in order. Any drift in the wording changes it.

    The answer key is stamped with this, and the page refuses to pair a key
    with a base it was not built against — so questions cannot quietly move
    underneath an answer that was checked by hand.
    """
    h = hashlib.sha256()
    for q in sorted(questions, key=lambda q: q['id']):
        h.update(f"{q['id']}\x1f".encode())
        h.update(unicodedata.normalize('NFC', q['stem']).encode() + b'\x1f')
        for o in q['options']:
            h.update(o['letter'].encode() + b'\x1e')
            h.update(unicodedata.normalize('NFC', o['text']).encode() + b'\x1f')
        h.update(b'\x1d')
    return h.hexdigest()


def load_js(path, var):
    """Read one of our own `window.X = {...};` data files back."""
    src = path.read_text(encoding='utf-8')
    marker = 'window.' + var + ' ='
    if marker not in src:
        raise SystemExit(f'{path.name}: expected `{marker}`')
    return json.loads(src.split(marker, 1)[1].rstrip().rstrip(';'))


def write_js(path, var, payload):
    path.parent.mkdir(exist_ok=True)
    path.write_text('window.' + var + ' = '
                    + json.dumps(payload, ensure_ascii=False, indent=1) + ';\n',
                    encoding='utf-8')


def load_questions():
    """The locked base. Everything downstream reads questions from here, never
    from the PDF — that is what 'locked' means."""
    if not QUESTIONS_JS.exists():
        raise SystemExit('kpp/questions.js is missing — run tools/lock-questions.py')
    data = load_js(QUESTIONS_JS, 'KPP_QUESTIONS')
    have = digest(data['questions'])
    if have != data['meta']['digest']:
        raise SystemExit(
            'kpp/questions.js has been edited: its contents no longer match its '
            f'own digest\n  stored     {data["meta"]["digest"]}\n  recomputed {have}')
    return data
