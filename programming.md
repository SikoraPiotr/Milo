# Programowanie

Nadrzędne reguły, jak piszę kod. Nie są od projektu. Projekt może dodać swoje. Tego nie wyłącza.

Piotr, 2026-11-03: myśl atomowo ma tu stać, nie w jednorazowej uwadze przy recenzji.

## Myśl atomowo

Jedna rzecz na ekranie albo w logice = jeden nazwany atom.

Ten sam znacznik, klasa albo rytuał drugi raz w tej samej roli to nie kopia. To brak atomu. Zrób mały komponent, funkcję albo helper. Potem używaj.

Atom jest mały: linia tekstu, para etykieta–wartość, jedno porównanie. Nie strona i nie worek „utils”.

Zanim dodasz nowy, szukaj istniejącego. Nie wyciągaj, gdy kopie mają się rozjechać z powodu.

Źle: pięć razy ten sam znacznik z innym tekstem.
Dobrze: jeden atom, różne wejścia.
