"""Build kpp/answers.js — the answer key, and nothing else.

CEM publishes the questions but deliberately publishes no answer key, so every
key in circulation is someone's reconstruction. This script matches each source
to the LOCKED question base and has them vote, so a question backed by several
independent keys can be told apart from one resting on a single guess.

It never reads question text from a PDF. Questions come from kpp/questions.js,
which tools/lock-questions.py froze, and the key is stamped with that base's
digest so the two cannot drift apart unnoticed.

Hand-set answers in kpp/answers-manual.json win over the vote — that file is
where a question settled with an instructor gets recorded, and re-running this
script will not undo it. Format:

    { "44": { "correct": "C", "note": "why, and who decided" } }

Usage:  python tools/build-answers.py
"""
import sys, re, json, glob, pathlib, datetime, collections

from kppcommon import (DOCS, ANSWERS_JS, ROOT, Index, load_questions, load_js, write_js,
                       vote_letter, merge_keys, pdf_date, src_pdf_bold,
                       src_quizlet_qa, src_quizlet_reversed, src_feniks)

MANUAL = ROOT / 'kpp' / 'answers-manual.json'

# Both bold-answer PDFs (drogaratownika 2024, dlaratownikaimedyka 2025) share an
# author in their metadata and agree on 220/220 shared questions, so they are ONE
# source. Counting them separately would manufacture corroboration.
# Labelled by edition, not by author: naming a private individual serves no one.
PDF_SOURCE = 'PDF 2024/2025'

# Shown as links in the page footer, so the credits cannot drift from the
# sources the key was actually built from.
PORTALS = [
    ('drogaratownika.pl',
     'https://drogaratownika.pl/baza-plikow/cmeitwl4b0015p60hyl5mz5cd'),
    ('dlaratownikaimedyka.pl',
     'https://dlaratownikaimedyka.pl/wp-content/uploads/2025/06/'
     'kpp-pytania-i-odpowiedzi-2025.pdf'),
    ('quizlet 710735124', 'https://quizlet.com/pl/710735124'),
    ('quizlet 595014549', 'https://quizlet.com/pl/595014549'),
    ('quizlet 804902455', 'https://quizlet.com/pl/804902455'),
    ('feniks.care', 'https://feniks.care/quiz_kpp.php?tryb=nauka&id=1'),
]

base = load_questions()
cem = base['questions']
print(f'locked base  : {len(cem)} questions, digest {base["meta"]["digest"][:16]}…\n')

key_pdfs = sorted((p for p in glob.glob(str(DOCS / '*.pdf'))
                   if 'KPP2026-CEM-official' not in p),
                  key=pdf_date, reverse=True)          # newest edition wins
SOURCES = []
if key_pdfs:
    editions = [(p, re.search(r'D:(\d{4})', pdf_date(p)).group(1)) for p in key_pdfs]
    print('  bold-answer PDFs: ' +
          ', '.join(f'{pathlib.Path(p).name} ({e})' for p, e in editions))
    SOURCES.append((PDF_SOURCE,
                    merge_keys([src_pdf_bold(p, e) for p, e in editions])))
for name, fn, fname in [
    ('quizlet-710735124', src_quizlet_qa, 'quizlet-710735124.json'),
    ('quizlet-595014549', src_quizlet_qa, 'quizlet-595014549.json'),
    ('quizlet-804902455', src_quizlet_reversed, 'quizlet-804902455.json'),
    ('feniks.care', src_feniks, 'feniks-care.json'),
]:
    if (DOCS / fname).exists():
        SOURCES.append((name, fn(DOCS / fname)))

indexes = []
for name, entries in SOURCES:
    print(f'  {name:<20} {len(entries):>4} keyed entries')
    indexes.append((name, Index(entries)))

# A fresh clone has no docs/ — it is third-party material and stays out of the
# repository. Rebuilding then would quietly overwrite a good key with a file in
# which every question is unkeyed, so refuse before writing rather than after.
if not SOURCES:
    raise SystemExit(
        '\nno answer-key sources found in docs/ — nothing to build from.\n'
        'Run  python tools/fetch-sources.py  first; it fetches what it can and\n'
        'names the PDFs you have to download by hand.')

if ANSWERS_JS.exists() and '--force' not in sys.argv:
    had = load_js(ANSWERS_JS, 'KPP_ANSWERS')['meta'].get('key_sources', [])
    lost = [s for s in had if s not in [n for n, _ in SOURCES]]
    if lost:
        raise SystemExit(
            f'\nthe existing key was built from {len(had)} sources, '
            f'of which these are missing now:\n  ' + '\n  '.join(lost) +
            '\nRebuilding would produce a WEAKER key than the one on disk.\n'
            'Restore the missing files in docs/ (tools/fetch-sources.py), or\n'
            'pass --force if you really mean to rebuild with fewer sources.')

manual = {}
if MANUAL.exists():
    manual = {int(k): v for k, v in json.load(open(MANUAL, encoding='utf-8')).items()}
    print(f'\n  answers-manual.json  {len(manual)} hand-set: {sorted(manual)}')
print()

answers = {}
stats = collections.Counter()
vote_hist = collections.Counter()

for q in cem:
    votes = collections.defaultdict(list)
    pdf_edition = None
    for name, idx in indexes:
        hit = idx.find(q['stem'], q['options'])
        if not hit:
            continue
        letter = vote_letter(hit, q['options'])
        if letter:
            votes[letter].append(name)
            if name == PDF_SOURCE:
                pdf_edition = hit.get('edition')

    tally = {L: len(v) for L, v in votes.items()}
    n_src = sum(tally.values())
    vote_hist[n_src] += 1

    if not tally:
        correct, status = None, 'unkeyed'
    else:
        top = max(tally.values())
        leaders = sorted(L for L, c in tally.items() if c == top)
        # Ties break toward the PDF key. Which edition cast that vote is
        # decided upstream: merge_keys() is fed newest-first, so the 2025
        # edition answers wherever it covers the question and 2024 only fills
        # its gaps. pdf_edition records which one it was, and is carried into
        # the output for the questions this rule had to settle.
        anchor = next((L for L in leaders if PDF_SOURCE in votes[L]), None)
        correct = anchor or leaders[0]
        if len(tally) == 1:
            status = 'verified' if n_src >= 2 else 'single-source'
        elif len(leaders) == 1:
            status = 'majority'
        else:
            status = 'conflict'

    rec = {'correct': correct, 'status': status,
           'votes': {L: sorted(v) for L, v in sorted(votes.items())}}
    if status in ('majority', 'conflict') and pdf_edition:
        rec['pdf_edition'] = pdf_edition

    # A decision made with an instructor outranks the vote, and survives every
    # later rebuild. The vote is kept alongside it so the disagreement stays
    # visible instead of being quietly erased.
    m = manual.get(q['id'])
    if m:
        letters = [o['letter'] for o in q['options']]
        if m['correct'] not in letters:
            raise SystemExit(f'answers-manual.json: Nr {q["id"]} has no option '
                             f'{m["correct"]} (has {letters})')
        if m['correct'] != rec['correct']:
            print(f'  Nr {q["id"]}: hand-set {m["correct"]} '
                  f'overrides voted {rec["correct"]}')
        rec['voted'] = rec['correct']
        rec['correct'] = m['correct']
        rec['status'] = 'manual'
        rec['note'] = m.get('note', '')
        status = 'manual'

    stats[status] += 1
    answers[str(q['id'])] = rec

print('status:')
for k in ('verified', 'manual', 'majority', 'single-source', 'conflict', 'unkeyed'):
    if stats[k]:
        print(f'  {k:<14}: {stats[k]}')
print('\nsources agreeing per question:')
for n in sorted(vote_hist):
    print(f'  {n} source(s): {vote_hist[n]}')

needs_review = [int(i) for i, r in answers.items()
                if r['status'] in ('conflict', 'majority', 'unkeyed')]
needs_review.sort()
print(f'\nneeds human review ({len(needs_review)}): {needs_review}')

write_js(ANSWERS_JS, 'KPP_ANSWERS', {
    'meta': {
        # Pairs this key with the exact question base it was built against.
        'questions_digest': base['meta']['digest'],
        'key_sources': [n for n, _ in SOURCES],
        'portals': [{'label': l, 'url': u} for l, u in PORTALS],
        'built': datetime.date.today().isoformat(),
        'count': len(answers),
        'stats': dict(stats),
        'needs_review': needs_review,
        'manual': sorted(manual),
    },
    'answers': answers,
})
print(f'\nwrote {ANSWERS_JS.relative_to(ROOT)}')
