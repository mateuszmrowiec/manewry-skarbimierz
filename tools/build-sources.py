"""Turn kpp/sources.json into kpp/sources.js for the page to show.

These are the sources an answer is checked against — regulations, guidelines —
as distinct from the answer keys we harvested. The keys say what somebody
believed the answer was; these say what is actually required or taught. The
page keeps them apart for that reason.

Editing the list means editing kpp/sources.json. Nothing here invents a URL:
--check fetches every one and reports what came back, so a link that has
rotted shows up here rather than in front of a reader.

Usage:  python tools/build-sources.py [--check]
"""
import os, sys, json, shutil, pathlib, datetime, subprocess

from kppcommon import ROOT, write_js

SRC = ROOT / 'kpp' / 'sources.json'
OUT = ROOT / 'kpp' / 'sources.js'
CHECK = '--check' in sys.argv

data = json.loads(SRC.read_text(encoding='utf-8'))

n = sum(len(g['items']) for g in data['groups'])
print(f'{SRC.name}: {len(data["groups"])} groups, {n} sources, '
      f'{len(data.get("caveats", []))} caveats')

seen = set()
for g in data['groups']:
    for it in g['items']:
        if it['url'] in seen:
            print(f'  !! duplicate url: {it["url"]}')
        seen.add(it['url'])
        if not it['url'].startswith('https://'):
            print(f'  !! not https: {it["url"]}')

if CHECK:
    # curl, not urllib: some of these hosts refuse Python's requests outright,
    # and a checker that reports a live link as dead is worse than no checker.
    if not shutil.which('curl'):
        raise SystemExit('--check needs curl on PATH')
    print('\nchecking every link:')
    for g in data['groups']:
        for it in g['items']:
            out = subprocess.run(
                ['curl', '-sIL', '-o', os.devnull, '--max-time', '30',
                 '-w', '%{http_code} %{content_type}', it['url']],
                capture_output=True, text=True).stdout.strip()
            code, _, kind = out.partition(' ')
            ok = ' ' if code.startswith('2') else '!'
            print(f'  {ok} {code:<5} {kind[:26]:<28} {it["url"][:70]}')
    print('  (a non-2xx is not automatically dead — some hosts gate automated '
          'fetches\n   while working normally in a browser; open it and see)')

write_js(OUT, 'KPP_SOURCES', {
    'meta': {'built': datetime.date.today().isoformat(), 'count': n},
    'groups': data['groups'],
    'caveats': data.get('caveats', []),
})
print(f'\nwrote {OUT.relative_to(ROOT)}')
