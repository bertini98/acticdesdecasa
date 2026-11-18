"""Logos para el perfil de Instagram (1080x1080, pensados para el recorte circular)."""
from PIL import Image, ImageDraw
from teaser import INK, LEVELS, OUT, WHITE, font

S = 1080
ACC = [LEVELS[k]["accent"] for k in ("basico", "medio", "avanzado")]
DST = OUT / "logo"


def ctext(d, s, fnt, color, cx, cy):
    l, t, r, b = fnt.getbbox(s)
    d.text((cx - (r + l) / 2, cy - (b + t) / 2), s, font=fnt, fill=color)


def bars(d, cx, base, w, gap, heights, r):
    x = cx - (3 * w + 2 * gap) / 2
    for c, h in zip(ACC, heights):
        d.rounded_rectangle((x, base - h, x + w, base), radius=r, fill=c)
        x += w + gap


def logo_oscuro():
    im = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(im)
    ctext(d, "ACTIC", font("ExtraBold", 230), WHITE, S / 2, 470)
    x = S / 2 - (3 * 190 + 2 * 24) / 2
    for c in ACC:
        d.rounded_rectangle((x, 640, x + 190, 690), radius=25, fill=c)
        x += 214
    return im


def logo_barras():
    im = Image.new("RGB", (S, S), (246, 244, 240))
    d = ImageDraw.Draw(im)
    bars(d, S / 2, 640, 150, 40, (160, 270, 380), 40)
    ctext(d, "ACTIC", font("ExtraBold", 140), INK, S / 2, 760)
    return im


def logo_check():
    im = Image.new("RGB", (S, S), (246, 244, 240))
    d = ImageDraw.Draw(im)
    bars(d, S / 2, 700, 170, 34, (220, 330, 440), 48)
    # check blanco atravesando las barras
    d.line([(330, 520), (470, 640), (760, 330)], fill=WHITE, width=56, joint="curve")
    ctext(d, "ACTIC", font("ExtraBold", 120), INK, S / 2, 820)
    return im


def circle_preview(ims):
    """Cómo se ven en el perfil: círculo a tamaño real y en pequeño."""
    pad, big, small = 40, 320, 110
    sheet = Image.new("RGB", (len(ims) * (big + pad) + pad, big + small + pad * 3), WHITE)
    for i, im in enumerate(ims):
        for size, y in ((big, pad), (small, big + pad * 2)):
            mask = Image.new("L", (size * 4, size * 4), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
            tile = im.resize((size, size), Image.LANCZOS)
            x = pad + i * (big + pad) + (big - size) // 2
            sheet.paste(tile, (x, y), mask.resize((size, size), Image.LANCZOS))
    return sheet


if __name__ == "__main__":
    DST.mkdir(parents=True, exist_ok=True)
    ims = {"oscuro": logo_oscuro(), "barras": logo_barras(), "check": logo_check()}
    for name, im in ims.items():
        im.save(DST / f"logo_{name}.png")
    circle_preview(list(ims.values())).save(DST / "vista_perfil.png")
    print("ok")
