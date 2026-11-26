"""Reels de promoción con personajes (Casi y Marta) y diálogo con voz.

Uso: python3 promo.py [1 5]  → salida/promo/promo_{n}.mp4 + portada
Voces en salida/quiz_voz/promo{n}_{m|c}{k}.mp3: m = Marta (voz Gala), c = Casi (voz Pablo).
La boca de cada personaje se mueve con el volumen de su propia voz; los bocadillos son los subtítulos.
"""
import math
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

from corto import buzzer, music
from personajes import GREEN, LINE, RED, bocadillo, casi, marta
from sfx import SR, chime, click, pop, riser, whoosh, write_wav
from teaser import FPS, H, INK, LEVELS, OUT, W, WHITE, background, clamp, ease_back, ease_out, font, paste, text
from voz import decode, duck

VOZ = OUT / "quiz_voz"
DST = OUT / "promo"
HANDLE = "@acticdesdecasa"
F_TITLE = font("ExtraBold", 66)
F_BUB = font("Bold", 46)
F_BADGE = font("Bold", 44)
F_CARD = font("Bold", 46)
F_OPT = font("Bold", 48)
F_BIG = font("ExtraBold", 110)
F_SMALL = font("Bold", 40)

MX, MY, MS = 330, 1450, 560  # Marta: centro y tamaño
CX, CY, CS = 805, 1478, 400  # Casi

# Guiones. Cada línea: (quién, archivo, texto del bocadillo, estado de los personajes durante la línea).
REELS = {
    1: dict(
        lv="basico", title="POV: el ACTIC es mañana",
        lines=[
            ("m", "promo1_m1", "¡Socorro! ¡El ACTIC es mañana y no he estudiado nada!",
             dict(m=dict(mood="worried", sweat=1), shake=1.0)),
            ("c", "promo1_c1", "Tranquila. En actic desde casa tienes tests tipo examen de los tres niveles, y cada "
                               "pregunta te explica la respuesta.",
             dict(m=dict(mood="wow"), c=dict(mood="smile", arms="wave"), enter=True,
                  badges=["Tests tipo examen", "3 niveles", "Cada respuesta explicada"])),
            ("m", "promo1_m2", "¿Y si me equivoco?", dict(m=dict(mood="worried"), c=dict(mood="smile"))),
            ("c", "promo1_c2", "Repasas tus fallos y haces un simulacro con cronómetro. Todo desde el móvil.",
             dict(m=dict(mood="smile", phone=True, look=(1, -0.5)), c=dict(mood="smile", arms="point"),
                  badges=["Repaso de fallos", "Simulacro con cronómetro", "Desde el móvil"])),
            ("m", "promo1_m3", "¡Aprobado! ¡No me lo creo!",
             dict(m=dict(mood="grin", arm_up=True), c=dict(mood="grin", arms="up"), card="Al día siguiente…",
                  stamp="¡APROBADO!", confetti=True)),
            ("c", "promo1_c3", "Haz el test gratis. Tienes el enlace en la bio.",
             dict(m=dict(mood="grin"), c=dict(mood="smile", arms="wave"), end=True)),
        ]),
    5: dict(
        lv="medio", title="El error que suspende a todos",
        question="¿Qué tecla mantienes pulsada para seleccionar varios archivos sueltos?",
        opts=["Mayús", "Ctrl", "Alt"], wrong=0, right=1,
        lines=[
            ("m", "promo5_m1", "Esta me la sé. Para seleccionar archivos sueltos… ¡mayúsculas, fijo!",
             dict(m=dict(mood="smile", look=(0.6, -1)), pick_at=0.72)),
            ("c", "promo5_c1", "¡Error! Con Mayús seleccionas todo lo que hay entre medio. Para archivos sueltos se "
                               "usa Ctrl.",
             dict(m=dict(mood="wow"), c=dict(mood="worried", arms="point"), enter=True, buzz=True, right_at=0.85)),
            ("m", "promo5_m2", "¿En serio? ¿Y cuántas trampas así hay en el examen?",
             dict(m=dict(mood="wow", sweat=1), c=dict(mood="smile"))),
            ("c", "promo5_c2", "Muchas. Por eso en actic desde casa cada pregunta te explica el porqué. Haz el test "
                               "gratis: enlace en la bio.",
             dict(m=dict(mood="smile"), c=dict(mood="smile", arms="wave"), end_at=0.55)),
        ]),
}

GAP = 0.3
ENTER = 0.6   # tiempo para que aparezca Casi antes de hablar
CARD = 1.2    # cartela de transición
BUZZ = 0.6
TAIL = 1.4


def build(n):
    r = REELS[n]
    t = 0.35
    beats = []
    for who, f, txt, st in r["lines"]:
        clip = decode(VOZ / f"{f}.mp3")
        if st.get("card"):
            st["card_t"] = t
            t += CARD
        if st.get("buzz"):
            st["buzz_t"] = t - GAP + 0.05
            t += BUZZ
        if st.get("enter"):
            st["enter_t"] = t
            t += ENTER
        dur = len(clip) / SR
        beats.append(dict(who=who, clip=clip, text=txt, st=st, start=t, end=t + dur))
        t += dur + GAP
    end = t - GAP + TAIL
    # envolvente de volumen por personaje y fotograma (para mover la boca)
    nf = int(end * FPS) + 2
    env = {"m": np.zeros(nf), "c": np.zeros(nf)}
    hop = SR // FPS
    for b in beats:
        c = b["clip"]
        rms = np.array([np.sqrt(np.mean(c[i:i + hop] ** 2)) for i in range(0, len(c), hop)])
        rms = rms / (np.percentile(rms, 95) + 1e-9)
        f0 = int(b["start"] * FPS)
        e = env[b["who"]]
        e[f0:f0 + len(rms)] = np.clip(rms[: len(e) - f0], 0, 1)
    for k in env:  # suavizado ligero
        env[k] = np.convolve(env[k], [0.25, 0.5, 0.25], mode="same")
    casi_in = next((b["st"]["enter_t"] for b in beats if b["st"].get("enter")), 0)
    return dict(r=r, beats=beats, end=end, env=env, casi_in=casi_in, lv=LEVELS[r["lv"]])


def current(sc, t):
    """Índice de la línea vigente (la última que ha empezado, contando su preparación)."""
    idx = 0
    for i, b in enumerate(sc["beats"]):
        pre = b["st"].get("card_t", b["st"].get("buzz_t", b["st"].get("enter_t", b["start"])))
        if t >= pre:
            idx = i
    return idx


def state(sc, who, t):
    """Estado del personaje: el de la última línea vigente que lo define."""
    st = {}
    for b in sc["beats"][: current(sc, t) + 1]:
        st = b["st"].get(who, st)
    return dict(st)


def blink(t, off):
    p = (t + off) % 3.3
    return clamp(1 - abs(p - 0.08) / 0.08) if p < 0.16 else 0.0


def badge_layer(s, acc):
    tl_w = int(F_BADGE.getlength(s))
    w, h = tl_w + 120, 92
    img = Image.new("RGBA", (w + 6, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((3, 8, w + 3, h + 8), radius=46, fill=(0, 0, 0, 40))
    d.rounded_rectangle((0, 0, w, h), radius=46, fill=WHITE, outline=LINE, width=4)
    d.ellipse((24, 24, 68, 68), fill=acc)
    d.line((35, 46, 44, 56, 58, 36), fill=WHITE, width=7, joint="curve")
    d.text((90, h / 2 - 27), s, font=F_BADGE, fill=INK)
    return img


def title_layer(s, acc):
    tw = int(F_TITLE.getlength(s))
    w, h = tw + 90, 120
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=60, fill=INK)
    d.text((45, 18), s, font=F_TITLE, fill=WHITE)
    return img


def stamp_layer(s, col):
    tw = int(F_BIG.getlength(s))
    w, h = tw + 80, 170
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, w - 6, h - 6), radius=30, outline=col, width=12)
    d.text((40, 18), s, font=F_BIG, fill=col)
    return img.rotate(8, expand=True, resample=Image.BICUBIC)


def question_layer(r, picked, wrong_k, right_k):
    cw = 980
    from corto import wrap
    lines = wrap(r["question"], F_CARD, cw - 90)
    oh = 88
    ch = 50 + len(lines) * 58 + 24 + len(r["opts"]) * (oh + 14) + 16
    img = Image.new("RGBA", (cw + 8, ch + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 10, cw + 4, ch + 10), radius=44, fill=(0, 0, 0, 40))
    d.rounded_rectangle((0, 0, cw, ch), radius=44, fill=WHITE, outline=LINE, width=4)
    for j, ln in enumerate(lines):
        d.text(((cw - F_CARD.getlength(ln)) / 2, 36 + j * 58), ln, font=F_CARD, fill=INK)
    y = 50 + len(lines) * 58 + 16
    blue = LEVELS["medio"]["accent"]
    for i, o in enumerate(r["opts"]):
        fill, fg, mark = (243, 241, 236), INK, None
        if i == r["wrong"] and wrong_k > 0:
            fill, fg, mark = RED, WHITE, "x"
        elif i == r["wrong"] and picked:
            fill, fg = blue, WHITE
        if i == r["right"] and right_k > 0:
            fill, fg, mark = GREEN, WHITE, "ok"
        d.rounded_rectangle((40, y, cw - 40, y + oh), radius=30, fill=fill, outline=LINE, width=3)
        d.text((80, y + 16), f"{'ABC'[i]})  {o}", font=F_OPT, fill=fg)
        if mark == "x":
            d.line((cw - 120, y + 22, cw - 76, y + 66), fill=WHITE, width=10)
            d.line((cw - 76, y + 22, cw - 120, y + 66), fill=WHITE, width=10)
        elif mark == "ok":
            d.line((cw - 124, y + 46, cw - 104, y + 66, cw - 70, y + 24), fill=WHITE, width=10, joint="curve")
        y += oh + 14
    return img


def end_layer(lv):
    w, h = 900, 560
    img = Image.new("RGBA", (w + 8, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 10, w + 4, h + 10), radius=50, fill=(0, 0, 0, 45))
    d.rounded_rectangle((0, 0, w, h), radius=50, fill=WHITE, outline=LINE, width=4)
    logo = Image.open(OUT / "logo" / "logo_check.png").convert("RGBA")
    logo.thumbnail((150, 150))
    img.alpha_composite(logo, ((w - logo.width) // 2, 40))
    f1 = font("ExtraBold", 64)
    s1 = "actic"
    s2 = "desdecasa"
    x0 = (w - f1.getlength(s1 + s2)) / 2
    d.text((x0, 210), s1, font=f1, fill=INK)
    d.text((x0 + f1.getlength(s1), 210), s2, font=f1, fill=GREEN)
    btn = "Haz el test gratis"
    fb = font("Bold", 54)
    bw = fb.getlength(btn) + 100
    d.rounded_rectangle(((w - bw) / 2, 330, (w + bw) / 2, 430), radius=50, fill=lv["accent"])
    d.text(((w - fb.getlength(btn)) / 2, 350), btn, font=fb, fill=WHITE)
    s3 = "Enlace en la bio  ·  sin registro"
    d.text(((w - F_SMALL.getlength(s3)) / 2, 465), s3, font=F_SMALL, fill=(110, 118, 122))
    return img


CONFETTI = [(random.Random(i).uniform(0, W), random.Random(i * 7).uniform(-400, 0), random.Random(i * 3).choice(
    [GREEN, RED, (46, 94, 145), (240, 190, 60)]), random.Random(i * 5).uniform(0.7, 1.3)) for i in range(70)]


def frame(sc, t):
    r, lv, beats = sc["r"], sc["lv"], sc["beats"]
    i = current(sc, t)
    b = beats[i]
    st = b["st"]
    f = background(lv, t)
    d = ImageDraw.Draw(f)
    fi = min(int(t * FPS), len(sc["env"]["m"]) - 1)

    # título fijo arriba
    tl = title_layer(r["title"], lv["accent"])
    k = ease_back((t - 0.1) / 0.5)
    paste(f, tl, W / 2, 200, alpha=clamp(k), scale=0.6 + 0.4 * k)

    # mesa
    d.rounded_rectangle((-40, 1700, W + 40, 1780), radius=20, fill=(196, 160, 120), outline=LINE, width=5)
    d.rectangle((0, 1780, W, H), fill=(170, 136, 100))

    # --- accesorios por reel ---
    if "question" in r:
        q = beats[0]
        pick_t = q["start"] + (q["end"] - q["start"]) * q["st"]["pick_at"]
        b1 = beats[1]
        right_t = b1["start"] + (b1["end"] - b1["start"]) * b1["st"]["right_at"]
        last = beats[-1]
        out_t = last["start"] + (last["end"] - last["start"]) * last["st"]["end_at"]
        a = clamp((t - 0.3) / 0.4) * (1 - clamp((t - out_t) / 0.35))
        if a > 0:
            ql = question_layer(r, t >= pick_t, t >= b1["st"]["buzz_t"], t >= right_t)
            paste(f, ql, W / 2, 565, alpha=a, scale=0.85 + 0.15 * ease_back((t - 0.3) / 0.5))
        if t >= out_t:
            k = ease_back((t - out_t - 0.2) / 0.5)
            paste(f, end_layer(lv), W / 2, 580, alpha=clamp(k), scale=0.7 + 0.3 * k)
    else:
        # calendario mientras Marta se agobia
        a = 1 - clamp((t - beats[1]["start"]) / 0.4)
        if a > 0:
            cal = Image.new("RGBA", (340, 320), (0, 0, 0, 0))
            cd = ImageDraw.Draw(cal)
            cd.rounded_rectangle((4, 4, 334, 314), radius=26, fill=WHITE, outline=LINE, width=5)
            cd.rounded_rectangle((4, 4, 334, 94), radius=26, fill=RED, outline=LINE, width=5)
            cd.rectangle((9, 64, 329, 92), fill=RED)
            cd.text((169 - font("ExtraBold", 48).getlength("ACTIC") / 2, 22), "ACTIC", font=font("ExtraBold", 48),
                    fill=WHITE)
            cd.text((169 - font("ExtraBold", 56).getlength("MAÑANA") / 2, 170), "MAÑANA",
                    font=font("ExtraBold", 56), fill=RED)
            wob = math.sin(t * 9) * 4 * clamp(1.5 - t)
            paste(f, cal.rotate(-6 + wob, expand=True, resample=Image.BICUBIC), 230, 520, alpha=a)
        # chapas de características
        for bb in beats:
            if not bb["st"].get("badges"):
                continue
            dur = bb["end"] - bb["start"]
            for j, s in enumerate(bb["st"]["badges"]):
                t0 = bb["start"] + dur * (0.15 + j * 0.25)
                k = ease_back((t - t0) / 0.4)
                a = clamp((t - t0) / 0.2) * (1 - clamp((t - bb["end"] - 0.15) / 0.3))
                if a > 0:
                    paste(f, badge_layer(s, lv["accent"]), W / 2, 420 + j * 115, alpha=a, scale=0.6 + 0.4 * k)
        # sello de aprobado y cartel final
        for bb in beats:
            if bb["st"].get("stamp") and t >= bb["start"]:
                k = ease_back((t - bb["start"] - 0.1) / 0.35)
                a = clamp((t - bb["start"]) / 0.15) * (1 - clamp((t - bb["end"] - 0.2) / 0.3))
                paste(f, stamp_layer(bb["st"]["stamp"], GREEN), W / 2, 520, alpha=a, scale=1.8 - 0.8 * k)
            if bb["st"].get("end") and t >= bb["start"] - 0.1:
                k = ease_back((t - bb["start"] + 0.1) / 0.5)
                paste(f, end_layer(lv), W / 2, 580, alpha=clamp(k), scale=0.7 + 0.3 * k)

    # --- personajes ---
    ms = state(sc, "m", t)
    shake = 0
    if st.get("shake") and t < b["start"] + st["shake"]:
        shake = math.sin(t * 60) * 8
    if "buzz_t" in st and st["buzz_t"] <= t < st["buzz_t"] + 0.4:
        shake = math.sin(t * 70) * 12
    talk_m = sc["env"]["m"][fi]
    bob_m = math.sin(t * 2.2) * 6 + talk_m * 8
    mouth_m = clamp(talk_m * 1.4) if talk_m > 0.12 else 0.0
    paste(f, marta(MS, mouth=mouth_m, blink=blink(t, 0.4), **ms), MX + shake, MY - bob_m)

    if t >= sc["casi_in"] - 0.01 and sc["casi_in"]:
        cs = state(sc, "c", t)
        k = ease_back((t - sc["casi_in"]) / 0.45)
        talk_c = sc["env"]["c"][fi]
        hop = abs(math.sin(t * 6)) * 18 if cs.get("arms") == "up" else math.sin(t * 2.6 + 1) * 5
        squash = -0.5 * math.sin(t * 12) if cs.get("arms") == "up" else talk_c * -0.15
        mouth_c = clamp(talk_c * 1.4) if talk_c > 0.12 else 0.0
        layer = casi(CS, mouth=mouth_c, blink=blink(t, 1.7), squash=squash, **cs)
        # nube al aparecer
        puff = clamp(1 - (t - sc["casi_in"]) / 0.5)
        if puff > 0:
            for j in range(7):
                ang = j / 7 * math.tau
                rr = 120 + 120 * (1 - puff)
                px, py = CX + math.cos(ang) * rr, CY + math.sin(ang) * rr * 0.6
                d.ellipse((px - 40 * puff, py - 40 * puff, px + 40 * puff, py + 40 * puff), fill=(255, 255, 255))
        paste(f, layer, CX, CY - hop, alpha=clamp(k * 2), scale=max(0.05, k))

    # mesa delante (tapa el cuerpo de Marta)
    d = ImageDraw.Draw(f)
    d.rounded_rectangle((-40, 1700, W + 40, 1780), radius=20, fill=(196, 160, 120), outline=LINE, width=5)
    d.rectangle((0, 1780, W, H), fill=(170, 136, 100))
    text(f, HANDLE, font("Bold", 40), WHITE, W / 2, 1850)

    # bocadillo de la línea actual
    for bb in beats:
        if bb["start"] - 0.05 <= t <= bb["end"] + 0.3:
            k = ease_back((t - bb["start"] + 0.05) / 0.3)
            a = clamp((t - bb["start"] + 0.05) / 0.15) * (1 - clamp((t - bb["end"] - 0.1) / 0.2))
            m = bb["who"] == "m"
            bl = bocadillo(bb["text"], F_BUB, 640 if m else 700, tail="left" if m else "right")
            top_of = 1110 if m else 1235
            cx = 480 if m else 600
            paste(f, bl, cx, top_of - bl.height / 2, alpha=a, scale=0.7 + 0.3 * k)

    # cartela de transición
    for bb in beats:
        c0 = bb["st"].get("card_t")
        if c0 is not None and c0 <= t < c0 + CARD:
            x = (t - c0) / CARD
            k = ease_out(x / 0.3) - ease_out((x - 0.75) / 0.25)
            ov = Image.new("RGBA", (W, H), lv["accent"] + (int(255 * clamp(k)),))
            f.alpha_composite(ov)
            text(f, bb["st"]["card"], font("ExtraBold", 90), WHITE, W / 2, H / 2, alpha=clamp(k))

    # confeti
    for bb in beats:
        if bb["st"].get("confetti") and t >= bb["start"]:
            dt = t - bb["start"]
            d = ImageDraw.Draw(f)
            for x, y, col, sp in CONFETTI:
                yy = y + dt * 700 * sp
                xx = x + math.sin(dt * 4 * sp + x) * 40
                if yy < H:
                    a = dt * 5 * sp
                    d.polygon([(xx + math.cos(a) * 14, yy + math.sin(a) * 8), (xx - math.sin(a) * 8, yy + math.cos(a) * 14),
                               (xx - math.cos(a) * 14, yy - math.sin(a) * 8), (xx + math.sin(a) * 8, yy - math.cos(a) * 14)],
                              fill=col)
    return f.convert("RGB")


def audio(sc):
    n = int(sc["end"] * SR) + SR
    voice = np.zeros(n)
    ev = [(0.1, whoosh(0.35), 0.5), (0.15, pop(700, 300, 0.1), 0.6)]
    for b in sc["beats"]:
        s = int(b["start"] * SR)
        voice[s:s + len(b["clip"])] += b["clip"]
        st = b["st"]
        ev.append((b["start"] - 0.05, click(), 0.5))
        if "enter_t" in st:
            ev += [(st["enter_t"] - 0.1, whoosh(), 0.6), (st["enter_t"] + 0.05, pop(520, 140, 0.15), 1.0)]
        if "buzz_t" in st:
            ev.append((st["buzz_t"], buzzer(), 0.8))
        if "card_t" in st:
            ev += [(st["card_t"], whoosh(0.5), 0.7), (b["start"] - 0.6, riser(), 0.8)]
        if st.get("stamp"):
            ev += [(b["start"] + 0.1, pop(400, 120, 0.2), 1.0), (b["start"] + 0.15, chime(), 1.0)]
        if st.get("badges"):
            dur = b["end"] - b["start"]
            for j in range(len(st["badges"])):
                ev.append((b["start"] + dur * (0.15 + j * 0.25), pop(900, 400, 0.08), 0.5))
        if st.get("end") or st.get("end_at"):
            t0 = b["start"] + (b["end"] - b["start"]) * st.get("end_at", 0)
            ev += [(t0, whoosh(0.4), 0.5), (t0 + 0.2, chime((1046.5, 1568)), 0.8)]
    r = sc["r"]
    if "question" in r:
        q = sc["beats"][0]
        ev.append((q["start"] + (q["end"] - q["start"]) * q["st"]["pick_at"], click(), 1.0))
        b1 = sc["beats"][1]
        ev.append((b1["start"] + (b1["end"] - b1["start"]) * b1["st"]["right_at"], chime(), 0.9))
    fx = np.zeros(n)
    for t0, snd, gain in ev:
        s = max(0, int(t0 * SR))
        fx[s:s + len(snd)] += snd[: n - s] * gain
    fx *= 0.6 / np.max(np.abs(fx))
    bed = np.zeros(n)
    m = music(sc["end"], seed=7)
    bed[: len(m)] = m * 0.24
    out = voice + (fx + bed) * duck(voice, depth=0.6)
    out = out[: int(sc["end"] * SR)]
    out *= 0.9 / np.max(np.abs(out))
    return np.stack([out, out], axis=1)


def render(n, preview=False):
    sc = build(n)
    DST.mkdir(parents=True, exist_ok=True)
    name = f"promo_{n}"
    if preview:
        for j, b in enumerate(sc["beats"]):
            frame(sc, (b["start"] + b["end"]) / 2).save(DST / f"{name}_f{j}.png")
        return
    frame(sc, sc["beats"][0]["start"] + 1.2).save(DST / f"portada_{name}.png")
    wav = DST / f"{name}.wav"
    write_wav(wav, audio(sc))
    path = DST / f"{name}.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
         "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-ar", "44100", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(path)],
        stdin=subprocess.PIPE)
    for k in range(int(sc["end"] * FPS)):
        proc.stdin.write(frame(sc, k / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    wav.unlink()
    print("ok", path, f"{sc['end']:.1f}s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--preview"]
    for a in args or REELS:
        render(int(a), preview="--preview" in sys.argv)
