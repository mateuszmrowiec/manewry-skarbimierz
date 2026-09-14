# Gałąź `klucz` — robocza, nie do publikacji

Tu leży praca nad kluczem odpowiedzi do testu KPP. **Nie ma jej na `main`**
i nie powinno być.

## Czego tu nie robić

> **Nigdy nie scalaj tej gałęzi do `main`.**

`main` to gałąź, z której GitHub Pages publikuje stronę
<https://mateuszmrowiec.github.io/manewry-skarbimierz/> — cały katalog, jeden
do jednego. Wrzucenie tu obecnych plików na `main` oznacza, że
`kpp/review.html` staje się działającą, publicznie dostępną stroną, mimo że
test **świadomie wyłączyliśmy** — w kluczu znaleziono błędy. Nikt do niej nie
linkuje, ale adres działa i indeksuje się.

Na `main` ma zostać to, co jest teraz: `index.html`, `historia/`
i `kpp/index.html` z komunikatem o wyłączeniu.

## Uwaga przy commitowaniu

Pliki z tej gałęzi są wymienione w `.gitignore` — bo na `main` mają nie trafić.
Są tu **śledzone mimo to** (dodane przez `git add -f`), więc zmiany w nich
commitujesz normalnie:

```bash
git commit -am "…"          # działa, pliki są już śledzone
git add -f kpp/answers.js   # gdyby git kręcił nosem na .gitignore
```

## Uwaga przy przełączaniu gałęzi

Plików z tej gałęzi nie ma na `main`, więc `git checkout main` **usunie je
z katalogu roboczego** (`questions.js`, `answers.js`, `review.html`, `tools/`).
To nie jest utrata danych — `git checkout klucz` przywraca wszystko — ale
potrafi zaskoczyć. Najprościej po prostu siedzieć na `klucz`.

## Start na nowej maszynie

```bash
git clone https://github.com/mateuszmrowiec/manewry-skarbimierz.git
cd manewry-skarbimierz
git checkout klucz

pip install pypdf pdfplumber
python tools/fetch-sources.py        # odtwarza docs/ — feniks.care i Quizlet
```

`docs/` **nie jest w repozytorium**: to cudze materiały, których nie
rozpowszechniamy. `fetch-sources.py` ściąga, co się da; trzy PDF-y trzeba
pobrać ręcznie, linki są w nagłówku tego skryptu i w `SOURCES.md`:

| Plik | Skąd |
|---|---|
| `docs/KPP2026-CEM-official.pdf` | <https://www.cem.edu.pl/pliki/KPP2026.pdf> |
| `docs/dlaratownikaimedyka-2025.pdf` | link bezpośredni, `SOURCES.md` |
| `docs/5e6782f4-….pdf` | drogaratownika.pl, z listy plików |

Bez PDF-ów nie zbudujesz klucza — `build-answers.py` potrzebuje ich jako źródeł.
Sama baza pytań (`kpp/questions.js`) jest już zamrożona w repozytorium i PDF-u
CEM do niej nie potrzeba, poza kontrolą `verify-cem.py`.

## Praca

```bash
python tools/verify-cem.py           # czy baza pytań wciąż zgadza się z CEM
python tools/build-answers.py        # przebudowa klucza -> kpp/answers.js
```

Test otwierasz jako plik: `kpp/review.html` — bez serwera, bez losowania,
pytania w kolejności numerów CEM.

Poprawkę do klucza zapisujesz w `kpp/answers-manual.json`:

```json
{ "44": { "correct": "C", "note": "kto i na jakiej podstawie" } }
```

i uruchamiasz `build-answers.py`. Wpis przebija głosowanie źródeł i przeżywa
każde kolejne przebudowanie.

Szczegóły — źródła, zasady zestawiania, zamek na bazie pytań, stan
weryfikacji — w [`SOURCES.md`](SOURCES.md).

## Kiedy klucz będzie sprawdzony

Dopiero wtedy wraca publikacja, i to świadomą decyzją, nie scaleniem gałęzi:
na `main` przenosi się `kpp/questions.js`, `kpp/answers.js` oraz treść
`review.html` jako `kpp/index.html` (z losowaniem albo bez — do decyzji),
i zdejmuje komunikat o wyłączeniu.
