"""Re-fetch the answer-key sources into docs/.

docs/ is not in the repository — it is third-party material we don't
redistribute — so on a fresh clone this is how the key sources come back.

What it can fetch:
  feniks.care          280 quiz pages, one request each
  quizlet 710735124    via Quizlet's own web API
  quizlet 595014549
  quizlet 804902455

What it cannot: the two bold-answer PDFs and the official CEM bank. Those are
downloads a person has to make, and the links are in SOURCES.md:

  docs/KPP2026-CEM-official.pdf       https://www.cem.edu.pl/pliki/KPP2026.pdf
  docs/dlaratownikaimedyka-2025.pdf   direct link, see SOURCES.md
  docs/5e6782f4-….pdf                 drogaratownika.pl, behind a file listing

Existing files are left alone unless --force is given, so a re-run after a
partial fetch only asks for what is missing.

Usage:  python tools/fetch-sources.py [--force] [--only feniks|quizlet]
"""
import sys, re, json, time, html, pathlib, urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'

FORCE = '--force' in sys.argv
ONLY = None
if '--only' in sys.argv:
    ONLY = sys.argv[sys.argv.index('--only') + 1]

UA = {'User-Agent': 'Mozilla/5.0 (KPP study-key cross-check; one pass, rate limited)'}
# Deliberately unhurried. These are small volunteer-run sites and a study
# project has no business hammering them.
DELAY = 0.6

QUIZLET = ['710735124', '595014549', '804902455']
QUIZLET_API = ('https://quizlet.com/webapi/3.4/studiable-item-documents'
               '?filters%5BstudiableContainerId%5D={}'
               '&filters%5BstudiableContainerType%5D=1&perPage=500&page=1')
FENIKS = 'https://feniks.care/quiz_kpp.php?tryb=nauka&id={}'


def get(url, timeout=45):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


def want(path):
    if path.exists() and not FORCE:
        print(f'  {path.name:<28} already there, skipping (--force to refetch)')
        return False
    return True


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', s))).strip()


def fetch_feniks():
    out = DOCS / 'feniks-care.json'
    if not want(out):
        return
    print(f'  feniks.care: 280 pages at {DELAY}s apart, about '
          f'{int(280 * DELAY / 60) + 1} min')
    data, failed = {}, []
    for i in range(1, 281):
        try:
            h = get(FENIKS.format(i), timeout=30)
        except Exception as e:
            failed.append(i)
            time.sleep(1)
            continue
        ans = re.search(r"const poprawna = '([A-E])'", h)
        uz = re.search(r'<b>Uzasadnienie:</b>(.*?)</div>', h, re.S)
        qm = re.search(r'(Nr\s*\d+\.?.*?)<form', h, re.S)
        q = None
        if qm:
            t = clean(qm.group(1))
            q = t[-300:] if len(t) > 300 else t
        opts = dict(re.findall(r"value='([A-E])'[^>]*>\s*<b>[A-E]\)</b>(.*?)</label>",
                               h, re.S))
        data[str(i)] = {'ans': ans.group(1) if ans else None,
                        'q': q,
                        'opts': {k: clean(v) for k, v in opts.items()},
                        'uz': clean(uz.group(1)) if uz else None}
        if i % 40 == 0:
            print(f'    {i}/280')
        time.sleep(DELAY)
    keyed = sum(1 for v in data.values() if v['ans'])
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'  wrote {out.name}: {len(data)} pages, {keyed} with an answer'
          + (f', failed {failed}' if failed else ''))


def fetch_quizlet():
    for set_id in QUIZLET:
        out = DOCS / f'quizlet-{set_id}.json'
        if not want(out):
            continue
        try:
            raw = get(QUIZLET_API.format(set_id))
        except Exception as e:
            print(f'  quizlet {set_id}: FAILED — {e}')
            continue
        try:
            n = len(json.loads(raw)['responses'][0]['models']['studiableItem'])
        except Exception:
            print(f'  quizlet {set_id}: response was not the expected shape — '
                  'the API may have moved; fetch the set by hand')
            continue
        out.write_text(raw, encoding='utf-8')
        print(f'  wrote {out.name}: {n} cards')
        time.sleep(DELAY)


DOCS.mkdir(exist_ok=True)
print(f'docs/ -> {DOCS}')

if ONLY in (None, 'quizlet'):
    fetch_quizlet()
if ONLY in (None, 'feniks'):
    fetch_feniks()

missing = [n for n in ('KPP2026-CEM-official.pdf', 'dlaratownikaimedyka-2025.pdf')
           if not (DOCS / n).exists()]
if not any(p.suffix == '.pdf' and 'KPP2026' not in p.name
           and 'dlaratownika' not in p.name for p in DOCS.glob('*.pdf')):
    missing.append('the drogaratownika.pl 2024 PDF')
if missing:
    print('\nstill needed, by hand (see the links at the top of this file):')
    for m in missing:
        print(f'  {m}')
