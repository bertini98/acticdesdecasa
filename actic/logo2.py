"""Logo acticdesdecasa: casa + barras de nivel + check, sobre fondo oscuro con brillo."""
import math
from PIL import Image, ImageDraw, ImageFilter
from teaser import LEVELS, OUT, WHITE, font

S = 1080
X = 2  # supersampling
ACC = [LEVELS[k]["accent"] for k in ("basico", "medio", "avanzado")]
DST = OUT / "logo"


def lighten(c, k):
    return tuple(int(v + (255 - v) * k) for v in c)


def background(top, bottom, glow):
    n = S * X
    bg = Image.new("RGB", (n, n))
    d = ImageDraw.Draw(bg)
    for y in range(n):
        k = y / n
        d.line([(0, y), (n, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)))
    g = Image.new("L", (n, n), 0)
    ImageDraw.Draw(g).ellipse((n * 0.2, n * 0.15, n * 0.8, n * 0.75), fill=110)
    g = g.filter(ImageFilter.GaussianBlur(n * 0.12))
    return Image.composite(Image.new("RGB", (n, n), glow), bg, g)


def thick_line(d, pts, w, color):
    d.line(pts, fill=color, width=w, joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=color)


def make(top, bottom, glow, sub_color):
    im = background(top, bottom, glow).convert("RGBA")
    s = lambda v: v * X
    # sombra
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    # tejado (casa)
    roof = [(s(190), s(430)), (s(540), s(140)), (s(890), s(430))]
    bars = []
    x, w, gap, base = 295, 150, 30, 715
    for c, h in zip(ACC, (150, 225, 300)):
        bars.append(((s(x), s(base - h), s(x + w), s(base)), c))
        x += w + gap
    for box, _ in bars:
        ds.rounded_rectangle(tuple(v + s(14) for v in box), radius=s(36), fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(s(14)))
    im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    thick_line(d, roof, s(46), WHITE)
    for (x0, y0, x1, y1), c in bars:
        d.rounded_rectangle((x0, y0, x1, y1), radius=s(36), fill=c)
        # brillo superior
        d.rounded_rectangle((x0, y0, x1, y0 + s(60)), radius=s(36), fill=lighten(c, 0.12))
        d.rectangle((x0, y0 + s(36), x1, y0 + s(60)), fill=c)
    check = [(s(345), s(585)), (s(470), s(680)), (s(765), s(395))]
    cs = Image.new("RGBA", im.size, (0, 0, 0, 0))
    thick_line(ImageDraw.Draw(cs), [(px + s(6), py + s(10)) for px, py in check], s(52), (0, 0, 0, 120))
    im.alpha_composite(cs.filter(ImageFilter.GaussianBlur(s(10))))
    d = ImageDraw.Draw(im)
    thick_line(d, check, s(52), WHITE)
    # nombre
    f1, f2 = font("ExtraBold", s(96)), font("SemiBold", s(96))
    w1, w2 = f1.getlength("actic"), f2.getlength("desdecasa")
    x0 = (S * X - w1 - w2) / 2
    y = s(800)
    d.text((x0, y), "actic", font=f1, fill=WHITE)
    d.text((x0 + w1, y), "desdecasa", font=f2, fill=sub_color)
    return im.convert("RGB").resize((S, S), Image.LANCZOS)


if __name__ == "__main__":
    from logo import circle_preview
    DST.mkdir(parents=True, exist_ok=True)
    ims = {
        "oscuro": make((24, 33, 40), (14, 20, 26), (52, 66, 78), (150, 200, 175)),
        "azul": make((30, 58, 96), (16, 30, 54), (66, 104, 150), (170, 200, 235)),
        "verde": make((26, 70, 52), (12, 36, 28), (60, 120, 92), (180, 225, 200)),
    }
    for name, im in ims.items():
        im.save(DST / f"logo_acticdesdecasa_{name}.png")
    circle_preview(list(ims.values())).save(DST / "vista_perfil_acticdesdecasa.png")
    print("ok")
