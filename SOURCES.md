# Źródła — baza pytań KPP

## Pytania (autorytatywne)

**Centrum Egzaminów Medycznych (CEM)** — <https://www.cem.edu.pl/ppomoc.php>
- Plik: <https://www.cem.edu.pl/pliki/KPP2026.pdf> (`docs/KPP2026-CEM-official.pdf`)
- Wersja z 17.06.2026, 278 pytań (numeracja 1–280, bez 13 i 218)
- CEM jest państwową jednostką budżetową podległą Ministrowi Zdrowia, więc
  publikowana przez nie baza to **materiał urzędowy** — art. 4 pkt 2 ustawy
  o prawie autorskim, czyli nie jest przedmiotem prawa autorskiego.
- **CEM nie publikuje klucza odpowiedzi.** To świadoma decyzja.

Egzamin teoretyczny to 30 pytań z tej bazy, próg zaliczenia 90 % (27/30).

## Klucze odpowiedzi (nieoficjalne)

Skoro nie istnieje oficjalny klucz, każdy krążący klucz jest czyjąś
rekonstrukcją. Zestawiamy je i pozwalamy im głosować.

Źródła są **trzy**, nie sześć. Sześć plików — ale dwa PDF-y to jedno źródło
w dwóch wydaniach, a trzy zestawy Quizlet to jeden klucz przepisywany między
fiszkami. Uzasadnienie niżej; liczenie ich osobno produkowałoby potwierdzenia,
których nie ma.

| Źródło | Wpisy | Postać |
|---|---|---|
| **PDF 2024/2025** | 281 | dwa PDF-y z **pogrubioną** poprawną odpowiedzią |
| **Quizlet 2021/2023** | 409 | trzy zestawy fiszek, scalone |
| **feniks.care** | 280 | quiz PHP, `const poprawna` w treści strony, plus uzasadnienia |

- feniks.care: `https://feniks.care/quiz_kpp.php?tryb=nauka&id=N`, N = 1..280

### Dlaczego trzy zestawy Quizlet to jedno źródło

| Zestaw | Kart | Ostatnia zmiana | Postać |
|---|---|---|---|
| 804902455 | 250 | 2023-05-22 | fiszki odwrócone: awers = sama litera |
| 710735124 | 100 | 2022-07-06 | pytanie → treść poprawnej odpowiedzi |
| 595014549 | 250 | 2021-10-03 | jw. |

Tam, gdzie którekolwiek dwa zestawy dotyczą tego samego pytania, **zgadzają się
co do jednego**:

```
710735124 vs 595014549:  37/37
710735124 vs 804902455:  62/62
595014549 vs 804902455:  55/55
```

154 porównania, zero rozbieżności. Trzy osoby przepisujące klucz niezależnie
tak nie trafiają — tak wygląda jeden klucz kopiowany między zestawami, w latach
2021, 2022 i 2023. Traktujemy je więc jako **jedno źródło**, scalone
`merge_keys()` od najnowszego, tak samo jak PDF-y.

Skutek jest jeden i konkretny: **Nr 79** miał 3:2 za `E`, bo trzy „niezależne"
głosy to był ten sam głos policzony trzykrotnie. Po scaleniu jest 1:2 za `D`.
To nie rozstrzyga, która odpowiedź jest **poprawna** — usuwa tylko pozorne
potwierdzenie. Pytanie zostaje na liście do weryfikacji.

### Dlaczego oba PDF-y to jedno źródło

- <https://drogaratownika.pl/baza-plikow/cmeitwl4b0015p60hyl5mz5cd> — wydanie
  z 29.07.2024, 280 pytań
- <https://dlaratownikaimedyka.pl/wp-content/uploads/2025/06/kpp-pytania-i-odpowiedzi-2025.pdf>
  — wydanie z 04.06.2025, 279 pytań sparsowanych

Oba wskazują w metadanych tego samego autora i zgadzają się w **220 na 220**
wspólnych pytań — zero rozbieżności. To ten sam klucz w dwóch wydaniach, więc
liczymy go **jako jedno źródło**; traktowanie ich osobno sztucznie zawyżałoby
liczbę „niezależnych" potwierdzeń.

W aplikacji źródło to występuje jako **PDF 2024/2025**. Nazwisko autora zostaje
w metadanych plików — nie ma powodu, by wymieniać osobę prywatną na publikowanej
stronie.

Nowsze wydanie ma pierwszeństwo, starsze uzupełnia braki.

> Uwaga metodyczna: konwerter PDF użyty w wydaniu 2025 gubi kropkę po numerze
> w pierwszym pytaniu każdej strony (`Nr 175 U poszkodowanego…` zamiast
> `Nr 175.`). Wymaganie kropki w wyrażeniu regularnym po cichu odrzucało
> **37 pytań** — dlatego kropka jest opcjonalna.

### Rozstrzyganie remisów

Gdy głosy dzielą się po równo, klucz przyjmuje odpowiedź z **wydania 2025**
(`TIEBREAK_EDITION` w skrypcie) jako najnowszej rekonstrukcji, jaką mamy.
Pole `pdf_edition` przy pytaniu mówi, z którego wydania pochodzi ten głos.
To reguła porządkowa, nie dowód — pytania rozstrzygnięte w ten sposób
pozostają oznaczone jako `conflict`.

Żaden z tych plików nie jest w repozytorium — patrz `.gitignore`.

> **Zastrzeżenie co do feniks.care.** Część treści pytań jest parafrazowana
> (`resuscytacji krążeniowo-oddechowej` → `RKO`), a uzasadnienia sprawiają
> wrażenie generowanych maszynowo. Traktujemy je jako mocne, ale prawdopodobnie
> niesamodzielne potwierdzenie — nie jako czyste źródło ludzkie.

### Sprawdzone, bez klucza

`niebiescy997.pl`, `kursyratownictwa.pl` (3 quizy), `centrumratownictwa.com`,
`cormedratownictwo.pl`, `aquamed.pl`, `strefa998`, Fiszkoteka, Brainscape,
AnkiWeb — wszystkie oceniają po stronie serwera albo publikują same pytania.
`memorizer.pl/powtorzenie/7897` ma klucz, ale do **wydania z 2011 r.** — inne
pytania i inna doktryna, więc to szum, nie kontrola.

> Uwaga metodyczna: PDF z dlaratownikaimedyka.pl był początkowo odrzucony jako
> „bez odpowiedzi", bo wyodrębniony tekst ich nie pokazuje. Odpowiedzi są
> zaznaczone **krojem pisma**, nie treścią — trzeba czytać `/BaseFont` z run-ów
> tekstowych. Ten sam błąd łatwo popełnić przy każdym kolejnym PDF-ie.

## Zasady zestawiania

Dwie reguły, których trzyma się `tools/kppcommon.py`:

1. **Pytania dopasowujemy po treści — nigdy po numerze.** Numeracja zmienia się
   między wydaniami. Dopasowanie liczy treść pytania *i* treść odpowiedzi,
   bo kilka pytań ma identyczną treść (`Wskaż fałszywe stwierdzenie:`),
   a inne różnią się tylko wiekiem poszkodowanego.
2. **Odpowiedzi porównujemy po treści — nigdy po literze.** Kolejność opcji
   również się zmienia: `D. prawdziwe A i B` w jednym wydaniu bywa `E` w innym.

Opcje wskazujące na inne opcje (`prawdziwe są odpowiedzi A i B`,
`wszystkie wymienione`) sprowadzane są do zbioru liter, więc różne
sformułowania tej samej odpowiedzi porównują się poprawnie.

Gdy dwie opcje różnią się tylko liczbą (`8 l/min` vs `15 l/min`,
`¼` vs `⅓`), źródło musi trafić w treść dokładnie — inaczej wstrzymuje się
od głosu, zamiast zgadywać.

## Wynik

| Status | Pytań |
|---|---|
| `verified` — zgodne, ≥ 2 źródła | **252** |
| `single-source` — tylko jedno źródło | 23 |
| `majority` — źródła niezgodne, jest większość | 2 |
| `conflict` — remis | 1 |
| **Razem** | **278** |

Rozkład liczby zgodnych źródeł: 1 → 23, 2 → 127, 3 → 128.
Każde pytanie ma klucz; żadne nie zostało bez odpowiedzi.

Ile pytań obsłużyło każde źródło: PDF 2024/2025 278, feniks.care 244,
Quizlet 2021/2023 139.

Wszystkie 23 pytania `single-source` stoją wyłącznie na PDF-ie — to najcieńszy
lód w całym kluczu:

```
38, 83, 159, 164, 170, 171, 185, 188, 189, 191, 229, 237,
239, 240, 242, 251, 261, 262, 265, 266, 268, 269, 276
```

> Uwaga metodyczna: przy dopasowywaniu pytań remis między niemal identycznymi
> wpisami oznaczał wstrzymanie się od głosu. Po scaleniu wydań jednego klucza
> takich remisów robi się dużo — wpisy różnią się kropką na końcu — i kosztowało
> to 41 pytań pokrycia bez żadnego zysku. Teraz remis blokuje głos tylko wtedy,
> gdy remisujące wpisy **wskazują różne odpowiedzi**. Pytania różniące się
> wiekiem poszkodowanego czy dawką nadal się wykluczają, bo tam odpowiedzi
> faktycznie się różnią.

## Pytania wycofane przez CEM

Baza KPP2026 numeruje 1–280, ale zawiera **278 pytań** — brakuje **13** i **218**.
To nie jest błąd parsowania: oficjalny plik CEM tych numerów po prostu nie ma,
co potwierdza niezależnie `verify-cem.py`.

Numeracja **nie przesunęła się**: wszystkie 278 numerów wspólnych z wydaniem
2024 trzyma to samo pytanie, 278/278, każdy rdzeń dopasowany w 1.00. CEM
wyjął dwa pytania i zostawił dziury, zamiast przenumerować bazę.

Oba były w bazie co najmniej od 2021 do 2025 i wszystkie pięć zebranych
kluczy zgadza się co do nich:

| Nr | Temat | Stary klucz | Widziane w |
|---|---|---|---|
| 13 | ból w klatce piersiowej w autobusie, postępowanie | `E` (B, C i D) | 2021–2025 |
| 218 | RKO ciężarnej, odbarczenie aortalno-żylne | `D` (przechylenie w osi długiej) | 2021, 2024, 2025 |

Nr 218 wygląda na pytanie, które wyprzedziły wytyczne: dziś uczy się **ręcznego
przesunięcia macicy w lewo** (odpowiedź `A`), bo przechylanie całego ciała psuje
jakość uciśnięć. Stary klucz wskazuje `D`. Jeśli CEM wolał je wycofać niż
przekluczować, to dokładnie ten scenariusz, na który trzeba uważać w reszcie
klucza — baza jest z 2026, a klucze z lat 2021–2025.

Pytania te trzyma `kpp/retired.js`, budowany przez `tools/lock-retired.py`
(numer obecny w starszym wydaniu, nieobecny w bieżącym pliku CEM; treść i klucz
z najnowszego wydania, które je jeszcze miało). **Nie trafiają do
`questions.js`** — tamten plik cytuje wyłącznie bazę CEM i ma się zgadzać z nią
co do znaku. W teście pokazują się na swoim miejscu, wyszarzone, z etykietą
*wycofane po 2025*, bez możliwości odpowiadania i bez wpływu na wynik.

## Źródła merytoryczne

Wszystko powyżej to rekonstrukcje **cudzych kluczy** — mówią, co ktoś uznał za
poprawne, nie co jest poprawne. Do rozstrzygania spornych pytań potrzebna jest
doktryna, a nie kolejna kopia klucza:

- **ERC Guidelines 2025** — <https://www.erc.edu/science-research/guidelines/guidelines-2025/guidelines-2025-english>
  Wytyczne Europejskiej Rady Resuscytacji. Polskie szkolenia KPP opierają się na
  nich, więc to najbliższe „źródło prawdy", jakie tu mamy.

Uwaga na przesunięcie w czasie: baza pytań CEM to wydanie KPP2026, a krążące
klucze powstały w latach 2021–2025, częściowo jeszcze na wytycznych 2021.
Tam, gdzie wytyczne się zmieniły, klucz i doktryna mogą się rozjeżdżać —
i wtedy wygrywa to, czego oczekuje komisja egzaminacyjna, nawet jeśli
wytyczne mówią co innego. Taka rozbieżność jest warta odnotowania w `note`.

### Do rozstrzygnięcia przez instruktora

**Nr 44** — *Po spożyciu przez poszkodowanego dużej ilości leków…* — 2:1 za `B`.
`B` prowokować wymioty (PDF, Quizlet) vs `C` zabezpieczyć opakowania
(feniks.care). Prowokowanie wymiotów jest dziś przeciwwskazane — do
potwierdzenia, czego oczekuje komisja.

**Nr 79** — *W przypadku braku szyn Kramera…* — 2:1 za `D`.
`D` przymocowanie do drugiej kończyny (PDF, feniks.care) vs `E` to samo
**z przekładką** (Quizlet). Klucz wskazywał `E`, dopóki trzy zestawy Quizlet
liczyły się osobno; po scaleniu jest `D`. Uwaga: `E` opisuje to, czego uczy
się na kursach — przekładka między kończynami — więc *głosowanie* zmieniło
zdanie, a nie dowód. Do rozstrzygnięcia.

**Nr 175** — *Zastępcza wentylacja przy niedrożności nosa…* — remis 1:1.
`B` maska worka samorozprężalnego chwytem jednoręcznym (PDF) vs
`E` prawdziwe są odpowiedzi A i B (Quizlet).

## Kontrola zgodności z bazą CEM

```
python tools/verify-cem.py [--verbose]
```

Skrypt **nie korzysta z niczego z `kppcommon.py`**. Tamten moduł czyta PDF
przez `pypdf` ze śledzeniem pogrubień znak po znaku; ten czyta ten sam plik
przez `pdfplumber` (silnik `pdfminer.six`) i tnie tekst własnym podziałem.
Dwa silniki, dwa parsery — błąd wspólny dla obu jest znacznie mniej prawdopodobny
niż błąd w którymkolwiek z osobna.

Wynik z 14.09.2026, plik `KPP2026-CEM-official.pdf`:

| Sprawdzenie | Wynik |
|---|---|
| Liczba pytań | 278 w obu (numeracja 1–280, brak 13 i 218) |
| Numery pytań | identyczny zbiór, zero brakujących, zero nadmiarowych |
| Treść pytania | 278 z 278 zgodnych |
| Treść odpowiedzi | 1390 z 1390 zgodnych (5 opcji przy każdym pytaniu) |
| Litera klucza | zawsze wskazuje na istniejącą opcję |

Z 1668 porównywanych pól 1375 różniło się **wyłącznie kropką na końcu**
(świadomie usuwaną przy budowaniu bazy), a jedno — indeksem dolnym w `CO₂`,
który `pdfplumber` raportuje jako osobny wiersz. Poza tym teksty są
identyczne znak w znak.

**Czego to nie sprawdza.** CEM nie publikuje klucza, więc poprawności pola
`correct` nie da się tu potwierdzić. Kontrola dowodzi tylko, że pytania i
odpowiedzi są cytowane dokładnie — jeśli w teście coś jest błędne, błąd jest
w kluczu, nie w przepisaniu bazy.

## Wersja robocza do przeglądu

`kpp/review.html` (poza repozytorium) to ten sam test **bez losowania** —
pytania idą w kolejności numerów CEM, a każda karta ma nagłówek `Nr N`
i kotwicę `#qN`. Dzięki temu pytanie N w przeglądarce to pytanie N w PDF-ie
i da się je sprawdzać jedno po drugim.

`kpp/index.html` pozostaje komunikatem o wyłączeniu testu do czasu
zakończenia tej weryfikacji.

## Pytania zamrożone, klucz ruchomy

Pytania i klucz leżą w **osobnych plikach** i mają osobne narzędzia. To nie jest
kosmetyka: dopóki trzymaliśmy je razem, każde przebudowanie klucza przepisywało
też treść pytań, więc odpowiedź sprawdzona ręcznie mogła po cichu trafić do
pytania o zmienionym brzmieniu. Teraz zmienia się wyłącznie klucz.

```
python tools/lock-questions.py     # docs/KPP2026-CEM-official.pdf -> kpp/questions.js
python tools/build-answers.py      # źródła kluczy               -> kpp/answers.js
python tools/verify-cem.py         # niezależna kontrola obu
```

| Plik | Co zawiera | Kiedy się zmienia |
|---|---|---|
| `kpp/questions.js` | `window.KPP_QUESTIONS` — 278 pytań CEM + suma kontrolna | tylko przy nowym wydaniu bazy CEM |
| `kpp/answers.js` | `window.KPP_ANSWERS` — klucz, głosy, statusy | przy każdej poprawce klucza |
| `kpp/answers-manual.json` | odpowiedzi ustalone ręcznie | gdy coś zostanie rozstrzygnięte |

Zapis jako `.js` (`window.X = {...}`), a nie `.json`, bo przeglądarki blokują
`fetch()` dla adresów `file://`. Dzięki temu strona działa po zwykłym otwarciu
pliku, bez serwera HTTP.

### Zamek

`lock-questions.py` liczy SHA-256 ze wszystkich numerów, treści pytań, liter
i treści odpowiedzi. Suma trafia do `questions.js`, a `build-answers.py`
stempluje nią `answers.js`. Trzy rzeczy pilnują, żeby to się nie rozjechało:

- `lock-questions.py` uruchomiony ponownie na tym samym PDF-ie nic nie robi;
  jeśli pytania *wyszłyby* inne, **odmawia** i wypisuje, co się zmieniło.
  Nadpisanie wymaga `--force`.
- `build-answers.py` bierze pytania **wyłącznie** z `questions.js`, nigdy z PDF-a,
  i przerywa, jeśli plik nie zgadza się z własną sumą kontrolną.
- `review.html` nie pokaże testu, jeśli klucz zbudowano na innej bazie pytań —
  bo wtedy poprawna odpowiedź mogłaby wylądować przy nie tym pytaniu.

Stan na 14.09.2026: `012f39c495d248ac…`

### Odpowiedzi ustalone ręcznie

`kpp/answers-manual.json` przebija głosowanie i przeżywa każde przebudowanie
klucza — to tam trafia pytanie rozstrzygnięte z instruktorem:

```json
{ "44": { "correct": "C", "note": "kto i na jakiej podstawie" } }
```

Takie pytanie dostaje status `manual`, a karta w teście pokazuje żółtą etykietę
*ustalone ręcznie*, wpisaną odpowiedź, tę wygłosowaną i notatkę. Głosy źródeł
zostają widoczne — spór jest odnotowany, nie zamieciony.

Wymaga plików w `docs/`: PDF CEM, PDF z drogaratownika (nie w repozytorium)
oraz plików JSON z pozostałych źródeł.
