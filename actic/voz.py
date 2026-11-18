"""Locución en castellano (ElevenLabs) mezclada con los efectos sobre los teasers.

Uso: python3 voz.py   (necesita los vídeos de teaser.py en salida/)
La clave se toma de ELEVENLABS_API_KEY; sin ella, se confía en el proxy.
Las locuciones se guardan en salida/voz/ y no se vuelven a pedir si ya existen.
"""
import json
import os
import subprocess
import urllib.request
from pathlib import Path

import numpy as np

from sfx import SR, mix, timeline, write_wav
from teaser import DUR, LEVELS, OUT

VOICE_ID = "TZ3pgF19H1pelFonL8Zq"
MODEL_ID = "eleven_multilingual_v2"
VOZ_DIR = OUT / "voz"
MAX_TEMPO = 1.2  # aceleración máxima para encajar una frase en su escena

NIVEL = {
    "basico": "Nivel básico. Uno de tres: fácil.",
    "medio": "Nivel medio. Dos de tres: intermedio.",
    "avanzado": "Nivel avanzado. Tres de tres: difícil.",
}


def lines(key):
    """(inicio, fin del hueco, texto) sincronizado con las escenas de teaser.py."""
    return [
        (0.15, 2.30, "¿Te presentas al examen ACTIC?"),
        (2.50, 5.30, NIVEL[key]),
        (5.50, 6.85, "¿Sabrías aprobar?"),  # antes de la campanita (6.90)
        (8.25, DUR - 0.1, "Muy pronto. ¡Síguenos!"),
    ]


# --- TTS -------------------------------------------------------------------

def tts(text, path):
    if path.exists():
        return
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
           "?output_format=mp3_44100_128")
    body = json.dumps({
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3},
    }).encode()
    headers = {"Content-Type": "application/json", "Accept": "audio/mpeg"}
    if os.environ.get("ELEVENLABS_API_KEY"):
        headers["xi-api-key"] = os.environ["ELEVENLABS_API_KEY"]
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as r:
        path.write_bytes(r.read())


def decode(path, tempo=1.0):
    """mp3 -> float32 mono a SR, recortando silencios al principio y al final."""
    af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
    if tempo != 1.0:
        af += f",atempo={tempo:.4f}"
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-af", af,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


# --- mezcla ----------------------------------------------------------------

def voice_track(key):
    out = np.zeros(int(DUR * SR))
    for i, (start, end, text) in enumerate(lines(key)):
        mp3 = VOZ_DIR / f"{key}_{i}.mp3"
        tts(text, mp3)
        clip = decode(mp3)
        slot = end - start
        dur = len(clip) / SR
        if dur > slot:
            tempo = min(dur / slot, MAX_TEMPO)
            clip = decode(mp3, tempo)
            if len(clip) / SR > slot:
                print(f"  aviso: '{text}' dura {len(clip) / SR:.2f}s para un hueco de {slot:.2f}s")
        s = int(start * SR)
        n = min(len(clip), len(out) - s)
        out[s:s + n] += clip[:n]
    return out


def duck(voice, depth=0.6, attack=0.03, release=0.25):
    """Ganancia para los efectos: baja `depth` mientras suena la voz."""
    level = np.abs(voice) > 0.02
    g = np.where(level, 1 - depth, 1.0)
    # suavizado asimétrico (rápido al bajar, lento al subir)
    ka, kr = 1 / (attack * SR), 1 / (release * SR)
    y = np.empty_like(g)
    acc = 1.0
    for i, v in enumerate(g):
        acc += (ka if v < acc else kr) * (v - acc)
        y[i] = acc
    return y


if __name__ == "__main__":
    VOZ_DIR.mkdir(parents=True, exist_ok=True)
    for key, lv in LEVELS.items():
        voice = voice_track(key)
        fx = mix(timeline(lv))[:, 0] * 0.55
        out = voice + fx * duck(voice)
        out *= 0.9 / np.max(np.abs(out))
        wav = OUT / f"voz_{key}.wav"
        write_wav(wav, np.stack([out, out], axis=1))
        src = OUT / f"teaser_actic_{key}.mp4"
        dst = OUT / f"teaser_actic_{key}_voz.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-i", str(wav),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-movflags", "+faststart", str(dst)], check=True)
        print("ok", dst)
