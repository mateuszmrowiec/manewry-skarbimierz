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
rekonstrukcją. Zestawiamy pięć niezależnych i pozwalamy im głosować.

| Źródło | Wpisy | Postać |
|---|---|---|
| **PDF 2024/2025** | 281 | dwa PDF-y z **pogrubioną** poprawną odpowiedzią — patrz niżej |
| **quizlet 710735124** | 100 | fiszki: pytanie → treść poprawnej odpowiedzi |
| **quizlet 595014549** | 250 | jw., wydanie 2021 |
| **quizlet 804902455** | 150 | fiszki odwrócone: awers = sama litera, rewers = pytanie |
| **feniks.care** | 280 | quiz PHP, `const poprawna` w treści strony, plus uzasadnienia |

- feniks.care: `https://feniks.care/quiz_kpp.php?tryb=nauka&id=N`, N = 1..280

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
| `verified` — zgodne, ≥ 2 źródła | **249** |
| `single-source` — tylko jedno źródło | 26 |
| `majority` — źródła niezgodne, jest większość | 2 |
| `conflict` — remis | 1 |
| **Razem** | **278** |

Rozkład liczby zgodnych źródeł: 1 → 26, 2 → 106, 3 → 62, 4 → 49, 5 → 35.
Każde pytanie ma klucz; żadne nie zostało bez odpowiedzi.

Ile pytań obsłużyło każde źródło: PDF 2024/2025 276, feniks.care 243,
quizlet-595014549 117, quizlet-804902455 89, quizlet-710735124 70.

### Do rozstrzygnięcia przez instruktora

**Nr 44** — *Po spożyciu przez poszkodowanego dużej ilości leków…* — 4:1.
`B` prowokować wymioty (PDF + trzy zestawy Quizlet) vs `C`
zabezpieczyć opakowania (feniks.care). Prowokowanie wymiotów jest dziś
przeciwwskazane — do potwierdzenia, czego oczekuje komisja.

**Nr 79** — *W przypadku braku szyn Kramera…* — 3:2 za `E`.
`E` przymocowanie do drugiej kończyny **z przekładką** (trzy zestawy Quizlet)
vs `D` bez przekładki (PDF, feniks.care). Klucz wskazuje `E`, ale
przewagą jednego głosu — a dwa źródła po stronie `D` to te, które pokrywają
bazę najpełniej.

**Nr 175** — *Zastępcza wentylacja przy niedrożności nosa…* — remis 1:1.
`B` maska worka samorozprężalnego chwytem jednoręcznym (PDF) vs
`E` prawdziwe są odpowiedzi A i B (quizlet-595014549).

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
