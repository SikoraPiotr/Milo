# Próbka głosu

2026-11-17. CREPE tiny, klatka co 10 ms. Nagranie 15 s z domyślnego wejścia: Microphone (USB Audio).

Żadna klatka nie wyszła jako dźwięczna. Szczyt nagrania: 0.0001. Średniej, minimum, maksimum i rozpiętości nie ma, bo nie było głosu w sygnale.

Inne wejścia, sprawdzone krótko:

- Microphone (Realtek(R) Audio): otwarte, szczyt około 0.0004, też cisza.
- SteelSeries Sonar - Microphone: nie otwarte. PortAudioError -9996, Invalid device.
- Słuchawki LE-Bose NC 700 HP i Twins Breez: nie startują. PortAudioError -9999, Windows WDM-KS, GLE 0x0000048F (urządzenie niepodłączone).
