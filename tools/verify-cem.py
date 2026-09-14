"""Independent check: does the locked base quote the CEM bank verbatim?

This deliberately does NOT reuse anything from tools/kppcommon.py. That module
reads the PDF with pypdf and a character-level bold tracker; this one reads it
with pdfplumber (pdfminer.six engine) and segments the text itself. Two
engines, two parsers — a bug shared by both is far less likely than a bug in
either.

What is checked:
  - kpp/questions.js still matches its own digest (nobody edited it by hand)
  - the same set of question numbers as the PDF
  - stem text, character for character
  - every option letter and its text, character for character
  - kpp/answers.js, if present, keys the same base and points at real options

CEM publishes no answer key, so whether an answer is RIGHT cannot be checked
here. Only the questions and the wording of the options can.

Usage:  python tools/verify-cem.py [--verbose]
"""
import sys, re, json, pathlib, hashlib, unicodedata

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pdfplumber

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / 'docs' / 'KPP2026-CEM-official.pdf'
JS = ROOT / 'kpp' / 'questions.js'
ANSWERS = ROOT / 'kpp' / 'answers.js'

VERBOSE = '--verbose' in sys.argv

HEADER = 'PYTANIA DO EGZAMINU'
NR_RE = re.compile(r'Nr\s*(\d+)\.\s')
# Options cannot be found on line starts: short ones are typeset side by side
# ('A. 5,4. B. 3,2,4,1. C. 3,4,5.'), and long ones wrap. So the block is
# flattened first and the markers found inside it, in order.
OPT_RE = re.compile(r'(?<![^\s])([A-E])\.\s')


def pdf_questions():
    """Segment the official PDF: 'Nr N.' opens a question, then the markers
    'A.'..'E.' in sequence cut its options out of the flattened block."""
    if not PDF.exists():
        raise SystemExit(
            f'missing {PDF.relative_to(ROOT)} — the official CEM bank.\n'
            'docs/ is not in the repository (third-party material). Download it\n'
            'from https://www.cem.edu.pl/pliki/KPP2026.pdf, or run\n'
            '  python tools/fetch-sources.py\n'
            'which fetches what it can and names the rest.')
    chunks = []
    with pdfplumber.open(PDF) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or '').split('\n'):
                line = line.strip()
                if line and not line.startswith(HEADER):
                    chunks.append(line)
    text = ' '.join(chunks)

    starts = [(int(m.group(1)), m.start(), m.end()) for m in NR_RE.finditer(text)]
    out = []
    for i, (nr, s, e) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        block = text[e:end]

        marks, expect = [], 'A'
        for m in OPT_RE.finditer(block):
            if m.group(1) != expect:
                continue
            marks.append((m.group(1), m.start(), m.end()))
            expect = chr(ord(expect) + 1)
            if expect > 'E':
                break

        options = []
        for j, (letter, ms, me) in enumerate(marks):
            stop = marks[j + 1][1] if j + 1 < len(marks) else len(block)
            options.append({'letter': letter,
                            'text': ' '.join(block[me:stop].split())})
        stem_end = marks[0][1] if marks else len(block)
        out.append({'nr': nr, 'stem': ' '.join(block[:stem_end].split()),
                    'options': options})
    return out


def read_js(path, var):
    src = path.read_text(encoding='utf-8')
    marker = 'window.' + var + ' ='
    if marker not in src:
        raise SystemExit(f'{path.name}: expected `{marker}`')
    return json.loads(src.split(marker, 1)[1].rstrip().rstrip(';'))


def js_questions():
    return read_js(JS, 'KPP_QUESTIONS')


def strip_tail(s):
    """The bank ends most options with a full stop and some without one; the
    build drops it. Compare on the text, not on that punctuation."""
    return s.rstrip().rstrip('.').rstrip()


def canonical(s):
    """Same characters, differently encoded, are not a difference: the two PDF
    engines disagree on non-breaking spaces, soft hyphens and the shape of
    quotes and dashes."""
    s = unicodedata.normalize('NFC', s)
    s = s.replace(' ', ' ').replace('­', '')
    s = re.sub(r'[‘’‚′]', "'", s)
    s = re.sub(r'[“”„″]', '"', s)
    s = re.sub(r'[‐‑‒–—−]', '-', s)
    # Subscripts are typeset on their own baseline, so pdfplumber reports the
    # '2' of CO2 as a separate line and flattening leaves 'CO . 2'. Put the
    # digit back where it belongs rather than call it a difference.
    s = re.sub(r'(?<=[A-Za-z]) \. (\d)(?![\d\w])', r'\1 .', s)
    return ' '.join(s.split()).rstrip('.').rstrip()


def show(label, a, b):
    print(f'      {label}')
    print(f'        PDF : {a}')
    print(f'        JS  : {b}')
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            print(f'        first difference at {i}: '
                  f'{x!r} (U+{ord(x):04X}) vs {y!r} (U+{ord(y):04X})')
            print(f'        ...{a[max(0,i-25):i+25]}...')
            print(f'        ...{b[max(0,i-25):i+25]}...')
            break
    else:
        print(f'        lengths differ: {len(a)} vs {len(b)}')


pdf = pdf_questions()
data = js_questions()
js = data['questions']
key = read_js(ANSWERS, 'KPP_ANSWERS') if ANSWERS.exists() else None

print(f'PDF  (pdfplumber) : {len(pdf)} questions, '
      f'numbers {min(q["nr"] for q in pdf)}-{max(q["nr"] for q in pdf)}')
print(f'questions.js      : {len(js)} questions, '
      f'numbers {min(q["id"] for q in js)}-{max(q["id"] for q in js)}, '
      f'locked {data["meta"]["locked"]}')

# The lock is only worth something if the file still is what it says it is.
# Recomputed with this script's own hashing, not the build's.
h = hashlib.sha256()
for q in sorted(js, key=lambda q: q['id']):
    h.update(f'{q["id"]}\x1f'.encode())
    h.update(unicodedata.normalize('NFC', q['stem']).encode() + b'\x1f')
    for o in q['options']:
        h.update(o['letter'].encode() + b'\x1e')
        h.update(unicodedata.normalize('NFC', o['text']).encode() + b'\x1f')
    h.update(b'\x1d')
lock_ok = h.hexdigest() == data['meta']['digest']
print(f'digest            : {data["meta"]["digest"][:16]}… '
      + ('matches the file contents' if lock_ok
         else f'!! MISMATCH, recomputed {h.hexdigest()[:16]}…'))

key_ok = True
if key:
    key_ok = key['meta']['questions_digest'] == data['meta']['digest']
    print(f'answers.js        : {len(key["answers"])} answers, built '
          f'{key["meta"]["built"]}, '
          + ('keyed to this base' if key_ok
             else '!! built against a DIFFERENT question base'))

by_nr = {q['nr']: q for q in pdf}
if len(by_nr) != len(pdf):
    seen = set()
    dupes = sorted({q['nr'] for q in pdf if q['nr'] in seen or seen.add(q['nr'])})
    print(f'!! duplicate numbers in the PDF: {dupes}')

pdf_nrs, js_nrs = set(by_nr), {q['id'] for q in js}
missing = sorted(pdf_nrs - js_nrs)
extra = sorted(js_nrs - pdf_nrs)
gaps = sorted(set(range(min(pdf_nrs), max(pdf_nrs) + 1)) - pdf_nrs)
print(f'gaps in CEM numbering : {gaps or "none"}')
if missing:
    print(f'!! in the PDF but NOT in questions.js: {missing}')
if extra:
    print(f'!! in questions.js but NOT in the PDF: {extra}')

bad_stem = bad_opts = bad_key = 0
print()
for nr in sorted(pdf_nrs & js_nrs):
    p, j = by_nr[nr], next(q for q in js if q['id'] == nr)
    problems = []

    ps, jss = canonical(strip_tail(p['stem'])), canonical(strip_tail(j['stem']))
    if ps != jss:
        problems.append(('stem', ps, jss))
        bad_stem += 1

    po = [(o['letter'], canonical(strip_tail(o['text']))) for o in p['options']]
    jo = [(o['letter'], canonical(strip_tail(o['text']))) for o in j['options']]
    if len(po) != len(jo):
        problems.append(('option count', str([l for l, _ in po]),
                         str([l for l, _ in jo])))
        bad_opts += 1
    else:
        diffs = [(a, b) for a, b in zip(po, jo) if a != b]
        if diffs:
            bad_opts += 1
            for (la, ta), (lb, tb) in diffs:
                problems.append((f'option {la}/{lb}', ta, tb))

    a = (key['answers'].get(str(nr)) if key else None) or {}
    if a.get('correct') and a['correct'] not in [l for l, _ in jo]:
        problems.append(('keyed letter absent from options',
                         a['correct'], str([l for l, _ in jo])))
        bad_key += 1

    if problems:
        print(f'  Nr {nr}')
        for label, a, b in problems:
            show(label, a, b)
    elif VERBOSE:
        print(f'  Nr {nr}  ok ({len(jo)} options)')

print()
print(f'stems differing          : {bad_stem}')
print(f'option sets differing    : {bad_opts}')
print(f'keys pointing nowhere    : {bad_key}')
ok = (lock_ok and key_ok and not (missing or extra or bad_stem or bad_opts or bad_key))
print('RESULT:', 'the locked base quotes the CEM bank verbatim'
      if ok else 'DIFFERENCES FOUND — see above')
sys.exit(0 if ok else 1)
