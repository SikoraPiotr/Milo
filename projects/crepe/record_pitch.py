"""Nagrywa około 15 s z mikrofonu i liczy wysokość głosu modelem CREPE (co 10 ms)."""

from __future__ import annotations

import sys
import wave
from datetime import date
from pathlib import Path

import numpy as np
import sounddevice as sd

from pitch_onnx import PitchModel

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
MODEL = ROOT / "crepe-tiny.onnx"
OUT = REPO / "memory" / "glos-probka.md"
SR = 16000
SECONDS = 15


def characterize(mean_hz: float, span_hz: float) -> str:
    if mean_hz < 120:
        register = "niski rejestr"
    elif mean_hz < 180:
        register = "średni rejestr, zwykły dla mowy"
    elif mean_hz < 250:
        register = "wyższy rejestr"
    else:
        register = "wysoki rejestr"
    if span_hz < 40:
        motion = "głos trzyma się wąsko, mało się waha"
    elif span_hz < 100:
        motion = "zwykły ruch wysokości"
    else:
        motion = "szeroki ruch wysokości"
    return f"{register}; {motion}"


def load_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as handle:
        if handle.getframerate() != SR or handle.getnchannels() != 1:
            raise RuntimeError(
                f"WAV ma być {SR} Hz, mono. Jest {handle.getframerate()} Hz, "
                f"{handle.getnchannels()} kanałów."
            )
        frames = handle.readframes(handle.getnframes())
        width = handle.getsampwidth()
    if width == 2:
        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif width == 4:
        samples = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise RuntimeError(f"Nieobsługiwana szerokość próbki: {width}")
    return samples


def main() -> int:
    if not MODEL.is_file():
        print(f"Brak wag: {MODEL}", file=sys.stderr)
        return 2
    source = f"{SECONDS} s z mikrofonu"
    if len(sys.argv) > 1:
        wav_path = Path(sys.argv[1])
        try:
            y = load_wav(wav_path)
        except Exception as exc:
            print(f"PLIK_NIEDOSTEPNY: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 3
        source = f"plik {wav_path.name}, {len(y) / SR:.1f} s"
        print(f"Czytam {wav_path}", flush=True)
    else:
        try:
            device = sd.query_devices(kind="input")
            print(f"Mikrofon: {device['name']}", flush=True)
            print(f"Nagrywam {SECONDS} s. Mów teraz.", flush=True)
            audio = sd.rec(int(SECONDS * SR), samplerate=SR, channels=1, dtype="float32")
            sd.wait()
        except Exception as exc:
            print(f"MIKROFON_NIEDOSTEPNY: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 3
        y = np.asarray(audio[:, 0], dtype=np.float32)
    peak = float(np.max(np.abs(y))) if y.size else 0.0
    model = PitchModel(str(MODEL))
    f0, voiced, _conf = model(y)
    voiced_f0 = f0[voiced]
    n_frames = int(f0.shape[0])
    n_voiced = int(voiced_f0.shape[0])

    if n_voiced == 0:
        text = (
            f"# Próbka głosu\n\n"
            f"{date.today().isoformat()}. CREPE tiny, klatka co 10 ms, {source}.\n\n"
            f"Żadna klatka nie wyszła jako dźwięczna (próg modelu). "
            f"Szczyt nagrania: {peak:.4f}. Próbka jest za cicha albo to nie jest głos.\n"
        )
        OUT.write_text(text, encoding="utf-8")
        print(text)
        print(f"ZAPISANO {OUT}")
        return 0

    avg = float(voiced_f0.mean())
    lo = float(voiced_f0.min())
    hi = float(voiced_f0.max())
    span = hi - lo
    desc = characterize(avg, span)
    text = (
        f"# Próbka głosu\n\n"
        f"{date.today().isoformat()}. CREPE tiny, klatka co 10 ms, {source}. "
        f"Liczby tylko z klatek, które model uznał za dźwięczne ({n_voiced} z {n_frames}).\n\n"
        f"- średnia: {avg:.1f} Hz\n"
        f"- minimum: {lo:.1f} Hz\n"
        f"- maksimum: {hi:.1f} Hz\n"
        f"- rozpiętość: {span:.1f} Hz\n"
        f"- opis: {desc}\n"
        f"- szczyt nagrania: {peak:.4f}\n"
    )
    OUT.write_text(text, encoding="utf-8")
    print(text)
    print(f"ZAPISANO {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
