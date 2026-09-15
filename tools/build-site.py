"""Build the publishable test into kpp/index.html.

Only questions somebody has actually gone through by hand are published. The
review log is the gate: a question appears on the site when it has a verdict
in kpp/review-log.jsonl, and not before. Everything else — the rest of the
bank, the answers resting on nothing but a vote — stays on this machine.

The output is ONE self-contained file. The data is inlined rather than loaded
from questions.js / answers.js / explanations.js, so there is no way to publish
the full bank by accident: the unpublished questions are simply not in the file
that gets committed. It also means the page works opened from disk.

The page itself is kpp/review.html — the same file used for reviewing, so the
published test cannot drift from the one being checked.

Usage:  python tools/build-site.py [--all]

  --all   publish every question, reviewed or not. Only for when the whole
          bank has been checked; it is the thing this script exists to stop
          you doing by accident.
"""
import re, sys, json, pathlib, datetime

from kppcommon import ROOT, load_questions, load_js

SRC = ROOT / 'kpp' / 'review.html'
OUT = ROOT / 'kpp' / 'index.html'
LOG = ROOT / 'kpp' / 'review-log.jsonl'

PUBLISH_ALL = '--all' in sys.argv

base = load_questions()
answers = load_js(ROOT / 'kpp' / 'answers.js', 'KPP_ANSWERS')
explain = (load_js(ROOT / 'kpp' / 'explanations.js', 'KPP_EXPLAIN')
           if (ROOT / 'kpp' / 'explanations.js').exists() else {'explain': {}})
retired = (load_js(ROOT / 'kpp' / 'retired.js', 'KPP_RETIRED')
           if (ROOT / 'kpp' / 'retired.js').exists() else {'questions': []})

if answers['meta']['questions_digest'] != base['meta']['digest']:
    raise SystemExit('answers.js was built against a different question base')

# ---- which questions have been reviewed -----------------------------------
reviewed = set()
if LOG.exists():
    for line in LOG.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if 'nr' in rec:
            reviewed.add(rec['nr'])

ids = sorted(q['id'] for q in base['questions']
             if PUBLISH_ALL or q['id'] in reviewed)
if not ids:
    raise SystemExit('nothing reviewed yet — nothing to publish')

held = len(base['questions']) - len(ids)
print(f'reviewed      : {len(reviewed & {q["id"] for q in base["questions"]})}')
print(f'publishing    : {len(ids)} questions (Nr {ids[0]}-{ids[-1]})')
print(f'held back     : {held}')

pub_q = [q for q in base['questions'] if q['id'] in ids]
pub_a = {str(i): answers['answers'][str(i)] for i in ids}
pub_e = {k: v for k, v in explain['explain'].items() if int(k) in ids}
# a withdrawn question is shown only if it falls inside the published range,
# so the numbering has no unexplained hole
pub_r = [r for r in retired['questions'] if ids[0] <= r['id'] <= ids[-1]]
print(f'explanations  : {len(pub_e)}')
print(f'withdrawn shown: {[r["id"] for r in pub_r] or "none"}')

lede = (
  'Pytania pochodzą z oficjalnej bazy Centrum Egzaminów Medycznych. '
  'CEM nie publikuje odpowiedzi, więc klucz jest nieoficjalny — te '
  f'{len(ids)} pytań przeszliśmy ręcznie, jedno po drugim, i tylko one są tutaj. '
  'Reszta bazy dojdzie, gdy zostanie sprawdzona. Jeśli widzisz błędną '
  'odpowiedź, kliknij przy niej „Klucz jest tu błędny”.'
)

payload = {
    'KPP_QUESTIONS': {'meta': dict(base['meta'], count=len(pub_q),
                                   lede=lede),
                      'questions': pub_q},
    'KPP_ANSWERS': {'meta': dict(answers['meta'], count=len(pub_a),
                                 needs_review=[n for n in answers['meta']['needs_review']
                                               if n in ids]),
                    'answers': pub_a},
    'KPP_EXPLAIN': {'meta': dict(explain.get('meta', {}), count=len(pub_e)),
                    'explain': pub_e},
    'KPP_RETIRED': {'meta': retired.get('meta', {}), 'questions': pub_r},
}

# ---- rewrite the page ------------------------------------------------------
html = SRC.read_text(encoding='utf-8')


def once(pattern, repl, text, what, flags=0):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'build-site: could not find {what} in review.html — '
                         'the page changed shape, fix this script rather than '
                         'publishing something unchecked')
    return new


data = '<script>\n' + '\n'.join(
    f'window.{k} = ' + json.dumps(v, ensure_ascii=False, separators=(',', ':')) + ';'
    for k, v in payload.items()) + '\n</script>'

html = once(r'<!-- optional: questions CEM has withdrawn.*?<script src="explanations\.js"></script>',
            lambda m: data, html, 'the data script tags', re.S)
html = once(r'<script src="questions\.js"></script>\s*<script src="answers\.js"></script>\s*',
            '', html, 'the questions/answers script tags')
html = once(r'<title>.*?</title>', '<title>Test KPP — Manewry SAR Skarbimierz</title>',
            html, 'the title')
html = once(r'<h1>.*?</h1>', '<h1>Test — kwalifikowana pierwsza pomoc</h1>',
            html, 'the heading', re.S)
html = once(r'<p class="lede">.*?</p>',
            '<p class="lede" id="lede"></p>', html, 'the lede', re.S)
# the closing date guarded an unverified draft; this is checked material
html = once(r"CLOSES: '[^']*'", "CLOSES: ''", html, 'the CLOSES setting')

OUT.write_text(html, encoding='utf-8')
print(f'\nwrote {OUT.relative_to(ROOT)}  ({len(html) // 1024} KB, self-contained)')
