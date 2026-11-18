"""Efectos de sonido sintetizados y mezcla sobre los teasers.

Uso: python3 sfx.py   (necesita los vídeos de teaser.py en salida/)
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

from teaser import LEVELS, DUR, OUT

SR = 44100
rng = np.random.default_rng(7)


def env(n, attack, release):
    """Envolvente con ataque lineal y caída exponencial."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / release)


def lowpass(x, cutoff):
    """Filtro paso bajo de un polo; `cutoff` puede variar por muestra."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    k = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += k[i] * (x[i] - acc)
        y[i] = acc
    return y


# --- sonidos ---------------------------------------------------------------

def whoosh(dur=0.45):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    band = lowpass(noise, 300 + 3500 * np.sin(np.pi * t)) - lowpass(noise, 150)
    return band * np.sin(np.pi * t) ** 2 * 1.4


def pop(f0=650, f1=180, dur=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = f1 + (f0 - f1) * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * env(n, 0.002, 0.04) * 0.9


def tick(freq=1900, dur=0.05):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env(n, 0.001, 0.012) * 0.45


def click(dur=0.06):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 1100 * t) * env(n, 0.001, 0.015)
    return (body + rng.standard_normal(n) * env(n, 0.0005, 0.004) * 0.4) * 0.5


def chime(notes=(880, 1318.5), gap=0.09, dur=0.9):
    """'Respuesta correcta': dos notas ascendentes tipo campanita."""
    n = int((dur + gap * len(notes)) * SR)
    out = np.zeros(n)
    for i, f in enumerate(notes):
        m = int(dur * SR)
        t = np.arange(m) / SR
        tone = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
                + 0.12 * np.sin(2 * np.pi * 3.01 * f * t))
        s = int(i * gap * SR)
        out[s:s + m] += tone * env(m, 0.003, 0.28) * 0.35
    return out


def riser(dur=0.6):
    """Subidita suave antes del cierre."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    freq = 300 + 500 * t ** 2
    tone = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    return tone * t ** 2 * (1 - t ** 8) * 0.18


# --- línea de tiempo (sincronizada con teaser.py) --------------------------

def timeline(lv):
    ev = [
        (0.05, whoosh(), 0.7),
        (0.50, pop(), 1.0),
        (2.30, whoosh(), 0.7),
        (2.50, pop(520, 140, 0.15), 1.0),
        (3.00, pop(900, 500, 0.08), 0.6),
        (5.30, whoosh(), 0.7),
        (6.90, chime(), 1.0),
        (7.75, riser(), 1.0),
        (8.20, whoosh(), 0.6),
        (8.50, pop(), 1.0),
        (9.00, click(), 1.0),
    ]
    # un tick por cada barra de nivel que se rellena
    # (inversa del ease_out de level_bars: momento en que la barra i queda casi llena)
    for i in range(lv["n"]):
        k = 0.95 * (i + 1) / lv["n"]
        ev.append((2.4 + 0.8 * (1 - (1 - k) ** (1 / 3)), tick(1600 + 300 * i), 1.0))
    # las 4 opciones del test aparecen
    for i in range(4):
        ev.append((5.75 + i * 0.15, click(), 0.6))
    return ev


def mix(events):
    out = np.zeros(int(DUR * SR) + SR)
    for t, snd, gain in events:
        s = int(t * SR)
        out[s:s + len(snd)] += snd[: len(out) - s] * gain
    out = out[: int(DUR * SR)]
    out *= 0.85 / np.max(np.abs(out))  # pico a ~-1.4 dBFS; bajar al mezclar con voz
    return np.stack([out, out], axis=1)


def write_wav(path, stereo):
    data = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    for key, lv in LEVELS.items():
        wav = OUT / f"sfx_{key}.wav"
        write_wav(wav, mix(timeline(lv)))
        src = OUT / f"teaser_actic_{key}.mp4"
        dst = OUT / f"teaser_actic_{key}_sfx.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-i", str(wav),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-movflags", "+faststart", str(dst)], check=True)
        print("ok", dst)
