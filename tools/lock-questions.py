"""Freeze the CEM question base into kpp/questions.js.

This is the only tool allowed to write question text. It runs once per CEM
edition and then stays out of the way: the answer key is worked on separately,
against the frozen base, so an answer somebody checked by hand cannot end up
attached to a question whose wording has shifted underneath it.

Re-running it on the same PDF is a no-op. If the questions come out different
— a new CEM edition, or a parser change — it refuses and says what moved;
pass --force to accept the new base, and expect to re-check the key, because
kpp/answers.js will no longer match the digest.

Verify the result against the PDF with a second, independent reader:

    python tools/verify-cem.py

Usage:  python tools/lock-questions.py [--force]
"""
import sys, json, difflib, datetime

from kppcommon import (CEM_PDF, QUESTIONS_JS, parse_pdf, digest, load_js,
                       write_js)

FORCE = '--force' in sys.argv

if not CEM_PDF.exists():
    raise SystemExit(f'missing {CEM_PDF} — the official CEM bank')

parsed = parse_pdf(CEM_PDF, read_key=False)
questions = [{'id': q['nr'], 'stem': q['stem'], 'options': q['options']}
             for q in sorted(parsed, key=lambda q: q['nr'])]
fresh = digest(questions)

nums = [q['id'] for q in questions]
gaps = sorted(set(range(min(nums), max(nums) + 1)) - set(nums))
print(f'{CEM_PDF.name}: {len(questions)} questions, '
      f'numbers {min(nums)}-{max(nums)}, gaps {gaps or "none"}')
bad = [q['id'] for q in questions if len(q['options']) != 5]
if bad:
    print(f'!! questions without five options: {bad}')

try:
    old = load_js(QUESTIONS_JS, 'KPP_QUESTIONS') if QUESTIONS_JS.exists() else None
except SystemExit:
    # An older questions.js held questions and key together under KPP_DATA.
    # There is no lock to protect, so replacing it is not an overwrite.
    print('existing kpp/questions.js predates the lock — replacing it')
    old = None

if old:
    if old['meta']['digest'] == fresh:
        print('already locked, identical — nothing to do')
        raise SystemExit(0)

    print('\nthe question base would CHANGE:')
    was, now = {q['id']: q for q in old['questions']}, {q['id']: q for q in questions}
    for nr in sorted(set(was) - set(now)):
        print(f'  Nr {nr}: removed')
    for nr in sorted(set(now) - set(was)):
        print(f'  Nr {nr}: added')
    for nr in sorted(set(was) & set(now)):
        a = json.dumps(was[nr], ensure_ascii=False, sort_keys=True)
        b = json.dumps(now[nr], ensure_ascii=False, sort_keys=True)
        if a == b:
            continue
        print(f'  Nr {nr}: changed')
        for line in difflib.unified_diff(
                [was[nr]['stem']] + [o['letter'] + '. ' + o['text']
                                     for o in was[nr]['options']],
                [now[nr]['stem']] + [o['letter'] + '. ' + o['text']
                                     for o in now[nr]['options']],
                lineterm='', n=0):
            if line[:1] in '+-' and line[:3] not in ('---', '+++'):
                print('      ' + line)
    if not FORCE:
        raise SystemExit(
            '\nrefusing to overwrite a locked base. If this is intended '
            '(new CEM edition),\nre-run with --force — then rebuild and '
            're-check kpp/answers.js, which will\nno longer match the digest.')
    print('\n--force given: replacing the locked base')

write_js(QUESTIONS_JS, 'KPP_QUESTIONS', {
    'meta': {
        'source': 'Centrum Egzaminów Medycznych (CEM)',
        'url': 'https://www.cem.edu.pl/ppomoc.php',
        'version': 'KPP2026 / 2026-06-17',
        'file': CEM_PDF.name,
        'locked': datetime.date.today().isoformat(),
        'count': len(questions),
        'digest': fresh,
    },
    'questions': questions,
})
print(f'\nwrote {QUESTIONS_JS.relative_to(QUESTIONS_JS.parent.parent)}')
print(f'digest {fresh}')
