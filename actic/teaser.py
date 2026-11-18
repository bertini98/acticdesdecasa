"""Teaser ACTIC: genera un reel 1080x1920 por nivel + portada + vista de cuadrícula.

Uso: python3 teaser.py
"""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 10.0
OUT = Path(__file__).parent / "salida"
FONT_DIR = "/usr/share/fonts/opentype/inter/"

INK = (31, 41, 46)
WHITE = (255, 255, 255)

LEVELS = {
    "basico": dict(name="BÁSICO", chip="Nivel 1 de 3 · Fácil", n=1,
                   bg=(228, 242, 232), soft=(204, 230, 212), accent=(52, 128, 84)),
    "medio": dict(name="MEDIO", chip="Nivel 2 de 3 · Intermedio", n=2,
                  bg=(225, 236, 247), soft=(200, 218, 240), accent=(46, 94, 145)),
    "avanzado": dict(name="AVANZADO", chip="Nivel 3 de 3 · Difícil", n=3,
                     bg=(247, 228, 224), soft=(238, 203, 196), accent=(170, 74, 62)),
}


def font(weight, size):
    return ImageFont.truetype(f"{FONT_DIR}Inter-{weight}.otf", size)


F = {
    "pill": font("Bold", 40),
    "h1": font("Bold", 92),
    "h1x": font("ExtraBold", 150),
    "small": font("SemiBold", 54),
    "chip": font("SemiBold", 44),
    "body": font("Medium", 50),
    "opt": font("Bold", 42),
    "btn": font("Bold", 56),
}


# --- easing / tiempo -------------------------------------------------------

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c = 1.6
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def window(t, start, end, fade=0.35):
    """Opacidad de una escena: entra en `start`, sale en `end`."""
    return ease_out((t - start) / fade) * (1 - ease_out((t - (end - fade)) / fade))


def lerp(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


# --- dibujo ----------------------------------------------------------------

def text_layer(text, fnt, color):
    l, t, r, b = fnt.getbbox(text)
    img = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((2 - l, 2 - t), text, font=fnt, fill=color)
    return img


def paste(canvas, layer, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))),
                             Image.LANCZOS)
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def text(canvas, s, fnt, color, cx, cy, alpha=1.0, scale=1.0):
    paste(canvas, text_layer(s, fnt, color), cx, cy, alpha, scale)


def pill_layer(s, fnt, fg, bg, padx=34, pady=18):
    tl = text_layer(s, fnt, fg)
    w, h = tl.width + padx * 2, tl.height + pady * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg)
    img.alpha_composite(tl, (padx, pady))
    return img


def background(lv, t):
    img = Image.new("RGBA", (W, H), lv["bg"] + (255,))
    d = ImageDraw.Draw(img)
    # círculos suaves que se mueven lentamente
    for i, (bx, by, r) in enumerate([(160, 330, 300), (960, 1500, 380), (900, 260, 160)]):
        dx = math.sin(t * 0.5 + i * 2) * 30
        dy = math.cos(t * 0.4 + i) * 30
        d.ellipse((bx + dx - r, by + dy - r, bx + dx + r, by + dy + r), fill=lv["soft"])
    # trama de puntos muy sutil
    dot = lerp(lv["bg"], lv["soft"], 0.9)
    for y in range(60, H, 72):
        for x in range(60, W, 72):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=dot)
    return img


def level_bars(canvas, lv, cx, cy, fill_k=1.0, alpha=1.0):
    """Indicador 3 barras: rellena tantas como nivel."""
    layer = Image.new("RGBA", (3 * 90 + 2 * 18, 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(3):
        x = i * 108
        d.rounded_rectangle((x, 0, x + 90, 25), radius=13, fill=WHITE + (200,))
        k = clamp(fill_k * lv["n"] - i)
        if i < lv["n"] and k > 0:
            d.rounded_rectangle((x, 0, x + max(26, int(90 * k)), 25), radius=13, fill=lv["accent"])
    paste(canvas, layer, cx, cy, alpha)


def quiz_card(canvas, lv, t0, t, alpha):
    """Tarjeta de pregunta tipo test con 4 opciones; se marca la correcta."""
    cw, ch = 860, 700
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=48, fill=WHITE + (245,))
    # "pregunta" difuminada
    d.rounded_rectangle((60, 70, 800, 100), radius=15, fill=lv["soft"])
    d.rounded_rectangle((60, 125, 560, 155), radius=15, fill=lv["soft"])
    correct = 1
    reveal = ease_out((t - (t0 + 1.4)) / 0.3)
    for i, letter in enumerate("ABCD"):
        k = ease_out((t - (t0 + 0.25 + i * 0.15)) / 0.3)
        if k <= 0:
            continue
        y = 210 + i * 118
        row_bg = lerp(lv["bg"], lv["accent"], reveal) if i == correct else lv["bg"]
        d.rounded_rectangle((60, y, 800, y + 92), radius=28, fill=row_bg + (int(255 * k),))
        circ_bg = WHITE if (i == correct and reveal > 0.5) else lv["accent"]
        circ_fg = lv["accent"] if (i == correct and reveal > 0.5) else WHITE
        d.ellipse((80, y + 14, 144, y + 78), fill=circ_bg + (int(255 * k),))
        tl = text_layer(letter, F["opt"], circ_fg)
        card.alpha_composite(tl, (112 - tl.width // 2, y + 46 - tl.height // 2))
        line_c = lerp(lv["soft"], WHITE, reveal) if i == correct else lv["soft"]
        d.rounded_rectangle((176, y + 34, 176 + [420, 360, 470, 300][i], y + 58), radius=12, fill=line_c)
        if i == correct and reveal > 0:
            # check
            pts = [(730, y + 46), (750, y + 66), (782, y + 28)]
            d.line(pts, fill=WHITE, width=10, joint="curve")
    rise = (1 - ease_out((t - t0) / 0.5)) * 120
    paste(canvas, card, W / 2, 1010 + rise, alpha)


# --- escenas ---------------------------------------------------------------

def frame(lv, t):
    c = background(lv, t)
    acc = lv["accent"]

    # Cabecera fija: pastilla ACTIC + barras de nivel
    head_a = ease_out(t / 0.4)
    paste(c, pill_layer("ACTIC", F["pill"], WHITE, acc), W / 2, 330, head_a)
    level_bars(c, lv, W / 2, 425, ease_out((t - 2.4) / 0.8), head_a)

    # Escena 1 (0 - 2.4s): gancho
    a = window(t, 0.1, 2.4)
    if a > 0:
        up = (1 - ease_out((t - 0.1) / 0.5)) * 60
        text(c, "¿Te presentas", F["h1"], INK, W / 2, 820 + up, a)
        text(c, "al examen", F["h1"], INK, W / 2, 935 + up, a)
        k = ease_back((t - 0.5) / 0.5)
        text(c, "ACTIC?", F["h1x"], acc, W / 2, 1090, a * clamp(k * 2), 0.6 + 0.4 * k)

    # Escena 2 (2.4 - 5.4s): nivel
    a = window(t, 2.4, 5.4)
    if a > 0:
        text(c, "NIVEL", F["small"], INK, W / 2, 800, a)
        k = ease_back((t - 2.5) / 0.55)
        size_k = 1.0 if len(lv["name"]) <= 6 else 0.8
        text(c, lv["name"], F["h1x"], acc, W / 2, 935, a * clamp(k * 2), (0.7 + 0.3 * k) * size_k)
        ck = ease_out((t - 3.0) / 0.4)
        paste(c, pill_layer(lv["chip"], F["chip"], acc, WHITE), W / 2, 1100 + (1 - ck) * 30, a * ck)

    # Escena 3 (5.4 - 8.2s): pregunta tipo test
    a = window(t, 5.4, 8.2)
    if a > 0:
        text(c, "¿Sabrías aprobar?", F["h1"], INK, W / 2, 570, a)
        quiz_card(c, lv, 5.5, t, a)

    # Escena 4 (8.2 - 10s): CTA
    a = window(t, 8.2, DUR + 1)
    if a > 0:
        text(c, "Preguntas tipo examen", F["body"], INK, W / 2, 800, a)
        text(c, f"del nivel {lv['name'].lower()}", F["body"], INK, W / 2, 870, a)
        k = ease_back((t - 8.5) / 0.5)
        text(c, "MUY PRONTO", F["h1"], acc, W / 2, 1010, a * clamp(k * 2), 0.7 + 0.3 * k)
        bk = ease_out((t - 9.0) / 0.4)
        paste(c, pill_layer("Síguenos", F["btn"], WHITE, acc, 60, 26), W / 2, 1180 + (1 - bk) * 30, a * bk)

    return c.convert("RGB")


def cover(lv):
    """Portada pensada para el recorte 3:4 de la cuadrícula."""
    c = background(lv, 0)
    acc = lv["accent"]
    paste(c, pill_layer("ACTIC", F["pill"], WHITE, acc), W / 2, 560)
    level_bars(c, lv, W / 2, 650)
    text(c, "NIVEL", F["small"], INK, W / 2, 860)
    text(c, lv["name"], F["h1x"], acc, W / 2, 995, scale=1.0 if len(lv["name"]) <= 6 else 0.8)
    paste(c, pill_layer(lv["chip"], F["chip"], acc, WHITE), W / 2, 1160)
    return c.convert("RGB")


def grid_preview(covers):
    """Simula el perfil: 3 columnas con recorte 3:4."""
    tw, th, gap = 360, 480, 6
    crop_top = (H - W * 4 // 3) // 2
    g = Image.new("RGB", (tw * 3 + gap * 2, th), WHITE)
    for i, im in enumerate(covers):
        tile = im.crop((0, crop_top, W, crop_top + W * 4 // 3)).resize((tw, th), Image.LANCZOS)
        g.paste(tile, (i * (tw + gap), 0))
    return g


def render(key):
    lv = LEVELS[key]
    path = OUT / f"teaser_actic_{key}.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-f", "lavfi", "-t", str(DUR), "-i", "anullsrc=r=44100:cl=stereo",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(path)],
        stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        proc.stdin.write(frame(lv, i / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print("ok", path)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    covers = []
    for key in LEVELS:
        im = cover(LEVELS[key])
        im.save(OUT / f"portada_{key}.png")
        covers.append(im)
    grid_preview(covers).save(OUT / "vista_cuadricula.png")
    for key in LEVELS:
        render(key)
