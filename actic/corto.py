"""Reels cortos ACTIC: una pregunta por vídeo, con gancho inicial de ~3 s.

Uso: python3 corto.py [basico medio avanzado | basico:7 ...]
Usa las locuciones de salida/quiz_voz/ (gancho, {nivel}_qN, {nivel}_aN).
Lleva subtítulos de la respuesta, música de fondo sintetizada y cierre con llamada a seguir.
"""
import math
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

from quiz import CARD_H, G, QUIZ, VOZ, art_card, cross, ctext, option_layer, text_layer, wrap
from sfx import SR, chime, click, lowpass, pop, riser, tick, whoosh, write_wav
from teaser import (FPS, H, INK, LEVELS, OUT, W, WHITE, background, clamp, ease_back, ease_out,
                    font, lerp, level_bars, paste, pill_layer, text)
from voz import decode, duck

HANDLE = "@acticdesdecasa"
DST = OUT / "cortos"

# Texto de los subtítulos (la locución usa grafías fonéticas: "jota pe ge", "ce, ce, o"...)
CAPTIONS = {
    "basico": ["¡La B! Control + C copia. Y Control + V, pega.",
               "¡La C! El navegador, como Chrome, Firefox o Edge.",
               "¡La D! .jpg es un formato de imagen. .mp3 es audio.",
               "¡La B! Retroceso borra a la izquierda. Supr, a la derecha.",
               "¡La B! A la Papelera de reciclaje. Desde ahí todavía puedes recuperarlos.",
               "¡La C! Larga, con letras, números y símbolos. Y distinta en cada cuenta.",
               "¡La B! Guarda el archivo con otro nombre o en otra carpeta, sin tocar el original.",
               "¡La C! El teclado envía datos al ordenador. El monitor y la impresora son de salida.",
               "¡La D! Es la dirección de una página web, la que escribes en el navegador.",
               "¡La C! La RAM. Por eso, si no guardas, pierdes lo que estabas haciendo.",
               "¡La B! Detecta y elimina programas maliciosos, como virus o troyanos.",
               "¡La D! Copiar duplica el archivo. Cortar lo mueve, y desaparece de su sitio original."],
    "medio": ["¡La B! Los dos puntos marcan un rango, de A1 a A5. Con punto y coma, solo sumarías dos celdas.",
              "¡La B! CCO: con copia oculta. Nadie verá las direcciones que pongas ahí.",
              "¡La D! El PDF mantiene el formato, las fuentes y las imágenes en cualquier dispositivo.",
              "¡La B! Escribes una carta modelo, y se rellena sola con los datos de cada persona.",
              "¡La C! CONTAR.SI. Por ejemplo, para saber cuántas celdas dicen «Sí».",
              "¡La B! Te escriben haciéndose pasar por tu banco o por una empresa, para robarte tus datos.",
              "¡La B! Hace que el texto siga en la página siguiente, aunque la actual no esté llena.",
              "¡La C! Da 6: suma 18 y lo divide entre los 3 valores.",
              "¡La D! Se guardan en servidores de internet, y puedes abrirlos desde cualquier dispositivo.",
              "¡La B! Estás dividiendo entre cero, o entre una celda vacía. Las almohadillas (####), en cambio, significan que la columna es estrecha.",
              "¡La C! Deja fijas las filas o columnas que elijas, por ejemplo los títulos, mientras te desplazas.",
              "¡La D! Al remitente, y a todos los destinatarios visibles. Piensa bien lo que escribes."],
    "avanzado": ["¡La B! Es una referencia absoluta: al copiar la fórmula, sigue apuntando a la celda A1.",
                 "¡La C! Solo indica que la conexión va cifrada. Una web fraudulenta también puede tener candado.",
                 "¡La D! Es el campo que identifica cada registro sin repetirse, como el DNI de una persona.",
                 "¡La B! El gráfico circular muestra cada dato como una porción del total.",
                 "¡La C! Le pide a la base de datos solo los registros que cumplen unos criterios.",
                 "¡La D! Además de la contraseña, te pide un código, por ejemplo en el móvil.",
                 "¡La B! Comprueba una condición, y devuelve un valor si se cumple, y otro si no.",
                 "¡La C! El software libre. Ojo: que un programa sea gratis no significa que sea libre.",
                 "¡La D! Es el efecto al pasar de una diapositiva a otra. Mover un objeto dentro de la diapositiva es una animación.",
                 "¡La B! Oculta las filas que no cumplen el criterio. Ordenar solo cambia el orden, no oculta nada.",
                 "¡La C! Quita información que casi no se nota, como en un .jpg o un .mp3. Un ZIP, en cambio, no pierde nada.",
                 "¡La A! Por ejemplo, un cliente puede tener muchos pedidos, pero cada pedido es de un solo cliente."],
}

# Estilo del gancho de cada vídeo (índice 0-based). Sin entrada: "classic" con gancho.mp3.
# Los que tienen estilo propio usan su locución gancho_{nivel}_{n}.mp3.
HOOKS = {
    ("basico", 9): "timer", ("basico", 10): "pov", ("basico", 11): "fail",
    ("medio", 9): "trap_a", ("medio", 10): "challenge", ("medio", 11): "trap",
    ("avanzado", 9): "versus", ("avanzado", 10): "nota", ("avanzado", 11): "comment",
}
RED = (205, 90, 80)

CAP_FONT = font("Bold", 50)
CAP_W = 900


def caption_chunks(s, start, dur):
    """Trocea el subtítulo por frases y, si una no cabe en 2 líneas, en partes equilibradas.

    El tiempo de cada bloque es proporcional a sus caracteres.
    """
    sentences = re.split(r"(?<=[.?»])\s+", s)  # ".jpg" o "CONTAR.SI" no cortan
    chunks = []
    for sent in (x.strip() for x in sentences if x.strip()):
        words = sent.split()
        n = math.ceil(len(wrap(sent, CAP_FONT, CAP_W)) / 2)
        while True:
            size = math.ceil(len(words) / n)
            parts = [" ".join(words[j:j + size]) for j in range(0, len(words), size)]
            if all(len(wrap(p, CAP_FONT, CAP_W)) <= 2 for p in parts):
                break
            n += 1
        chunks += parts
    # "¡La B!" solo es muy corto: se une al bloque siguiente si cabe
    if len(chunks) > 1 and len(chunks[0].split()) <= 2:
        joined = f"{chunks[0]} {chunks[1]}"
        if len(wrap(joined, CAP_FONT, CAP_W)) <= 2:
            chunks[:2] = [joined]
    total = sum(len(c) for c in chunks)
    out, t = [], start
    for c in chunks:
        d = dur * len(c) / total
        out.append((t, t + d, c))
        t += d
    return out


# --- línea de tiempo -----------------------------------------------------------

def build(key, i, hook=True):
    """Tiempos del vídeo. Con `hook`, empieza con el gancho y todo lo demás se desplaza `off`."""
    q = decode(VOZ / f"{key}_q{i + 1}.mp3")
    a = decode(VOZ / f"{key}_a{i + 1}.mp3")
    style = HOOKS.get((key, i), "classic")
    own = VOZ / f"gancho_{key}_{i + 1}.mp3"
    hk = decode(own if own.exists() else VOZ / "gancho.mp3") if hook else np.zeros(0)
    dq, da, dh = len(q) / SR, len(a) / SR, len(hk) / SR
    off = 0.15 + dh + 0.35 if hook else 0.0
    vq = off + 0.25
    cd = max(vq + dq + 0.3, off + 0.3 + 3 * 0.12 + 0.5)
    rv = cd + 3.0
    va = rv + 0.35
    end = va + da + 1.8
    return dict(q=q, a=a, hk=hk, off=off, hit=0.15 + second_phrase(hk, last=style == "pov"), dh=dh, style=style,
                vq=vq, cd=cd, rv=rv, va=va, end=end, caps=caption_chunks(CAPTIONS[key][i], va, da))


def second_phrase(clip, last=False):
    """Segundo en que empieza la 2ª parte del gancho: fin de la pausa interna más larga
    (o de la última, con `last`)."""
    if not len(clip):
        return 0.0
    win = int(0.02 * SR)
    rms = np.sqrt(np.convolve(clip ** 2, np.ones(win) / win, mode="same"))[::win]
    quiet = rms < 0.06 * rms.max()
    best, run, best_end = 0, 0, None
    lo, hi = int(0.3 / 0.02), len(quiet) - int(0.3 / 0.02)
    for j in range(lo, hi):
        run = run + 1 if quiet[j] else 0
        if run > best or (last and run * 0.02 >= 0.12):
            best, best_end = run, j + 1
    if best * 0.02 >= 0.12:
        return best_end * 0.02
    return 0.45 * len(clip) / SR


# --- vídeo ----------------------------------------------------------------------

def hook_frame(lv, sc, t):
    """Pantalla de gancho. Cada estilo enseña una primera frase y, en `hit`, el remate."""
    acc = lv["accent"]
    c = background(lv, t)
    style, h = sc["style"], sc["hit"]
    if style == "versus":
        d = ImageDraw.Draw(c)
        d.rectangle((0, 330, W, 1000), fill=lerp(lv["bg"], acc, 0.85))
    paste(c, pill_layer(f"ACTIC · NIVEL {lv['name']}", font("Bold", 40), WHITE, acc), W / 2, 150)
    level_bars(c, lv, W / 2, 235)
    k1 = ease_out(t / 0.3)
    pop1 = ease_back(t / 0.4)
    k2 = ease_back((t - h) / 0.35)
    shake = math.sin(t * 60) * 10 * (1 - clamp((t - h) / 0.4)) if t > h else 0
    big, mid = font("ExtraBold", 118), G["big"]

    def lines(items, y0, fnt, col, k, step=None, dx=0.0):
        step = step or fnt.size * 1.18
        for j, ln in enumerate(items):
            text(c, ln, fnt, col, W / 2 + dx, y0 + j * step, clamp(k * 2), 1.4 - 0.4 * clamp(k))

    def remate(items, y0, col=acc, fnt=big):
        if k2 > 0:
            lines(items, y0, fnt, col, k2, dx=shake)

    if style == "classic":
        for j, ln in enumerate(["Si no sabes", "responder esta", "pregunta…"]):
            k = ease_out((t - j * 0.12) / 0.3)
            text(c, ln, mid, INK, W / 2, 640 + j * 112 + (1 - k) * 40, k)
        remate(["NO APROBARÁS", "EL ACTIC"], 1060)
    elif style == "timer":
        text(c, "TIENES", mid, INK, W / 2, 520, k1)
        rem = max(0.0, 3 * (1 - t / max(sc["dh"], 0.1)))
        ring = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
        dd = ImageDraw.Draw(ring)
        dd.ellipse((10, 10, 410, 410), fill=WHITE)
        dd.arc((10, 10, 410, 410), -90, -90 + 360 * rem / 3, fill=acc, width=28)
        ctext(dd, str(max(1, math.ceil(rem))), font("ExtraBold", 190), INK, 210, 200)
        paste(c, ring, W / 2, 840, k1, 0.7 + 0.3 * pop1)
        text(c, "SEGUNDOS", mid, INK, W / 2, 1150, k1)
        remate(["¿LA SABES?"], 1330)
    elif style == "pov":
        paste(c, pill_layer("POV", font("ExtraBold", 80), WHITE, INK, 50, 20), W / 2, 560, k1, 0.7 + 0.3 * pop1)
        lines(["es tu examen", "ACTIC…"], 760, mid, INK, k1)
        remate(["…y te sale", "ESTO"], 1100)
    elif style == "fail":
        lines(["CASI TODO", "EL MUNDO"], 600, mid, INK, k1)
        remate(["FALLA ESTA", "PREGUNTA"], 900)
        if k2 > 0:
            xl = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
            dd = ImageDraw.Draw(xl)
            dd.ellipse((0, 0, 219, 219), fill=RED)
            cross(dd, 110, 110, 52, WHITE, 22)
            paste(c, xl, W / 2 + shake, 1300, clamp(k2 * 2), 0.6 + 0.4 * k2)
    elif style == "trap_a":
        text(c, "SI RESPONDES LA…", mid, INK, W / 2, 540, k1)
        circ = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
        dd = ImageDraw.Draw(circ)
        dd.ellipse((0, 0, 299, 299), fill=acc)
        ctext(dd, "A", font("ExtraBold", 170), WHITE, 150, 145)
        if t > h:
            cross(dd, 150, 150, 95, RED, 30)
        paste(c, circ, W / 2 + shake, 850, k1, 0.6 + 0.4 * pop1)
        remate(["HAS", "SUSPENDIDO"], 1150, RED)
    elif style == "challenge":
        stamp = text_layer("TE RETO", font("ExtraBold", 170), acc).rotate(7, expand=True, resample=Image.BICUBIC)
        paste(c, stamp, W / 2, 720, clamp(pop1 * 2), 1.6 - 0.6 * clamp(pop1))
        if k2 > 0:
            lines(["si aciertas esta,", "estás listo para"], 990, mid, INK, k2)
            text(c, f"EL NIVEL {lv['name']}", big, acc, W / 2 + shake, 1260, clamp(k2 * 2), 1.4 - 0.4 * k2)
    elif style == "trap":
        w = Image.new("RGBA", (320, 290), (0, 0, 0, 0))
        dd = ImageDraw.Draw(w)
        dd.polygon([(160, 0), (320, 280), (0, 280)], fill=RED)
        ctext(dd, "!", font("ExtraBold", 180), WHITE, 160, 175)
        paste(c, w, W / 2, 680, clamp(pop1 * 2), 0.6 + 0.4 * pop1)
        text(c, "¡CUIDADO!", big, RED, W / 2, 930, k1)
        if k2 > 0:
            text(c, "esta pregunta", mid, INK, W / 2, 1110, clamp(k2 * 2))
        remate(["TIENE TRAMPA"], 1250)
    elif style == "versus":
        kl = ease_out(t / 0.35)
        text(c, "¿FILTRAR?", font("ExtraBold", 130), WHITE, W / 2 - (1 - kl) * 600, 660, kl)
        kr = ease_out((t - 0.25) / 0.35)
        text(c, "¿ORDENAR?", font("ExtraBold", 130), INK, W / 2 + (1 - kr) * 600, 1340, kr)
        vs = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        dd = ImageDraw.Draw(vs)
        dd.ellipse((0, 0, 199, 199), fill=INK)
        ctext(dd, "VS", font("ExtraBold", 80), WHITE, 100, 96)
        paste(c, vs, W / 2, 1000, clamp(ease_back((t - 0.4) / 0.4) * 2), 0.6 + 0.4 * ease_back((t - 0.4) / 0.4))
        if k2 > 0:
            text(c, "mucha gente los confunde", font("Bold", 64), INK, W / 2 + shake, 1520, clamp(k2 * 2))
    elif style == "nota":
        circ = Image.new("RGBA", (380, 380), (0, 0, 0, 0))
        dd = ImageDraw.Draw(circ)
        dd.ellipse((0, 0, 379, 379), fill=WHITE, outline=acc, width=26)
        ctext(dd, "10", font("ExtraBold", 190), acc, 190, 180)
        text(c, "SOLO PARA LOS QUE", font("Bold", 64), INK, W / 2, 520, k1)
        paste(c, circ, W / 2, 820, k1, 0.6 + 0.4 * pop1)
        remate(["VAN A", "POR NOTA"], 1130)
    elif style == "comment":
        bub = Image.new("RGBA", (780, 400), (0, 0, 0, 0))
        dd = ImageDraw.Draw(bub)
        dd.rounded_rectangle((0, 0, 779, 320), radius=60, fill=INK)
        dd.polygon([(160, 310), (260, 310), (150, 395)], fill=INK)
        ctext(dd, "COMENTA TU", font("ExtraBold", 100), WHITE, 390, 105)
        ctext(dd, "RESPUESTA", font("ExtraBold", 100), acc if acc != INK else WHITE, 390, 215)
        paste(c, bub, W / 2, 760, clamp(pop1 * 2), 0.6 + 0.4 * pop1)
        if k2 > 0:
            text(c, "antes de que salga", mid, INK, W / 2, 1060, clamp(k2 * 2))
        remate(["LA SOLUCIÓN"], 1190)
        if k2 > 0:
            bounce = abs(math.sin(t * 6)) * 30
            dd2 = ImageDraw.Draw(c)
            ax, ay = W / 2, 1340 + bounce
            dd2.polygon([(ax - 50, ay), (ax + 50, ay), (ax, ay + 60)], fill=acc)
    return c


def frame(lv, item, sc, t):
    c = question_frame(lv, item, sc, t)
    if sc["off"] and t < sc["off"] + 0.3:
        mix = ease_out((t - sc["off"]) / 0.3)
        c = Image.blend(hook_frame(lv, sc, t).convert("RGB"), c, mix)
    return c


def question_frame(lv, item, sc, t):
    acc = lv["accent"]
    c = background(lv, t)
    paste(c, pill_layer(f"ACTIC · NIVEL {lv['name']}", font("Bold", 40), WHITE, acc), W / 2, 150)
    level_bars(c, lv, W / 2, 235)
    # la pregunta está completa en cuanto se ve (sin animación de entrada)
    lines = wrap(item["q"], G["q"], 960)
    fq, lh = G["q"], 74
    if len(lines) > 3:
        fq, lh = font("Bold", 52), 66
        lines = wrap(item["q"], fq, 980)
    y0 = 340
    for j, ln in enumerate(lines):
        text(c, ln, fq, INK, W / 2, y0 + j * lh)
    art_y = y0 + 30 + len(lines) * lh + CARD_H / 2
    reveal = ease_out((t - sc["rv"]) / 0.35)
    paste(c, art_card(lv, item["art"], reveal), W / 2, art_y)
    opt_y0 = art_y + CARD_H / 2 + 90
    for j, s in enumerate(item["opts"]):
        ap = ease_out((t - (sc["off"] + 0.3 + j * 0.12)) / 0.25)
        if ap <= 0:
            continue
        ok = j == item["ok"]
        layer, alpha = option_layer(lv, "ABCD"[j], s, ap, reveal, ok)
        bump = 1 + 0.05 * math.sin(math.pi * clamp((t - sc["rv"]) / 0.4)) if ok else 1
        paste(c, layer, W / 2 + (1 - ap) * 80, opt_y0 + j * 122, alpha, bump)
    wy = opt_y0 + 4 * 122 + 50
    # cuenta atrás
    if sc["cd"] <= t < sc["rv"] + 0.3:
        rem = sc["rv"] - t
        fa = ease_out((t - sc["cd"]) / 0.25) * (1 - ease_out((t - sc["rv"]) / 0.25))
        ring = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
        d = ImageDraw.Draw(ring)
        d.ellipse((5, 5, 145, 145), fill=WHITE)
        if rem > 0:
            d.arc((5, 5, 145, 145), -90, -90 + 360 * clamp(rem / 3.0), fill=acc, width=12)
        ctext(d, str(max(1, math.ceil(rem))), G["num"], INK, 75, 72)
        paste(c, ring, W / 2, wy, fa, 1 + 0.08 * ease_out(((rem % 1.0) - 0.8) / 0.2))
    # subtítulos de la explicación
    for s0, s1, chunk in sc["caps"]:
        if s0 <= t < s1 + 0.15:
            k = ease_back((t - s0) / 0.2)
            box = caption_layer(chunk, acc)
            paste(c, box, W / 2, wy + 20, clamp(k * 2), 0.9 + 0.1 * k)
    # cierre
    end_k = ease_back((t - (sc["caps"][-1][1] + 0.2)) / 0.45)
    if end_k > 0:
        paste(c, pill_layer("Síguenos para más", G["btn"], WHITE, acc, 60, 26), W / 2, wy - 10,
              clamp(end_k * 2), 0.7 + 0.3 * end_k)
        text(c, HANDLE, font("SemiBold", 40), INK, W / 2, wy + 85, clamp(end_k * 2))
    return c.convert("RGB")


def caption_layer(s, acc):
    lines = wrap(s, CAP_FONT, CAP_W)
    lh = 62
    h = len(lines) * lh + 36
    img = Image.new("RGBA", (CAP_W + 80, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, CAP_W + 79, h - 1), radius=30, fill=INK + (235,))
    for j, ln in enumerate(lines):
        ctext(d, ln, CAP_FONT, WHITE, (CAP_W + 80) / 2, 18 + lh / 2 + j * lh)
    return img


# --- música de fondo -------------------------------------------------------------

def music(dur, seed=3):
    """Base suave a 100 BPM: acordes de pad, bajo, bombo y charles."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    beat = 60 / 100
    bar = 4 * beat
    chords = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (261.6, 329.6, 392.0), (196.0, 246.9, 293.7)]
    pad = np.zeros(n)
    bass = np.zeros(n)
    for b in range(int(dur / bar) + 1):
        s, e = int(b * bar * SR), min(n, int((b + 1) * bar * SR))
        if s >= n:
            break
        tt = t[s:e] - b * bar
        env = np.clip(tt / 0.4, 0, 1) * np.clip((bar - tt) / 0.3, 0, 1)
        for f in chords[b % 4]:
            pad[s:e] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt + 0.5)) * env
        f0 = chords[b % 4][0] / 2
        bass[s:e] += np.sin(2 * np.pi * f0 * tt) * env
    drums = np.zeros(n)
    kn = int(0.25 * SR)
    kt = np.arange(kn) / SR
    kick = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-kt * 30)) / SR) * np.exp(-kt * 12)
    hn = int(0.05 * SR)
    hat_noise = rng.standard_normal(hn)
    hat = (hat_noise - lowpass(hat_noise, 4000)) * np.exp(-np.arange(hn) / SR * 80)
    for k in range(int(dur / beat) + 1):
        s = int(k * beat * SR)
        if k % 2 == 0 and s < n:
            drums[s:s + kn] += kick[: n - s] * 0.9
        s2 = int((k + 0.5) * beat * SR)
        if s2 < n:
            drums[s2:s2 + hn] += hat[: n - s2] * 0.35
    mix = pad / 6 + bass * 0.35 + drums * 0.5
    fade = np.clip(t / 0.3, 0, 1) * np.clip((dur - t) / 1.0, 0, 1)
    return mix * fade / np.max(np.abs(mix))


def buzzer(dur=0.35):
    """Zumbido de "respuesta incorrecta"."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = np.sign(np.sin(2 * np.pi * 140 * t)) + 0.5 * np.sign(np.sin(2 * np.pi * 147 * t))
    return lowpass(tone, 1800) * np.clip(t / 0.01, 0, 1) * np.exp(-t * 4) * 0.35


def audio(lv, sc):
    n = int(sc["end"] * SR) + SR
    voice = np.zeros(n)
    for t0, clip in ((0.15, sc["hk"]), (sc["vq"], sc["qa"]), (sc["va"], sc["aa"])):
        s = int(t0 * SR)
        voice[s:s + len(clip)] += clip
    off = sc["off"]
    ev = [(off, pop(700, 300, 0.1), 0.6)]
    if off:
        ev += [(sc["hit"], pop(520, 140, 0.15), 1.0), (sc["hit"], whoosh(0.3), 0.5),
               (off - 0.15, whoosh(), 0.6)]
        if sc["style"] in ("trap_a", "fail", "trap"):
            ev.append((sc["hit"], buzzer(), 0.7))
        if sc["style"] == "timer":
            for s in range(3):
                ev.append((s * sc["dh"] / 3, tick(1900), 1.0))
    for j in range(4):
        ev.append((off + 0.3 + j * 0.12, click(), 0.6))
    for s in range(3):
        ev.append((sc["cd"] + s, tick(1900), 1.0))
        ev.append((sc["cd"] + s + 0.5, tick(1250), 0.5))
    ev += [(sc["rv"] - 0.6, riser(), 0.8), (sc["rv"], chime(), 1.0),
           (sc["caps"][-1][1] + 0.2, whoosh(), 0.5), (sc["caps"][-1][1] + 0.35, pop(), 0.8)]
    fx = np.zeros(n)
    for t0, snd, gain in ev:
        s = int(t0 * SR)
        fx[s:s + len(snd)] += snd[: n - s] * gain
    fx *= 0.6 / np.max(np.abs(fx))
    bed = np.zeros(n)
    m = music(sc["end"])
    bed[: len(m)] = m * 0.22
    out = voice + (fx + bed) * duck(voice, depth=0.6)
    out = out[: int(sc["end"] * SR)]
    out *= 0.9 / np.max(np.abs(out))
    return np.stack([out, out], axis=1)


def render(key, i):
    lv = LEVELS[key]
    item = QUIZ[key][i]
    sc = build(key, i)
    sc["qa"], sc["aa"] = sc.pop("q"), sc.pop("a")
    name = f"actic_{key}_{i + 1}"
    wav = DST / f"{name}.wav"
    write_wav(wav, audio(lv, sc))
    cover_t = sc["hit"] + 0.6 if sc["off"] else sc["rv"] + 1.0
    frame(lv, item, sc, cover_t).save(DST / f"portada_{name}.png")
    path = DST / f"{name}.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(path)],
        stdin=subprocess.PIPE)
    for f in range(int(sc["end"] * FPS)):
        proc.stdin.write(frame(lv, item, sc, f / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    wav.unlink()
    print("ok", path, f"{sc['end']:.1f}s")


if __name__ == "__main__":
    DST.mkdir(parents=True, exist_ok=True)
    # argumentos: "basico" (todas sus preguntas) o "basico:4" (solo la pregunta 4)
    for arg in sys.argv[1:] or list(QUIZ):
        key, _, num = arg.partition(":")
        for i in [int(num) - 1] if num else range(len(QUIZ[key])):
            render(key, i)
