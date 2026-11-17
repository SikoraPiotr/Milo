"""Pitch (f0) from the Scicom-intl ONNX exports of RMVPE, FCPE, CREPE and PESTO, with numpy and
onnxruntime only (no torch). Each graph contains its model's own front end, so the only input is
16 kHz mono float32 audio (CREPE: its 1024-sample frames, cut here).

    from pitch_onnx import PitchModel
    m = PitchModel("rmvpe.onnx")                 # or fcpe.onnx, crepe-full.onnx, crepe-tiny.onnx, pesto.onnx
    f0, voiced, confidence = m(audio_16k)        # one value per 10 ms frame, frame i centred at i * 10 ms
                                                 # (FCPE: i * 10 ms + 5 ms, its STFT is uncentred)

Voicing thresholds default to the ones that gave the lowest F0 frame error on PTDB-TUG's dev
speakers (see the model card); pass `threshold=` to change it.
"""
from __future__ import annotations

import numpy as np
import onnxruntime as ort

SR = 16000
HOP = 160

# CREPE and RMVPE: 360 bins of 20 cents from 1997.38 cents re 10 Hz (32.70 Hz).
CREPE_CENTS = 1997.3794084376191 + 20.0 * np.arange(360)
# FCPE: 360 bins evenly spaced in cents between 32.7 and 1975.5 Hz.
FCPE_CENTS = np.linspace(1200 * np.log2(32.7 / 10), 1200 * np.log2(1975.5 / 10), 360)

# Voicing thresholds on the peak salience (PESTO: its confidence), chosen on PTDB-TUG's dev
# speakers for the lowest F0 frame error (evaluate.py). The upstream defaults are lower (RVC 0.03,
# torchfcpe 0.006, torchcrepe 0.21) and call far more unvoiced frames voiced.
DEFAULT_THRESHOLD = {"rmvpe": 0.35, "fcpe": 0.33, "crepe-full": 0.61, "crepe-tiny": 0.58, "pesto": 0.12}


def local_average_cents(sal: np.ndarray, cents: np.ndarray, width: int = 4) -> np.ndarray:
    """sal [T, K] -> cents [T]: salience-weighted mean of the bins within `width` of the peak
    (the decoder RMVPE, FCPE and CREPE ship with)."""
    k = sal.shape[1]
    idx = np.clip(sal.argmax(1)[:, None] + np.arange(-width, width + 1)[None, :], 0, k - 1)
    w = np.maximum(np.take_along_axis(sal, idx, 1), 0)
    return (w * cents[idx]).sum(1) / np.maximum(w.sum(1), 1e-12)


def crepe_frames(audio: np.ndarray) -> np.ndarray:
    """torchcrepe's framing: zero-pad 512 each side, 1024-sample frames every 160 samples."""
    a = np.pad(audio, (512, 512))
    n = 1 + len(audio) // HOP
    idx = np.arange(1024)[None, :] + HOP * np.arange(n)[:, None]
    return a[idx].astype(np.float32)


class PitchModel:
    def __init__(self, path: str, threshold: float | None = None, threads: int = 1):
        o = ort.SessionOptions()
        o.intra_op_num_threads = threads
        self.sess = ort.InferenceSession(path, o, providers=["CPUExecutionProvider"])
        ins = [i.name for i in self.sess.get_inputs()]
        outs = [o.name for o in self.sess.get_outputs()]
        name = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
        if "frames" in ins:
            self.kind, key = "crepe", ("crepe-tiny" if "tiny" in name else "crepe-full")
        elif "pitch_hz" in outs:
            self.kind = key = "pesto"
        else:
            self.kind = key = "fcpe" if "fcpe" in name else "rmvpe"
        self.threshold = DEFAULT_THRESHOLD[key] if threshold is None else threshold

    def salience(self, audio: np.ndarray):
        """Raw model output: [T, 360] salience (PESTO: (pitch_hz [T], confidence [T]))."""
        audio = np.ascontiguousarray(audio, dtype=np.float32)
        if self.kind == "pesto":
            p, c, _a = self.sess.run(None, {"audio": audio[None]})
            return p[0], c[0]
        if self.kind == "crepe":
            fr = crepe_frames(audio)
            return np.concatenate([self.sess.run(None, {"frames": f})[0]
                                   for f in np.array_split(fr, max(1, len(fr) // 512))])
        return self.sess.run(None, {"audio": audio[None]})[0][0]

    def __call__(self, audio: np.ndarray):
        """16 kHz mono audio -> (f0 Hz [T], voiced bool [T], confidence [T]); f0 is 0 where unvoiced."""
        if self.kind == "pesto":
            f0, conf = self.salience(audio)
            f0, conf = f0.astype(np.float64), conf.astype(np.float64)
        else:
            sal = self.salience(audio).astype(np.float64)
            cents = local_average_cents(sal, FCPE_CENTS if self.kind == "fcpe" else CREPE_CENTS)
            f0, conf = 10.0 * 2 ** (cents / 1200.0), sal.max(1)
        voiced = conf > self.threshold
        return np.where(voiced, f0, 0.0), voiced, conf
