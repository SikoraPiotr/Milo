# Programowanie

Nadrzędne reguły, jak piszę kod. Nie są od projektu. Projekt może dodać swoje. Tego nie wyłącza.

Piotr, 2026-11-03: myśl atomowo ma tu stać, nie w jednorazowej uwadze przy recenzji.
Piotr, 2026-11-03: zawsze szukaj reguł programowania w otwartym projekcie. One są nadrzędne. Wiedzy o projekcie nie składaj z pamięci czatu.
Piotr, 2026-11-05: do ludzi mów słowami ludzi. Słów z reguł i notatek nie wkładaj do zdań dla nich.
Piotr, 2026-11-09: komunikacja jest nadrzędna. Ucz się, jak my mówimy, i tak pisz. Przyjaźnie jak UI. Para słów to przykład, nie cała reguła. `communication.md`.

## Szukaj reguł w projekcie

Zanim napiszesz albo recenzujesz kod: znajdź w tym workspace pliki zasad (Commands, rules, standard repo, CLAUDE.md). Przeczytaj. Stosuj jako nadrzędne.

Nie odtwarzaj ich z poprzedniej rozmowy. Projekt mógł dopisać zasadę, której nie pamiętasz.

Wiedzę o tym, jak system działa, też bierz z projektu: kod, testy, plik obok. Pamięć między czatami jest druga.

## Myśl atomowo

Jedna rzecz na ekranie albo w logice = jeden nazwany atom.

Ten sam znacznik, klasa albo rytuał drugi raz w tej samej roli to nie kopia. To brak atomu. Zrób mały komponent, dyrektywę, funkcję albo helper. Potem używaj.

Gdy atom to tylko klasy na istniejącym znaczniku, zrób dyrektywę. Nie owijaj znacznika w nowy tag.

Atom jest mały: linia tekstu, para etykieta-wartość, jedno porównanie. Nie strona i nie worek „utils”.

Zanim dodasz nowy, szukaj istniejącego. Nie wyciągaj, gdy kopie mają się rozjechać z powodu.

Źle: pięć razy ten sam znacznik z innym tekstem.
Dobrze: jeden atom, różne wejścia.

## Lokalny adres do testu

Piotr, 2026-11-06: nie wymyślaj drugiego localhost, gdy właściwy port jest zajęty. Nie otwieraj w panelu logowania na 5011/5012. Lokalny test UI = URL z `npm start` w tym repo. Jak port zajęty: zdejmij stary proces albo powiedz. Nie zakładaj ślepego adresu. Finalnie zadanie UI kończysz end-to-end na tym adresie: przeklikać ścieżkę, nie sam ekran logowania.
