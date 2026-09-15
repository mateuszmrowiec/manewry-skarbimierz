"""Record the questions CEM has withdrawn, into kpp/retired.js.

CEM's KPP2026 bank numbers 1-280 but holds 278 questions: 13 and 218 are
simply absent. They are not a parsing failure — the official file skips them —
and they are not ours to invent, so they cannot go in kpp/questions.js, which
is locked to quote that file exactly.

They are still worth keeping. Every circulating key still carries them, anyone
studying from an older set will meet them, and knowing a question was dropped
is more useful than finding a hole where it used to be.

A number counts as withdrawn when an older edition of the bank has it and the
current CEM file does not. The text and the old key come from the newest
edition that still carried it.

Usage:  python tools/lock-retired.py
"""
import re, json, glob, pathlib, datetime

from kppcommon import (CEM_PDF, DOCS, ROOT, parse_pdf, pdf_date, write_js)

RETIRED_JS = ROOT / 'kpp' / 'retired.js'

if not CEM_PDF.exists():
    raise SystemExit(f'missing {CEM_PDF} — the official CEM bank')

current = {q['nr'] for q in parse_pdf(CEM_PDF, read_key=False)}
print(f'{CEM_PDF.name}: {len(current)} questions')

# Newest edition first, so the text and key come from the last file that had it.
editions = sorted((p for p in glob.glob(str(DOCS / '*.pdf'))
                   if 'KPP2026-CEM-official' not in p),
                  key=pdf_date, reverse=True)
if not editions:
    raise SystemExit('no older editions in docs/ to compare against — '
                     'run tools/fetch-sources.py and read its notes')

seen, found = {}, {}
for path in editions:
    year = (re.search(r'D:(\d{4})', pdf_date(path)) or [None, '?'])[1]
    qs = parse_pdf(path, read_key=True)
    print(f'  {pathlib.Path(path).name}: {len(qs)} questions ({year})')
    for q in qs:
        seen.setdefault(q['nr'], []).append(year)
        if q['nr'] not in current and q['nr'] not in found and q['correct']:
            found[q['nr']] = (q, year)

gone = sorted(found)
print(f'\nwithdrawn from the current bank: {gone or "none"}')

questions = []
for nr in gone:
    q, year = found[nr]
    questions.append({
        'id': nr,
        'stem': q['stem'],
        'options': q['options'],
        # The key here is the OLD key from the circulating reconstructions.
        # CEM never published one for these either.
        'correct': q['correct'],
        'last_edition': year,
        'seen_in': sorted(set(seen.get(nr, []))),
    })
    print(f'  Nr {nr}: key {q["correct"]}, last seen in the {year} edition')

write_js(RETIRED_JS, 'KPP_RETIRED', {
    'meta': {
        'note': 'Pytania obecne w starszych wydaniach bazy, nieobecne w KPP2026.',
        'dropped_from': 'KPP2026 / 2026-06-17',
        'built': datetime.date.today().isoformat(),
        'count': len(questions),
    },
    'questions': questions,
})
print(f'\nwrote {RETIRED_JS.relative_to(ROOT)}')
