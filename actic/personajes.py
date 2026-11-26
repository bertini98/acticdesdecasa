"""Personajes animables para los reels de promoción (dibujados con PIL, sin imágenes externas).

- Casi: la mascota, una casita (como el logo) con las 3 barras de nivel en la barriga.
- Marta: la estudiante que prepara el ACTIC.

Cada función dibuja el personaje en una capa RGBA con parámetros de animación
(boca 0..1 para hablar, parpadeo 0..1, expresión, pose) y se pega en el fotograma con teaser.paste.
Se dibuja al doble de tamaño y se reduce para que los bordes queden suaves.

Uso de prueba: python3 personajes.py  → salida/personajes/hoja.png
"""
import math

from PIL import Image, ImageDraw

from teaser import INK, LEVELS, OUT, WHITE, font

SS = 2  # supermuestreo

GREEN = LEVELS["basico"]["accent"]
BLUE = LEVELS["medio"]["accent"]
RED = LEVELS["avanzado"]["accent"]
CREAM = (255, 250, 240)
LINE = (40, 52, 58)
CHEEK = (246, 160, 150)
SKIN = (241, 194, 160)
SKIN_D = (222, 168, 132)
HAIR = (74, 50, 40)
HOODIE = (92, 130, 200)
HOODIE_D = (70, 104, 168)


def _down(img):
    return img.resize((img.width // SS, img.height // SS), Image.LANCZOS)


def _eye(d, cx, cy, rx, ry, blink, look=(0, 0), happy=False):
    """Ojo blanco con pupila; blink=1 cerrado. happy: ojo en arco (^)."""
    if happy:
        d.arc((cx - rx, cy - ry * 0.6, cx + rx, cy + ry * 1.2), 200, 340, fill=LINE, width=int(rx * 0.32))
        return
    h = max(ry * (1 - blink), 2)
    if h <= 3:
        d.line((cx - rx, cy, cx + rx, cy), fill=LINE, width=int(rx * 0.3))
        return
    d.ellipse((cx - rx, cy - h, cx + rx, cy + h), fill=WHITE, outline=LINE, width=int(rx * 0.16))
    pr = rx * 0.55
    px, py = cx + look[0] * rx * 0.35, cy + look[1] * h * 0.35
    ph = min(pr, h * 0.8)
    d.ellipse((px - pr, py - ph, px + pr, py + ph), fill=LINE)
    d.ellipse((px - pr * 0.15 - pr * 0.3, py - ph * 0.55 - pr * 0.25, px - pr * 0.15 + pr * 0.1,
               py - ph * 0.55 + pr * 0.15), fill=WHITE)


def _mouth(d, cx, cy, w, mouth, mood):
    """mouth 0..1 = apertura al hablar; mood: smile, worried, wow, grin."""
    lw = int(w * 0.13)
    if mood == "worried" and mouth < 0.15:
        d.arc((cx - w * 0.5, cy, cx + w * 0.5, cy + w * 0.6), 200, 340, fill=LINE, width=lw)
        return
    if mood == "wow" or mouth >= 0.15:
        oh = w * (0.25 + 0.55 * max(mouth, 0.5 if mood == "wow" else 0))
        ow = w * (0.55 if mood == "wow" else 0.75)
        d.ellipse((cx - ow / 2, cy - oh * 0.3, cx + ow / 2, cy + oh * 0.7), fill=(120, 40, 50), outline=LINE,
                  width=lw)
        # lengua
        d.chord((cx - ow * 0.3, cy + oh * 0.25, cx + ow * 0.3, cy + oh * 0.75), 180, 360, fill=(232, 110, 110))
        return
    if mood == "grin":
        d.chord((cx - w * 0.5, cy - w * 0.2, cx + w * 0.5, cy + w * 0.55), 0, 180, fill=(120, 40, 50), outline=LINE,
                width=lw)
        return
    d.arc((cx - w * 0.5, cy - w * 0.35, cx + w * 0.5, cy + w * 0.35), 20, 160, fill=LINE, width=lw)


def casi(size=420, mouth=0.0, blink=0.0, mood="smile", arms="down", look=(0, 0), squash=0.0, bars=1.0):
    """Mascota casita. arms: down, wave, up (celebrar), point (señala a la derecha).
    squash: -1..1 estira/aplasta para los saltos. bars: relleno de las barras 0..1."""
    S = size * SS
    img = Image.new("RGBA", (S, int(S * 1.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = S / 2
    sy = 1 - 0.12 * squash
    sx = 1 + 0.12 * squash
    bw, bh = S * 0.62 * sx, S * 0.5 * sy
    base = S * 1.12
    top = base - bh
    lw = int(S * 0.022)

    # piernas
    for k in (-1, 1):
        lx = cx + k * bw * 0.22
        d.rounded_rectangle((lx - S * 0.045, base - S * 0.02, lx + S * 0.045, base + S * 0.08), radius=int(S * 0.04),
                            fill=LINE)
        d.ellipse((lx - S * 0.07 + k * S * 0.02, base + S * 0.05, lx + S * 0.07 + k * S * 0.02, base + S * 0.11),
                  fill=LINE)

    # brazos (detrás del cuerpo)
    def arm(k, ang):
        sx0 = cx + k * bw * 0.47
        sy0 = top + bh * 0.45
        ln = S * 0.2
        ex = sx0 + k * math.cos(ang) * ln
        ey = sy0 - math.sin(ang) * ln
        d.line((sx0, sy0, ex, ey), fill=LINE, width=int(S * 0.05))
        d.ellipse((ex - S * 0.045, ey - S * 0.045, ex + S * 0.045, ey + S * 0.045), fill=CREAM, outline=LINE,
                  width=lw)

    poses = {"down": (-1.1, -1.1), "wave": (-1.1, 1.2), "up": (1.1, 1.1), "point": (-1.1, 0.25)}
    a_l, a_r = poses.get(arms, poses["down"])
    if arms == "wave":
        a_r += 0.0
    arm(-1, a_l)
    arm(1, a_r)

    # cuerpo
    d.rounded_rectangle((cx - bw / 2, top, cx + bw / 2, base), radius=int(S * 0.08), fill=CREAM, outline=LINE,
                        width=lw)
    # tejado con alero redondeado + chimenea
    rw = bw * 1.22
    peak = top - S * 0.36 * sy
    ch_x = cx + rw * 0.24
    d.rounded_rectangle((ch_x - S * 0.045, peak + S * 0.08, ch_x + S * 0.045, top - S * 0.08), radius=int(S * 0.015),
                        fill=GREEN, outline=LINE, width=lw)
    d.polygon([(cx - rw / 2, top + S * 0.03), (cx, peak), (cx + rw / 2, top + S * 0.03)], fill=GREEN, outline=LINE,
              width=lw)
    d.line((cx - rw / 2, top + S * 0.03, cx, peak, cx + rw / 2, top + S * 0.03), fill=LINE, width=lw, joint="curve")
    # ventanita redonda en el tejado (check)
    wy = top - S * 0.12 * sy
    d.ellipse((cx - S * 0.06, wy - S * 0.06, cx + S * 0.06, wy + S * 0.06), fill=WHITE, outline=LINE, width=lw)
    d.line((cx - S * 0.03, wy, cx - S * 0.005, wy + S * 0.025, cx + S * 0.035, wy - S * 0.025), fill=GREEN,
           width=int(S * 0.018), joint="curve")

    # cara
    ey = top + bh * 0.3
    _eye(d, cx - bw * 0.2, ey, S * 0.06, S * 0.075, blink, look, happy=mood == "grin")
    _eye(d, cx + bw * 0.2, ey, S * 0.06, S * 0.075, blink, look, happy=mood == "grin")
    for k in (-1, 1):
        ccx = cx + k * bw * 0.33
        d.ellipse((ccx - S * 0.045, ey + S * 0.06, ccx + S * 0.045, ey + S * 0.1), fill=CHEEK)
    if mood == "worried":
        for k in (-1, 1):
            d.line((cx + k * bw * 0.27, ey - S * 0.12, cx + k * bw * 0.12, ey - S * 0.09), fill=LINE, width=lw)
    _mouth(d, cx, ey + S * 0.11, S * 0.13, mouth, mood)

    # barriga: 3 barras de nivel
    by = base - bh * 0.2
    bwid = bw * 0.17
    for i, col in enumerate((GREEN, BLUE, RED)):
        x = cx + (i - 1) * bwid * 1.3
        d.rounded_rectangle((x - bwid / 2, by - S * 0.022, x + bwid / 2, by + S * 0.022), radius=int(S * 0.022),
                            fill=(226, 222, 214))
        k = max(0.0, min(1.0, bars * 3 - i))
        if k > 0:
            d.rounded_rectangle((x - bwid / 2, by - S * 0.022, x - bwid / 2 + max(S * 0.044, bwid * k), by + S * 0.022),
                                radius=int(S * 0.022), fill=col)
    return _down(img)


def marta(size=520, mouth=0.0, blink=0.0, mood="smile", look=(0, 0), sweat=0.0, phone=False, arm_up=False):
    """Estudiante (busto). mood: smile, worried, wow, grin. sweat 0..1 = gota de agobio."""
    S = size * SS
    img = Image.new("RGBA", (S, int(S * 1.15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = S / 2
    lw = int(S * 0.016)

    # sudadera (hombros)
    sh_top = S * 0.72
    d.rounded_rectangle((cx - S * 0.36, sh_top, cx + S * 0.36, S * 1.3), radius=int(S * 0.16), fill=HOODIE,
                        outline=LINE, width=lw)
    d.polygon([(cx - S * 0.1, sh_top + S * 0.01), (cx, sh_top + S * 0.12), (cx + S * 0.1, sh_top + S * 0.01)],
              fill=HOODIE_D)
    for k in (-1, 1):  # cordones
        d.line((cx + k * S * 0.05, sh_top + S * 0.06, cx + k * S * 0.055, sh_top + S * 0.2), fill=WHITE, width=lw)
    # cuello
    d.rounded_rectangle((cx - S * 0.06, S * 0.62, cx + S * 0.06, sh_top + S * 0.04), radius=int(S * 0.03),
                        fill=SKIN_D)

    # moño + pelo de atrás
    hy = S * 0.42
    hr = S * 0.22
    d.ellipse((cx - S * 0.1, hy - hr - S * 0.17, cx + S * 0.1, hy - hr + S * 0.03), fill=HAIR, outline=LINE, width=lw)
    d.ellipse((cx - hr * 1.08, hy - hr * 1.02, cx + hr * 1.08, hy + hr * 1.1), fill=HAIR, outline=LINE, width=lw)
    # cara
    d.ellipse((cx - hr, hy - hr * 0.88, cx + hr, hy + hr * 1.05), fill=SKIN, outline=LINE, width=lw)
    # flequillo
    d.chord((cx - hr * 1.02, hy - hr * 1.0, cx + hr * 1.02, hy - hr * 0.1), 180, 360, fill=HAIR)
    d.polygon([(cx - hr * 0.95, hy - hr * 0.45), (cx - hr * 0.2, hy - hr * 0.6), (cx + hr * 0.5, hy - hr * 0.2),
               (cx + hr * 0.95, hy - hr * 0.35), (cx + hr * 0.9, hy - hr * 0.6), (cx - hr * 0.9, hy - hr * 0.6)],
              fill=HAIR)
    # orejas
    for k in (-1, 1):
        ex = cx + k * hr * 0.98
        d.ellipse((ex - S * 0.035, hy, ex + S * 0.035, hy + S * 0.08), fill=SKIN, outline=LINE, width=lw)

    ey = hy + hr * 0.12
    _eye(d, cx - hr * 0.4, ey, S * 0.042, S * 0.05, blink, look, happy=mood == "grin")
    _eye(d, cx + hr * 0.4, ey, S * 0.042, S * 0.05, blink, look, happy=mood == "grin")
    # cejas
    for k in (-1, 1):
        x0, x1 = cx + k * hr * 0.6, cx + k * hr * 0.2
        if mood == "worried":
            d.line((x0, ey - S * 0.07, x1, ey - S * 0.095), fill=HAIR, width=int(lw * 1.4))
        elif mood == "wow":
            d.arc((min(x0, x1), ey - S * 0.13, max(x0, x1), ey - S * 0.07), 200, 340, fill=HAIR, width=int(lw * 1.4))
        else:
            d.line((x0, ey - S * 0.08, x1, ey - S * 0.085), fill=HAIR, width=int(lw * 1.4))
    for k in (-1, 1):
        ccx = cx + k * hr * 0.58
        d.ellipse((ccx - S * 0.035, ey + S * 0.045, ccx + S * 0.035, ey + S * 0.075), fill=CHEEK)
    _mouth(d, cx, hy + hr * 0.55, S * 0.09, mouth, mood)

    if sweat > 0:
        sx, sy = cx + hr * 0.95, hy - hr * 0.35 + sweat * S * 0.03
        d.ellipse((sx - S * 0.03, sy, sx + S * 0.03, sy + S * 0.065), fill=(150, 205, 245), outline=LINE, width=lw)
        d.polygon([(sx - S * 0.026, sy + S * 0.02), (sx, sy - S * 0.03), (sx + S * 0.026, sy + S * 0.02)],
                  fill=(150, 205, 245))

    if phone or arm_up:
        # brazo levantado con móvil o puño
        ax, ay = cx + S * 0.3, sh_top + S * 0.18
        hx, hy2 = cx + S * 0.38, sh_top - S * (0.12 if arm_up else 0.02)
        d.line((ax, ay, hx, hy2), fill=HOODIE, width=int(S * 0.09))
        d.line((ax, ay, hx, hy2), fill=LINE, width=lw)
        if phone:
            d.rounded_rectangle((hx - S * 0.05, hy2 - S * 0.12, hx + S * 0.05, hy2 + S * 0.04), radius=int(S * 0.02),
                                fill=INK)
            d.rounded_rectangle((hx - S * 0.04, hy2 - S * 0.105, hx + S * 0.04, hy2 + S * 0.02), radius=int(S * 0.012),
                                fill=GREEN)
        d.ellipse((hx - S * 0.045, hy2 - S * 0.02, hx + S * 0.045, hy2 + S * 0.06), fill=SKIN, outline=LINE, width=lw)
    return _down(img)


def bocadillo(texto, fnt, max_w=620, tail="left", fill=WHITE, color=INK):
    """Bocadillo de cómic con el texto partido en líneas."""
    words, lines, cur = texto.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    lines.append(cur)
    lh = int(fnt.size * 1.25)
    tw = int(max(fnt.getlength(s) for s in lines))
    pad = 34
    w, h = tw + pad * 2, lh * len(lines) + pad * 2
    img = Image.new("RGBA", (w + 8, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, w + 4, h + 4), radius=38, fill=fill, outline=LINE, width=5)
    tx = 70 if tail == "left" else w - 70
    d.polygon([(tx - 26, h), (tx + 4 if tail == "left" else tx - 4, h + 52), (tx + 26, h)], fill=fill)
    d.line((tx - 26, h + 2, tx + 4 if tail == "left" else tx - 4, h + 52, tx + 26, h + 2), fill=LINE, width=5)
    for i, s in enumerate(lines):
        d.text((4 + pad + (tw - fnt.getlength(s)) / 2, 4 + pad + i * lh), s, font=fnt, fill=color)
    return img


if __name__ == "__main__":
    from teaser import H, W, background, paste, text

    dst = OUT / "personajes"
    dst.mkdir(parents=True, exist_ok=True)

    # Hoja de personajes
    sheet = Image.new("RGBA", (W * 2, H), (246, 244, 239, 255))
    t = font("ExtraBold", 72)
    s = font("SemiBold", 40)
    ImageDraw.Draw(sheet).text((80, 60), "Casi · la mascota", font=t, fill=INK)
    for i, (kw, lab) in enumerate([
        (dict(mood="smile"), "Normal"),
        (dict(mood="smile", mouth=0.8, arms="wave"), "Hablando / saluda"),
        (dict(mood="grin", arms="up", squash=-0.6), "¡Aprobado!"),
        (dict(mood="worried", arms="point", look=(1, 0)), "Señala / agobio"),
    ]):
        x = 280 + i * 500
        paste(sheet, casi(400, **kw), x, 520)
        sheet_d = ImageDraw.Draw(sheet)
        sheet_d.text((x - s.getlength(lab) / 2, 830), lab, font=s, fill=(110, 118, 122))

    ImageDraw.Draw(sheet).text((80, 960), "Marta · la estudiante", font=t, fill=INK)
    for i, (kw, lab) in enumerate([
        (dict(mood="worried", sweat=1), "Agobiada"),
        (dict(mood="smile", mouth=0.7), "Hablando"),
        (dict(mood="wow", look=(0.5, 0.3)), "¡¿Qué?!"),
        (dict(mood="grin", arm_up=True), "¡Aprobada!"),
        (dict(mood="smile", phone=True, look=(1, -0.5)), "Con el móvil"),
    ]):
        x = 260 + i * 420
        paste(sheet, marta(420, **kw), x, 1420)
        ImageDraw.Draw(sheet).text((x - s.getlength(lab) / 2, 1700), lab, font=s, fill=(110, 118, 122))
    sheet.convert("RGB").save(dst / "hoja.png")

    # Escena de ejemplo (fotograma de reel)
    lv = LEVELS["basico"]
    f = background(lv, 0)
    d = ImageDraw.Draw(f)
    # mesa
    d.rounded_rectangle((-40, 1520, W + 40, 1600), radius=20, fill=(196, 160, 120), outline=LINE, width=5)
    d.rectangle((0, 1600, W, H), fill=(170, 136, 100))
    # calendario
    d.rounded_rectangle((90, 250, 420, 560), radius=26, fill=WHITE, outline=LINE, width=5)
    d.rounded_rectangle((90, 250, 420, 340), radius=26, fill=RED, outline=LINE, width=5)
    d.rectangle((95, 310, 415, 340), fill=RED)
    text(f, "ACTIC", font("ExtraBold", 50), WHITE, 255, 297)
    text(f, "MAÑANA", font("ExtraBold", 54), RED, 255, 450)
    paste(f, marta(560, mood="worried", sweat=1, look=(1, 0.2)), 360, 1220)
    paste(f, casi(380, mood="smile", mouth=0.6, arms="wave"), 800, 1240)
    paste(f, bocadillo("¿El ACTIC mañana y sin estudiar?", font("Bold", 50), 520, tail="right"), 690, 760)
    text(f, "@acticdesdecasa", font("Bold", 40), INK, W / 2, 1800)
    f.convert("RGB").save(dst / "escena.png")
    print("ok", dst)
