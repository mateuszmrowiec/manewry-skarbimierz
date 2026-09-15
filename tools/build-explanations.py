"""Turn the review pass into kpp/explanations.js.

kpp/review-log.jsonl is the record of going through the bank question by
question: a verdict for each, and where one was written, an explanation of the
correct answer. This lifts those explanations out for the page to show.

They are kept in their own file on purpose. Rebuilding the answer key is a
mechanical thing that happens whenever a source changes; the explanations are
written by hand and must not be at the mercy of it. Same reasoning as the
question lock.

The log is append-only and a later record for a number supersedes an earlier
one, so an explanation can be corrected by simply writing it again.

Two fields in the log and only one of them belongs here:
  why      explains the correct answer — meant for whoever is learning
  comment  the reviewer's own remark about the question — NOT shown

Usage:  python tools/build-explanations.py
"""
import json, pathlib, datetime

from kppcommon import ROOT, load_questions, write_js

LOG = ROOT / 'kpp' / 'review-log.jsonl'
OUT = ROOT / 'kpp' / 'explanations.js'

if not LOG.exists():
    raise SystemExit(f'no {LOG.relative_to(ROOT)} yet — nothing to build')

base = load_questions()
known = {q['id'] for q in base['questions']}

rows, meta = {}, {}
for line in LOG.read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    if 'meta' in rec:
        meta = rec['meta']
        continue
    rows[rec['nr']] = rec          # last record for a number wins

if meta.get('questions_digest') and meta['questions_digest'] != base['meta']['digest']:
    raise SystemExit('the review log was written against a different question '
                     'base than the one locked now — check before building')

explain, orphan = {}, []
for nr, rec in sorted(rows.items()):
    why = (rec.get('why') or '').strip()
    if not why:
        continue
    if nr not in known:
        orphan.append(nr)          # e.g. a withdrawn question
        continue
    explain[str(nr)] = why

done = sorted(rows)
print(f'review log     : {len(rows)} questions judged, '
      f'{len(explain)} with an explanation')
print(f'covered so far : {done[0]}-{done[-1]}' if done else 'nothing yet')
missing = sorted(known - set(rows))
print(f'still to review: {len(missing)}' +
      (f', next is Nr {missing[0]}' if missing else ' — the whole bank is done'))
if orphan:
    print(f'explanations for questions outside the locked base: {orphan}')

write_js(OUT, 'KPP_EXPLAIN', {
    'meta': {
        'note': 'Wyjaśnienia własne, nie pochodzą z CEM.',
        'questions_digest': base['meta']['digest'],
        'built': datetime.date.today().isoformat(),
        'count': len(explain),
        'reviewed': len(rows),
    },
    'explain': explain,
})
print(f'wrote {OUT.relative_to(ROOT)}')
