"""Vídeos test ACTIC: 3 preguntas tipo examen por nivel, con locución (Pablo) y efectos.

Uso: python3 quiz.py [basico medio avanzado]
Necesita las locuciones en salida/quiz_voz/ ({nivel}_intro, {nivel}_q1..3, {nivel}_a1..3, outro).
La línea de tiempo se ajusta a la duración real de cada locución.
"""
import math
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from sfx import SR, chime, click, pop, riser, tick, whoosh, write_wav
from teaser import (FPS, H, INK, LEVELS, OUT, W, WHITE, background, clamp, ease_back, ease_out,
                    font, lerp, level_bars, paste, pill_layer, text, window)
from teaser import text_layer as _text_layer
from voz import decode, duck

VOZ = OUT / "quiz_voz"

QUIZ = {
    "basico": [
        dict(q="¿Qué atajo de teclado sirve para copiar?",
             opts=["Ctrl + V", "Ctrl + C", "Ctrl + X", "Ctrl + Z"], ok=1, art="keys",
             tip="Ctrl+C copia · Ctrl+V pega"),
        dict(q="¿Qué programa usas para visitar páginas web?",
             opts=["Un antivirus", "Un procesador de textos", "Un navegador", "Una hoja de cálculo"],
             ok=2, art="browser", tip="Chrome, Firefox, Edge…"),
        dict(q="¿Cuál de estos archivos es una imagen?",
             opts=["informe.docx", "notas.txt", "cancion.mp3", "foto.jpg"], ok=3, art="files",
             tip=".jpg es imagen · .mp3 es audio"),
        dict(q="¿Qué tecla borra el carácter que está a la izquierda del cursor?",
             opts=["Supr", "Retroceso", "Esc", "Tab"], ok=1, art="cursor",
             tip="Retroceso ← izquierda · Supr → derecha"),
        dict(q="¿Dónde van los archivos que eliminas en Windows?",
             opts=["Se borran para siempre", "A la Papelera de reciclaje", "A la carpeta Descargas",
                   "Al escritorio"], ok=1, art="trash", tip="Desde la Papelera puedes recuperarlos"),
        dict(q="¿Cómo debe ser una contraseña segura?",
             opts=["Corta y fácil de recordar", "Tu fecha de nacimiento",
                   "Letras, números y símbolos", "Igual en todas tus cuentas"],
             ok=2, art="password", tip="Larga, variada y distinta en cada cuenta"),
        dict(q="¿Qué hace la opción «Guardar como»?",
             opts=["Guarda con el mismo nombre", "Guarda con otro nombre",
                   "Imprime el documento", "Cierra sin guardar"], ok=1, art="saveas",
             tip="El original no se toca"),
        dict(q="¿Cuál de estos es un periférico de entrada?",
             opts=["Monitor", "Impresora", "Teclado", "Altavoces"], ok=2, art="devices",
             tip="Entrada: teclado, ratón · Salida: pantalla, impresora"),
        dict(q="¿Qué es una URL?",
             opts=["Un tipo de virus", "Un programa de correo", "Una red social",
                   "La dirección de una página web"], ok=3, art="url", tip="Lo que escribes en la barra del navegador"),
        dict(q="¿Qué memoria se borra al apagar el ordenador?",
             opts=["Disco duro", "Memoria USB", "Memoria RAM", "Disco SSD"], ok=2, art="ram",
             tip="La RAM es temporal"),
        dict(q="¿Para qué sirve un antivirus?",
             opts=["Acelera internet", "Detecta y elimina malware", "Hace copias de seguridad",
                   "Organiza tus archivos"], ok=1, art="antivirus", tip="Virus, troyanos, spyware…"),
        dict(q="¿Qué diferencia hay entre copiar y cortar?",
             opts=["Ninguna", "Copiar borra el original", "Cortar solo sirve con texto",
                   "Cortar mueve, copiar duplica"], ok=3, art="cutcopy", tip="Cortar = mover"),
    ],
    "medio": [
        dict(q="En una hoja de cálculo, ¿qué fórmula suma de la celda A1 a la A5?",
             opts=["=SUMA(A1;A5)", "=SUMA(A1:A5)", "=A1+A5", "=TOTAL(A1-A5)"], ok=1, art="sheet",
             tip="Los dos puntos (:) marcan un rango"),
        dict(q="Envías un correo a varias personas y no quieres que vean las direcciones de los demás. ¿Qué campo usas?",
             opts=["Para", "CCO", "CC", "Asunto"], ok=1, art="mail", tip="CCO = con copia oculta"),
        dict(q="¿Qué formato usarías para que un documento se vea igual en cualquier ordenador?",
             opts=[".txt", ".csv", ".mp4", ".pdf"], ok=3, art="pdf",
             tip="El PDF conserva el formato"),
        dict(q="En un procesador de textos, ¿para qué sirve la combinación de correspondencia?",
             opts=["Unir dos documentos en uno", "Crear cartas personalizadas",
                   "Revisar la ortografía", "Enviar un documento por correo"], ok=1, art="merge",
             tip="Carta modelo + lista de datos"),
        dict(q="En una hoja de cálculo, ¿qué función cuenta las celdas que cumplen una condición?",
             opts=["=SUMA", "=PROMEDIO", "=CONTAR.SI", "=MAX"], ok=2, art="countif",
             tip='=CONTAR.SI(B2:B6;"Sí")'),
        dict(q="¿Qué es el phishing?",
             opts=["Un tipo de antivirus", "Un engaño para robarte datos", "Una red wifi pública",
                   "Una copia de seguridad"], ok=1, art="phish",
             tip="Revisa siempre el remitente y el enlace"),
        dict(q="En un procesador de textos, ¿para qué sirve un salto de página?",
             opts=["Borra la página actual", "Sigue en la página siguiente", "Numera las páginas",
                   "Cambia la orientación"], ok=1, art="pagebreak", tip="Mejor que pulsar Intro muchas veces"),
        dict(q="En una hoja de cálculo, ¿qué resultado da =PROMEDIO(4;6;8)?",
             opts=["18", "8", "6", "4"], ok=2, art="average", tip="(4 + 6 + 8) / 3 = 6"),
        dict(q="¿Qué significa guardar tus archivos en la nube?",
             opts=["En una memoria USB", "En la memoria RAM", "En un archivo ZIP",
                   "En servidores de internet"], ok=3, art="cloud",
             tip="Accesibles desde cualquier dispositivo"),
        dict(q="En una hoja de cálculo, ¿qué significa este error?",
             opts=["La columna es muy estrecha", "Estás dividiendo entre cero", "Falta un paréntesis",
                   "El archivo está dañado"], ok=1, art="div0", tip="#### = columna estrecha"),
        dict(q="En una hoja de cálculo, ¿para qué sirve inmovilizar paneles?",
             opts=["Oculta columnas", "Bloquea con contraseña", "Fija filas o columnas",
                   "Impide editar celdas"], ok=2, art="freeze", tip="Los títulos siempre a la vista"),
        dict(q="Si pulsas «Responder a todos», ¿a quién le llega tu respuesta?",
             opts=["Solo al remitente", "A todos tus contactos", "A los de copia oculta",
                   "Al remitente y al resto"], ok=3, art="replyall", tip="Los de CCO no la reciben"),
    ],
    "avanzado": [
        dict(q="En una hoja de cálculo, ¿para qué sirve el símbolo $ en esta referencia?",
             opts=["Da formato de moneda", "Fija la referencia al copiar", "Redondea el resultado",
                   "Marca la celda como error"], ok=1, art="formula", tip="$A$1 = referencia absoluta"),
        dict(q="¿Qué te garantiza el candado de la barra del navegador?",
             opts=["Que la web es de fiar", "Que es una web oficial", "Que la conexión va cifrada",
                   "Que no tiene virus"], ok=2, art="lock", tip="Cifrada no significa legítima"),
        dict(q="En una base de datos, ¿qué es la clave primaria?",
             opts=["La contraseña de la base de datos", "El primer campo de la tabla",
                   "Un campo repetido en cada registro", "El campo que identifica cada registro"],
             ok=3, art="db", tip="Única en cada registro, como el DNI"),
        dict(q="¿Qué gráfico usarías para mostrar qué parte del total representa cada dato?",
             opts=["De líneas", "Circular", "De dispersión", "De radar"], ok=1, art="pie",
             tip="Circular = partes de un total"),
        dict(q="En una base de datos, ¿qué es una consulta?",
             opts=["Una copia de seguridad", "Un formulario de entrada",
                   "Una petición que filtra datos", "Un informe para imprimir"], ok=2, art="query",
             tip="Consulta = filtrar con criterios"),
        dict(q="¿Qué es la verificación en dos pasos?",
             opts=["Usar dos contraseñas", "Entrar desde dos dispositivos", "Cambiar la contraseña cada mes",
                   "Contraseña más un código extra"], ok=3, art="twofa",
             tip="Algo que sabes + algo que tienes"),
        dict(q="En una hoja de cálculo, ¿qué hace la función SI?",
             opts=["Suma si hay datos", "Elige según una condición",
                   "Cuenta las celdas vacías", "Busca un valor en una tabla"], ok=1, art="si",
             tip="=SI(condición; si se cumple; si no)"),
        dict(q="¿Qué tipo de software te permite usar, estudiar y modificar un programa?",
             opts=["Software privativo", "Freeware", "Software libre", "Shareware"], ok=2, art="freesw",
             tip="Gratis no es lo mismo que libre"),
        dict(q="En una presentación, ¿qué es una transición?",
             opts=["Animar un objeto", "Cambiar la plantilla", "Insertar un vídeo",
                   "Paso entre diapositivas"], ok=3, art="transition",
             tip="Transición: entre diapositivas"),
        dict(q="En una hoja de cálculo, ¿qué hace un filtro?",
             opts=["Ordena de la A a la Z", "Oculta lo que no cumple", "Borra las filas repetidas",
                   "Protege la hoja"], ok=1, art="filter", tip="Filtrar oculta · Ordenar reordena"),
        dict(q="¿Qué es la compresión con pérdida?",
             opts=["Comprime sin perder nada", "Divide el archivo en partes", "Quita datos para pesar menos",
                   "Cifra el archivo"], ok=2, art="lossy", tip=".jpg y .mp3 pierden · .zip no"),
        dict(q="En una base de datos, ¿qué es una relación uno a varios?",
             opts=["Uno de una tabla, varios de otra", "Dos tablas iguales",
                   "Una tabla de un registro", "Varias claves en una tabla"], ok=0, art="onemany",
             tip="1 cliente → N pedidos"),
    ],
}

G = {
    "q": font("Bold", 60),
    "count": font("Bold", 38),
    "num": font("ExtraBold", 72),
    "letter": font("Bold", 42),
    "tip": font("SemiBold", 42),
    "art": font("Bold", 40),
    "art_s": font("SemiBold", 30),
    "art_l": font("Bold", 64),
    "big": font("Bold", 92),
    "body": font("Medium", 50),
    "name": font("Bold", 58),
    "btn": font("Bold", 56),
}

CARD_W, CARD_H = 900, 340
DIM = (150, 158, 162)


@lru_cache(maxsize=512)
def text_layer(s, fnt, color):
    return _text_layer(s, fnt, color)


@lru_cache(maxsize=64)
def fit_font(s, weight, size, max_w):
    while size > 24 and font(weight, size).getlength(s) > max_w:
        size -= 2
    return font(weight, size)


def wrap(s, fnt, max_w):
    lines, cur = [], ""
    for w in s.split():
        nxt = f"{cur} {w}".strip()
        if fnt.getlength(nxt) <= max_w:
            cur = nxt
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def ctext(d, s, fnt, color, cx, cy):
    """Texto centrado en (cx, cy) sobre un ImageDraw."""
    l, t, r, b = fnt.getbbox(s)
    d.text((cx - (r + l) / 2, cy - (b + t) / 2), s, font=fnt, fill=color)


def rr(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def check(d, cx, cy, s, color, width=10):
    d.line([(cx - s, cy), (cx - s * 0.3, cy + s * 0.7), (cx + s, cy - s * 0.7)],
           fill=color, width=width, joint="curve")


def cross(d, cx, cy, s, color, width=8):
    d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=color, width=width)
    d.line([(cx - s, cy + s), (cx + s, cy - s)], fill=color, width=width)


def padlock(d, cx, cy, s, color, hole):
    w = max(3, int(s * 0.14))
    d.arc((cx - s * 0.33, cy - s * 0.85, cx + s * 0.33, cy - s * 0.15), 180, 360, fill=color, width=w)
    d.line([(cx - s * 0.33 + w / 2, cy - s * 0.5), (cx - s * 0.33 + w / 2, cy - s * 0.2)], fill=color, width=w)
    d.line([(cx + s * 0.33 - w / 2, cy - s * 0.5), (cx + s * 0.33 - w / 2, cy - s * 0.2)], fill=color, width=w)
    rr(d, (cx - s * 0.5, cy - s * 0.3, cx + s * 0.5, cy + s * 0.45), int(s * 0.12), color)
    d.ellipse((cx - s * 0.09, cy - s * 0.05, cx + s * 0.09, cy + s * 0.13), fill=hole)


# --- ilustraciones (sin pistas hasta el momento de la respuesta) ----------

def art_keys(d, lv, k):
    acc, cy = lv["accent"], 170

    def key(cx, w, label, fill, fg):
        rr(d, (cx - w / 2, cy - 64 + 12, cx + w / 2, cy + 76), 28, lerp(fill, INK, 0.25))
        rr(d, (cx - w / 2, cy - 76, cx + w / 2, cy + 64), 28, fill)
        ctext(d, label, G["art_l"], fg, cx, cy - 6)

    key(300, 250, "Ctrl", lv["bg"], INK)
    ctext(d, "+", G["art_l"], INK, 490, cy - 6)
    key(640, 160, "C" if k > 0.5 else "?", lerp(lv["bg"], acc, k), lerp(INK, WHITE, k))


def art_browser(d, lv, k):
    acc = lv["accent"]
    rr(d, (150, 25, 750, 315), 26, lv["bg"], outline=lv["soft"], width=4)
    rr(d, (150, 25, 750, 85), 26, lv["soft"])
    d.rectangle((152, 60, 748, 85), fill=lv["soft"])
    for i, c in enumerate([(226, 112, 98), (232, 190, 92), (110, 186, 120)]):
        d.ellipse((180 + i * 34 - 10, 45, 180 + i * 34 + 10, 65), fill=c)
    rr(d, (285, 38, 725, 74), 18, WHITE)
    d.text((305, 41), "www.ejemplo.es", font=G["art_s"], fill=DIM)
    gx, gy, r = 330, 205, 78
    g = lerp(WHITE, acc, k)
    line = lerp(acc, WHITE, k)
    d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=g, outline=acc, width=6)
    d.ellipse((gx - r * 0.45, gy - r, gx + r * 0.45, gy + r), outline=line, width=5)
    d.line([(gx - r, gy), (gx + r, gy)], fill=line, width=5)
    d.line([(gx, gy - r), (gx, gy + r)], fill=line, width=5)
    for i, wdt in enumerate([260, 220, 240]):
        rr(d, (450, 150 + i * 44, 450 + wdt, 170 + i * 44), 10, lv["soft"])


def art_files(d, lv, k):
    acc = lv["accent"]
    for i, ext in enumerate(["DOCX", "TXT", "MP3", "JPG"]):
        cx = 150 + i * 200
        ok = i == 3
        fade = 0 if ok else 0.55 * k
        base = lerp(lv["bg"], acc, k) if ok else lerp(lv["bg"], WHITE, fade)
        x0, y0, x1, y1 = cx - 66, 30, cx + 66, 205
        d.polygon([(x0, y0), (x1 - 36, y0), (x1, y0 + 36), (x1, y1), (x0, y1)], fill=base)
        d.polygon([(x1 - 36, y0), (x1 - 36, y0 + 36), (x1, y0 + 36)], fill=lerp(base, INK, 0.15))
        if ok and k > 0.5:
            d.ellipse((cx + 10, 70, cx + 36, 96), fill=WHITE)
            d.polygon([(x0 + 14, 185), (cx - 16, 112), (cx + 14, 160), (cx + 30, 140), (x1 - 14, 185)], fill=WHITE)
        else:
            for j in range(4):
                rr(d, (x0 + 18, 80 + j * 28, x1 - 18 - (j % 2) * 26, 94 + j * 28), 7,
                   lerp(lv["soft"], WHITE, fade))
        col = acc if ok and k > 0.5 else lerp(INK, WHITE, fade)
        ctext(d, "." + ext.lower(), G["art"], col, cx, 262)


def art_sheet(d, lv, k):
    acc = lv["accent"]
    x0, y0, rh = 200, 18, 43
    cols = [(x0, 80), (x0 + 80, 220), (x0 + 300, 200)]
    for r in range(7):
        y = y0 + r * rh
        for c, (cx, cw) in enumerate(cols):
            head = r == 0 or c == 0
            d.rectangle((cx, y, cx + cw, y + rh), fill=lv["soft"] if head else WHITE,
                        outline=lerp(lv["soft"], INK, 0.15), width=2)
            label = ""
            if r == 0:
                label = ["", "A", "B"][c]
            elif c == 0:
                label = str(r)
            elif c == 1 and r <= 5:
                label = str(r * 10)
            elif c == 1 and r == 6:
                label = "150" if k > 0.5 else "?"
            if label:
                color = acc if (r == 6 and c == 1 and k > 0.5) else INK
                ctext(d, label, G["art_s"], color, cx + cw / 2, y + rh / 2)
    if k > 0:
        a1, a5 = y0 + rh, y0 + 6 * rh
        d.rectangle((cols[1][0], a1, cols[1][0] + cols[1][1], a5),
                    outline=acc + (int(255 * k),), width=6)


def art_mail(d, lv, k):
    acc = lv["accent"]
    rr(d, (110, 15, 790, 325), 26, lv["bg"])
    rr(d, (110, 15, 790, 70), 26, lv["soft"])
    d.rectangle((112, 50, 788, 70), fill=lv["soft"])
    d.text((140, 24), "Nuevo mensaje", font=G["art_s"], fill=INK)
    for i, (lab, n) in enumerate([("Para:", 1), ("CC:", 2), ("CCO:", 3)]):
        y = 95 + i * 76
        hi = i == 2
        if hi and k > 0:
            rr(d, (130, y - 8, 770, y + 56), 20, lerp(lv["bg"], acc, k))
        fg = lerp(INK, WHITE, k) if hi else INK
        d.text((150, y + 4), lab, font=G["art"], fill=fg)
        for j in range(n):
            x = 290 + j * 160
            chip = lerp(WHITE, lv["soft"], 0.0) if not hi else lerp(WHITE, lerp(acc, WHITE, 0.25), k)
            rr(d, (x, y + 6, x + 140, y + 44), 19, chip)
            d.ellipse((x + 8, y + 12, x + 34, y + 38), fill=lv["soft"] if not hi else lerp(lv["soft"], acc, k))
            if hi and k > 0.5:
                for m in range(4):
                    d.ellipse((x + 48 + m * 20, y + 20, x + 58 + m * 20, y + 30), fill=acc)
            else:
                rr(d, (x + 44, y + 19, x + 124, y + 31), 6, lv["soft"])


def art_pdf(d, lv, k):
    acc = lv["accent"]

    def doc(x0, y0, w, h, badge):
        x1, y1 = x0 + w, y0 + h
        e = w * 0.22
        d.polygon([(x0, y0), (x1 - e, y0), (x1, y0 + e), (x1, y1), (x0, y1)], fill=WHITE,
                  outline=lv["soft"])
        rr(d, (x0 + w * 0.14, y0 + h * 0.18, x1 - w * 0.3, y0 + h * 0.36), 4, lv["soft"])
        for j in range(3):
            rr(d, (x0 + w * 0.14, y0 + h * (0.45 + j * 0.12), x1 - w * 0.14, y0 + h * (0.5 + j * 0.12)), 3,
               lv["soft"])
        if badge > 0:
            bw = w * 0.8
            cx, cy = (x0 + x1) / 2, y0 + h * 0.84
            rr(d, (cx - bw / 2, cy - h * 0.1, cx + bw / 2, cy + h * 0.1), int(h * 0.05),
               acc + (int(255 * badge),))
            if badge > 0.5 and w > 100:
                ctext(d, "PDF", G["art"], WHITE, cx, cy)

    # ordenador
    rr(d, (60, 70, 300, 230), 14, INK)
    rr(d, (72, 82, 288, 218), 8, lv["bg"])
    d.rectangle((160, 230, 200, 262), fill=INK)
    rr(d, (120, 258, 240, 272), 6, INK)
    doc(150, 92, 60, 118, k)
    # documento grande
    doc(360, 22, 180, 290, k)
    # móvil
    rr(d, (650, 50, 790, 300), 24, INK)
    rr(d, (662, 70, 778, 280), 12, lv["bg"])
    doc(686, 100, 68, 150, k)


def art_formula(d, lv, k):
    acc = lv["accent"]
    rr(d, (50, 25, 850, 125), 20, WHITE, outline=lv["soft"], width=4)
    rr(d, (50, 25, 150, 125), 20, lv["soft"])
    d.rectangle((120, 27, 150, 123), fill=lv["soft"])
    ctext(d, "fx", G["art"], INK, 100, 75)

    def formula(x, y, parts, fnt):
        for s, is_abs in parts:
            col = lerp(INK, acc, k) if is_abs else INK
            if s == "$":
                col = lerp(INK, acc, k)
            d.text((x, y), s, font=fnt, fill=col)
            x += fnt.getlength(s)

    big = font("Bold", 60)
    formula(185, 38, [("=B2*", False), ("$", True), ("A", False), ("$", True), ("1", False)], big)
    for i, row in enumerate(["2", "3"]):
        y = 168 + i * 72
        rr(d, (130, y, 230, y + 56), 14, lv["soft"])
        ctext(d, "C" + row, G["art"], INK, 180, y + 28)
        d.line([(250, y + 28), (300, y + 28)], fill=DIM, width=5)
        d.polygon([(300, y + 18), (318, y + 28), (300, y + 38)], fill=DIM)
        x = 340
        for s, absolute in [(f"=B{row}*", False), ("$A$1", True)]:
            col = lerp(INK, acc, k) if absolute else INK
            d.text((x, y + 4), s, font=G["art"], fill=col)
            x += G["art"].getlength(s)
        if k > 0.5:
            padlock(d, x + 40, y + 30, 40, acc, WHITE)


def art_lock(d, lv, k):
    acc = lv["accent"]
    rr(d, (60, 25, 840, 115), 45, WHITE, outline=lv["soft"], width=4)
    padlock(d, 120, 72, 52, lerp(INK, acc, k), WHITE)
    d.text((165, 44), "https://", font=G["art"], fill=lerp(DIM, acc, k))
    d.text((165 + G["art"].getlength("https://"), 44), "tubanco.es", font=G["art"], fill=INK)
    # tú <-> web
    for x, lab in [(90, "TÚ"), (630, "WEB")]:
        rr(d, (x, 170, x + 180, 290), 24, lv["soft"])
        ctext(d, lab, G["art"], INK, x + 90, 230)
    for x in range(285, 615, 30):
        d.line([(x, 230), (x + 16, 230)], fill=lerp(DIM, acc, k), width=6)
    if k > 0.5:
        rr(d, (395, 190, 505, 270), 22, acc)
        padlock(d, 450, 236, 44, WHITE, acc)
        ctext(d, "x7#k@9·f2!", G["art_s"], acc, 450, 165)
    else:
        rr(d, (405, 200, 495, 260), 22, WHITE)
        ctext(d, "?", G["art"], INK, 450, 230)


def art_db(d, lv, k):
    acc = lv["accent"]
    x0, y0, rh = 120, 40, 66
    cols = [("ID", 130), ("Nombre", 250), ("Ciudad", 280)]
    rows = [("1", "Ana", "Girona"), ("2", "Marc", "Lleida"), ("3", "Ana", "Tarragona")]
    for r in range(4):
        x = x0
        for c, (head, cw) in enumerate(cols):
            y = y0 + r * rh
            idcol = c == 0
            fill = lv["soft"] if r == 0 else WHITE
            if idcol:
                fill = lerp(fill, acc, k)
            d.rectangle((x, y, x + cw, y + rh), fill=fill, outline=lerp(lv["soft"], INK, 0.15), width=2)
            s = head if r == 0 else rows[r - 1][c]
            col = lerp(INK, WHITE, k) if idcol else INK
            ctext(d, s, G["art"] if r == 0 else G["art_s"], col, x + cw / 2, y + rh / 2)
            x += cw
    if k > 0.5:
        # llave junto a la columna ID
        kx, ky = 70, y0 + rh / 2
        d.ellipse((kx - 26, ky - 26, kx + 10, ky + 10), outline=acc, width=8)
        d.line([(kx + 4, ky + 4), (kx + 34, ky + 34)], fill=acc, width=8)
        d.line([(kx + 22, ky + 22), (kx + 12, ky + 32)], fill=acc, width=7)


def keycap(d, cx, cy, w, h, label, fill, fg, fnt):
    rr(d, (cx - w / 2, cy - h / 2 + 10, cx + w / 2, cy + h / 2 + 10), 22, lerp(fill, INK, 0.25))
    rr(d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 22, fill)
    ctext(d, label, fnt, fg, cx, cy - 4)


def art_cursor(d, lv, k):
    acc = lv["accent"]
    rr(d, (90, 30, 810, 140), 24, WHITE, outline=lv["soft"], width=4)
    s = "Holaa" if k < 0.5 else "Hola"
    d.text((130, 50), s, font=G["art_l"], fill=INK)
    x = 130 + G["art_l"].getlength(s) + 6
    d.line([(x, 48), (x, 122)], fill=acc, width=6)
    keycap(d, 300, 240, 200, 100, "Supr", lv["bg"], INK, G["art"])
    keycap(d, 590, 240, 300, 100, "← Retroceso", lerp(lv["bg"], acc, k), lerp(INK, WHITE, k), G["art"])


def art_trash(d, lv, k):
    acc = lv["accent"]
    # papelera
    bin_c = lerp(INK, acc, k)
    d.polygon([(580, 135), (740, 135), (722, 305), (598, 305)], fill=bin_c)
    rr(d, (562, 105, 758, 130), 12, bin_c)
    rr(d, (630, 88, 690, 106), 8, bin_c)
    for x in (625, 660, 695):
        d.line([(x, 160), (x, 280)], fill=lerp(bin_c, WHITE, 0.35), width=8)
    # archivo que vuela hacia la papelera
    m = 1 - 0.5 * k
    cx, cy = 230 + (660 - 230) * k, 170 - 60 * math.sin(math.pi * k)
    w, h = 130 * m, 170 * m
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    e = w * 0.28
    if k < 0.95:
        d.polygon([(x0, y0), (x1 - e, y0), (x1, y0 + e), (x1, y1), (x0, y1)], fill=lv["bg"],
                  outline=lv["soft"])
        for j in range(3):
            rr(d, (x0 + w * 0.15, y0 + h * (0.4 + j * 0.15), x1 - w * 0.15, y0 + h * (0.47 + j * 0.15)), 4,
               lv["soft"])
    if k < 0.5:
        for x in range(330, 520, 34):
            d.line([(x, 170), (x + 18, 170)], fill=DIM, width=6)
        d.polygon([(520, 158), (544, 170), (520, 182)], fill=DIM)
    else:
        ctext(d, "Papelera", G["art"], acc, 400, 170)


def art_password(d, lv, k):
    acc = lv["accent"]
    d.text((100, 18), "Contraseña", font=G["art_s"], fill=INK)
    rr(d, (100, 60, 800, 150), 22, WHITE, outline=lerp(lv["soft"], acc, k), width=4)
    if k < 0.5:
        for j in range(6):
            d.ellipse((140 + j * 46, 92, 168 + j * 46, 120), fill=INK)
    else:
        d.text((135, 74), "k7#Rq!m2$P", font=G["art_l"], fill=INK)
    labels = ["Débil", "Segura"]
    n_on = 1 + round(3 * k)
    for j in range(4):
        x = 100 + j * 180
        on = j < n_on
        col = lerp((205, 110, 100), acc, k) if on else lv["soft"]
        rr(d, (x, 200, x + 160, 230), 15, col)
    ctext(d, labels[k > 0.5], G["art"], lerp((205, 110, 100), acc, k), 450, 285)


def art_merge(d, lv, k):
    acc = lv["accent"]

    def letter(x0, y0, w, h, name, hi):
        d.rectangle((x0, y0, x0 + w, y0 + h), fill=WHITE, outline=lv["soft"], width=3)
        tag = name if name else "«Nombre»"
        col = acc if hi else INK
        if not name:
            rr(d, (x0 + 14, y0 + 16, x0 + 26 + G["art_s"].getlength("Hola " + tag), y0 + 58), 10,
               lerp(WHITE, acc, 0.15))
        d.text((x0 + 20, y0 + 20), f"Hola {tag},", font=G["art_s"], fill=col)
        for j in range(4):
            rr(d, (x0 + 20, y0 + 80 + j * 30, x0 + w - 20 - (j % 2) * 40, y0 + 92 + j * 30), 5, lv["soft"])

    letter(40, 40, 260, 250, None, True)
    ctext(d, "+", G["art_l"], INK, 335, 160)
    # lista de datos
    for j, n in enumerate(["Nombre", "Ana", "Marc", "Laia"]):
        y = 70 + j * 48
        d.rectangle((375, y, 525, y + 48), fill=lv["soft"] if j == 0 else WHITE,
                    outline=lerp(lv["soft"], INK, 0.15), width=2)
        ctext(d, n, G["art_s"], INK, 450, y + 24)
    if k > 0:
        a = int(255 * k)
        d.line([(545, 160), (590, 160)], fill=acc + (a,), width=7)
        d.polygon([(590, 146), (610, 160), (590, 174)], fill=acc + (a,))
        for j, n in enumerate(["Laia", "Marc", "Ana"]):
            off = j * 22 * k
            letter(625 + off, 30 + off, 200, 230, n, j == 2)


def art_countif(d, lv, k):
    acc = lv["accent"]
    x0, y0, rh = 230, 18, 43
    cols = [(x0, 70), (x0 + 70, 260)]
    vals = ["¿Aprobado?", "Sí", "No", "Sí", "Sí", "No"]
    for r in range(7):
        y = y0 + r * rh
        for c, (cx, cw) in enumerate(cols):
            head = c == 0
            si = c == 1 and 1 <= r <= 5 and vals[r] == "Sí"
            fill = lv["soft"] if head or r == 0 else (lerp(WHITE, acc, k) if si else WHITE)
            d.rectangle((cx, y, cx + cw, y + rh), fill=fill, outline=lerp(lv["soft"], INK, 0.15), width=2)
            if c == 0:
                label = "" if r == 0 else str(r + 1)
            elif r < 6:
                label = vals[r]
            else:
                label = "3" if k > 0.5 else "?"
            if label:
                col = WHITE if si and k > 0.5 else (acc if r == 6 and k > 0.5 else INK)
                ctext(d, label, G["art_s"], col, cx + cw / 2, y + rh / 2)


def warn(d, cx, cy, s, color):
    d.polygon([(cx, cy - s), (cx + s * 1.1, cy + s * 0.85), (cx - s * 1.1, cy + s * 0.85)], fill=color)
    ctext(d, "!", G["art"], WHITE, cx, cy + s * 0.2)


def art_phish(d, lv, k):
    acc = lv["accent"]
    red = (205, 90, 80)
    rr(d, (70, 15, 830, 325), 26, lv["bg"])
    d.text((100, 35), "De:", font=G["art_s"], fill=DIM)
    d.text((160, 35), "avisos@b4nco-seguro.xyz", font=G["art_s"], fill=INK)
    if k > 0:
        x0 = 160 + G["art_s"].getlength("avisos@")
        x1 = 160 + G["art_s"].getlength("avisos@b4nco-seguro.xyz")
        rr(d, (x0 - 8, 30, x1 + 8, 76), 14, None, outline=red + (int(255 * k),), width=5)
    d.text((100, 95), "¡Tu cuenta será bloqueada!", font=G["art"], fill=INK)
    for j in range(2):
        rr(d, (100, 160 + j * 32, 700 - j * 140, 176 + j * 32), 8, lv["soft"])
    rr(d, (100, 240, 380, 300), 30, acc)
    ctext(d, "Verificar ahora", G["art_s"], WHITE, 240, 270)
    if k > 0.5:
        warn(d, 640, 255, 44, red)
        d.text((700, 238), "Fraude", font=G["art"], fill=red)


def art_pie(d, lv, k):
    acc = lv["accent"]
    data = [("Norte", 40), ("Sur", 25), ("Este", 20), ("Oeste", 15)]
    shades = [acc, lerp(acc, WHITE, 0.3), lerp(acc, WHITE, 0.55), lerp(acc, WHITE, 0.75)]
    for j, (n, v) in enumerate(data):
        y = 50 + j * 60
        d.rectangle((80, y, 230, y + 60), fill=WHITE, outline=lerp(lv["soft"], INK, 0.15), width=2)
        d.rectangle((230, y, 340, y + 60), fill=WHITE, outline=lerp(lv["soft"], INK, 0.15), width=2)
        if k > 0.5:
            d.ellipse((92, y + 22, 108, y + 38), fill=shades[j])
        d.text((116 if k > 0.5 else 100, y + 14), n, font=G["art_s"], fill=INK)
        ctext(d, f"{v}%", G["art_s"], INK, 285, y + 30)
    cx, cy, r = 610, 170, 135
    if k <= 0:
        for a0 in range(0, 360, 20):
            d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 10, fill=DIM, width=6)
        ctext(d, "?", G["art_l"], DIM, cx, cy)
        return
    rr_ = r * (0.6 + 0.4 * k)
    a = -90
    for j, (_, v) in enumerate(data):
        sweep = 360 * v / 100 * k
        d.pieslice((cx - rr_, cy - rr_, cx + rr_, cy + rr_), a, a + sweep, fill=shades[j],
                   outline=WHITE, width=4)
        a += 360 * v / 100


def funnel(d, cx, cy, s, color):
    d.polygon([(cx - s, cy - s * 0.7), (cx + s, cy - s * 0.7), (cx + s * 0.2, cy + s * 0.1),
               (cx + s * 0.2, cy + s * 0.8), (cx - s * 0.2, cy + s * 0.6), (cx - s * 0.2, cy + s * 0.1)],
              fill=color)


def art_query(d, lv, k):
    acc = lv["accent"]
    chip = lerp(lv["bg"], acc, k)
    rr(d, (230, 12, 670, 70), 29, chip)
    funnel(d, 275, 41, 20, lerp(INK, WHITE, k))
    ctext(d, "Ciudad = Girona", G["art_s"], lerp(INK, WHITE, k), 475, 41)
    rows = [("Nombre", "Ciudad"), ("Ana", "Girona"), ("Marc", "Lleida"), ("Laia", "Girona"), ("Pau", "Tarragona")]
    for r, (n, c) in enumerate(rows):
        y = 88 + r * 48
        hit = c == "Girona"
        for x, w, s in ((210, 220, n), (430, 260, c)):
            if r == 0:
                fill, col = lv["soft"], INK
            elif hit:
                fill, col = lerp(WHITE, acc, k), lerp(INK, WHITE, k)
            else:
                fill, col = lerp(WHITE, lv["bg"], k), lerp(INK, DIM, k)
            d.rectangle((x, y, x + w, y + 48), fill=fill, outline=lerp(lv["soft"], INK, 0.15), width=2)
            ctext(d, s, G["art_s"], col, x + w / 2, y + 24)


def art_twofa(d, lv, k):
    acc = lv["accent"]
    rr(d, (60, 20, 540, 320), 26, lv["bg"])
    for j, (lab, kind) in enumerate([("Contraseña", "dots"), ("Código", "code")]):
        y = 45 + j * 135
        d.text((90, y), lab, font=G["art_s"], fill=INK)
        hi = kind == "code"
        rr(d, (90, y + 45, 510, y + 115), 18, WHITE, outline=lerp(lv["soft"], acc, k) if hi else lv["soft"],
           width=4)
        if kind == "dots":
            for m in range(7):
                d.ellipse((115 + m * 40, y + 68, 139 + m * 40, y + 92), fill=INK)
        elif k > 0.5:
            d.text((115, y + 55), "482 913", font=G["art"], fill=acc)
        else:
            for m in range(6):
                d.line([(115 + m * 55, y + 98), (150 + m * 55, y + 98)], fill=DIM, width=5)
    # móvil
    rr(d, (640, 25, 790, 315), 26, INK)
    rr(d, (652, 45, 778, 295), 14, WHITE)
    if k > 0:
        a = int(255 * k)
        rr(d, (662, 120, 768, 210), 16, acc + (a,))
        ctext(d, "Código", font("SemiBold", 22), WHITE, 715, 145)
        ctext(d, "482913", font("Bold", 28), WHITE, 715, 182)
        d.line([(560, 170), (620, 170)], fill=acc + (a,), width=6)
        d.polygon([(560, 158), (542, 170), (560, 182)], fill=acc + (a,))


def art_saveas(d, lv, k):
    acc = lv["accent"]
    rr(d, (50, 20, 580, 320), 24, lv["bg"])
    rr(d, (50, 20, 580, 72), 24, lv["soft"])
    d.rectangle((52, 50, 578, 72), fill=lv["soft"])
    d.text((80, 28), "Guardar como", font=G["art_s"], fill=INK)
    for j, (lab, a, b) in enumerate([("Carpeta:", "Documentos", "Escritorio"),
                                     ("Nombre:", "informe.docx", "informe_v2.docx")]):
        y = 100 + j * 80
        d.text((80, y + 10), lab, font=G["art_s"], fill=INK)
        rr(d, (220, y, 555, y + 56), 14, WHITE, outline=lerp(lv["soft"], acc, k), width=3)
        d.text((238, y + 11), b if k > 0.5 else a, font=G["art_s"], fill=acc if k > 0.5 else INK)
    rr(d, (400, 262, 555, 306), 20, acc)
    ctext(d, "Guardar", G["art_s"], WHITE, 477, 284)

    def doc(x, y, name, col):
        d.polygon([(x, y), (x + 70, y), (x + 95, y + 25), (x + 95, y + 120), (x, y + 120)], fill=col)
        for m in range(3):
            rr(d, (x + 14, y + 45 + m * 22, x + 80, y + 55 + m * 22), 4, WHITE)
        ctext(d, name, font("SemiBold", 22), INK, x + 48, y + 140)

    doc(640, 25 if k > 0 else 90, "informe.docx", lerp(lv["soft"], INK, 0.25))
    if k > 0:
        doc(700, 170 - 30 * (1 - k), "informe_v2.docx", acc)


def art_devices(d, lv, k):
    acc = lv["accent"]
    names = ["Monitor", "Impresora", "Teclado", "Altavoces"]
    for j, n in enumerate(names):
        cx = 140 + j * 207
        ok = j == 2
        col = lerp(INK, acc, k) if ok else lerp(INK, (200, 204, 206), 0.8 * k)
        if j == 0:
            rr(d, (cx - 75, 50, cx + 75, 160), 12, col)
            rr(d, (cx - 63, 62, cx + 63, 148), 6, lv["bg"])
            d.rectangle((cx - 12, 160, cx + 12, 190), fill=col)
            rr(d, (cx - 45, 186, cx + 45, 200), 6, col)
        elif j == 1:
            d.rectangle((cx - 45, 50, cx + 45, 95), fill=WHITE, outline=col, width=4)
            rr(d, (cx - 75, 90, cx + 75, 170), 16, col)
            d.rectangle((cx - 45, 160, cx + 45, 205), fill=WHITE, outline=col, width=4)
        elif j == 2:
            rr(d, (cx - 88, 95, cx + 88, 185), 16, col)
            for r in range(3):
                for m in range(7):
                    x = cx - 76 + m * 22
                    d.rectangle((x, 105 + r * 24, x + 16, 121 + r * 24), fill=lerp(col, WHITE, 0.75))
            d.rectangle((cx - 40, 160, cx + 40, 176), fill=lerp(col, WHITE, 0.75))
        else:
            for x in (cx - 50, cx + 10):
                rr(d, (x, 60, x + 40, 200), 10, col)
                d.ellipse((x + 6, 140, x + 34, 168), fill=lv["bg"])
                d.ellipse((x + 12, 82, x + 28, 98), fill=lv["bg"])
        ctext(d, n, G["art_s"], acc if (ok and k > 0.5) else col, cx, 262)
    if k > 0.5:
        ctext(d, "ENTRADA", font("Bold", 26), acc, 140 + 2 * 207, 300)


def art_url(d, lv, k):
    acc = lv["accent"]
    rr(d, (40, 50, 860, 140), 45, WHITE, outline=lerp(lv["soft"], acc, k), width=4)
    parts = [("https://", "protocolo"), ("www.ejemplo.es", "dominio"), ("/contacto", "página")]
    fnt = font("Bold", 46)
    x = 80
    for j, (p, lab) in enumerate(parts):
        w = fnt.getlength(p)
        d.text((x, 66), p, font=fnt, fill=INK)
        if k > 0.5:
            shade = [acc, lerp(acc, INK, 0.3), lerp(acc, WHITE, 0.35)][j]
            d.line([(x + 4, 152), (x + w - 4, 152)], fill=shade, width=8)
            ctext(d, lab, G["art_s"], shade, x + w / 2, 195)
        x += w
    if k <= 0.5:
        ctext(d, "?", G["art_l"], DIM, 450, 230)


def art_pagebreak(d, lv, k):
    acc = lv["accent"]
    for x0 in (130, 490):
        d.rectangle((x0, 15, x0 + 280, 325), fill=WHITE, outline=lv["soft"], width=3)
    for m in range(4):
        rr(d, (160, 45 + m * 26, 380 - (m % 2) * 50, 57 + m * 26), 5, lv["soft"])

    def heading(x, y):
        rr(d, (x, y, x + 160, y + 26), 6, INK)
        for m in range(3):
            rr(d, (x, y + 44 + m * 24, x + 220 - (m % 2) * 40, y + 54 + m * 24), 5, lv["soft"])

    if k < 0.5:
        heading(160, 165)
    else:
        for x in range(160, 380, 24):
            d.line([(x, 165), (x + 12, 165)], fill=acc, width=5)
        ctext(d, "salto de página", font("SemiBold", 24), acc, 270, 192)
        heading(520, 45)
        rr(d, (510, 35, 690, 80), 8, None, outline=acc, width=4)


def art_average(d, lv, k):
    acc = lv["accent"]
    rr(d, (60, 18, 840, 88), 18, WHITE, outline=lv["soft"], width=4)
    rr(d, (60, 18, 140, 88), 18, lv["soft"])
    d.rectangle((120, 20, 140, 86), fill=lv["soft"])
    ctext(d, "fx", G["art"], INK, 100, 53)
    d.text((165, 26), "=PROMEDIO(4;6;8)", font=G["art"], fill=INK)
    x0, y0, rh = 300, 110, 50
    for r, v in enumerate(["4", "6", "8", "6" if k > 0.5 else "?"]):
        y = y0 + r * rh
        last = r == 3
        d.rectangle((x0, y, x0 + 70, y + rh), fill=lv["soft"], outline=lerp(lv["soft"], INK, 0.15), width=2)
        ctext(d, str(r + 1), G["art_s"], INK, x0 + 35, y + rh / 2)
        fill = lerp(WHITE, acc, k) if last else WHITE
        d.rectangle((x0 + 70, y, x0 + 270, y + rh), fill=fill, outline=lerp(lv["soft"], INK, 0.15), width=2)
        ctext(d, v, G["art_s"], WHITE if last and k > 0.5 else INK, x0 + 170, y + rh / 2)
    if k > 0.5:
        d.text((610, 140), "4 + 6 + 8 = 18", font=G["art_s"], fill=INK)
        d.text((610, 190), "18 / 3 = 6", font=G["art"], fill=acc)


def cloud_shape(d, cx, cy, s, fill):
    for dx, dy, r in ((-0.55, 0.15, 0.42), (0.0, -0.15, 0.55), (0.55, 0.12, 0.45)):
        d.ellipse((cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s), fill=fill)
    d.rectangle((cx - 0.55 * s, cy + 0.1 * s, cx + 0.55 * s, cy + 0.57 * s), fill=fill)


def art_cloud(d, lv, k):
    acc = lv["accent"]
    rr(d, (70, 170, 270, 290), 12, INK)
    rr(d, (82, 182, 258, 278), 6, lv["bg"])
    rr(d, (50, 290, 290, 306), 6, INK)
    rr(d, (690, 150, 790, 310), 18, INK)
    rr(d, (700, 166, 780, 294), 8, lv["bg"])
    cx, cy = 450, 105
    if k < 0.5:
        cloud_shape(d, cx, cy, 120, lv["soft"])
        ctext(d, "?", G["art_l"], DIM, cx, cy + 15)
    else:
        cloud_shape(d, cx, cy, 120, acc)
        d.polygon([(cx - 22, cy - 10), (cx + 10, cy - 10), (cx + 24, cy + 4), (cx + 24, cy + 50),
                   (cx - 22, cy + 50)], fill=WHITE)
        for (x0, y0), (x1, y1) in (((290, 220), (370, 160)), ((670, 200), (540, 160))):
            d.line([(x0, y0), (x1, y1)], fill=acc, width=7)
            for (px, py) in ((x0, y0), (x1, y1)):
                d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=acc)


def art_si(d, lv, k):
    acc = lv["accent"]
    red = (205, 90, 80)
    rr(d, (30, 18, 870, 88), 18, WHITE, outline=lv["soft"], width=4)
    fnt = font("Bold", 34)
    x = 55
    for part, col in [("=SI(", INK), ("B2>=5", acc), (';"Aprobado"', lerp(INK, acc, k)),
                      (';"Suspendido"', lerp(INK, red, k)), (")", INK)]:
        d.text((x, 32), part, font=fnt, fill=col)
        x += fnt.getlength(part)
    x0, y0, rh = 200, 115, 62
    for r, (a, b, col) in enumerate([("Nota (B)", "Resultado", None), ("7", "Aprobado", acc),
                                     ("3", "Suspendido", red)]):
        y = y0 + r * rh
        head = r == 0
        d.rectangle((x0, y, x0 + 170, y + rh), fill=lv["soft"] if head else WHITE,
                    outline=lerp(lv["soft"], INK, 0.15), width=2)
        d.rectangle((x0 + 170, y, x0 + 500, y + rh), fill=lv["soft"] if head else WHITE,
                    outline=lerp(lv["soft"], INK, 0.15), width=2)
        ctext(d, a, G["art_s"], INK, x0 + 85, y + rh / 2)
        res = b if (head or k > 0.5) else "?"
        ctext(d, res, G["art"] if not head else G["art_s"], col if (col and k > 0.5) else INK,
              x0 + 335, y + rh / 2)


def art_freesw(d, lv, k):
    acc = lv["accent"]
    rr(d, (290, 15, 610, 185), 20, INK)
    d.text((315, 25), "</>", font=G["art"], fill=WHITE)
    for m, (w, c) in enumerate([(180, acc), (230, (232, 190, 92)), (150, lv["soft"]), (200, acc)]):
        rr(d, (340, 80 + m * 24, 340 + w, 92 + m * 24), 6, lerp(c, WHITE, 0.2))
    if k < 0.5:
        d.ellipse((400, 50, 500, 150), fill=lv["soft"])
        padlock(d, 450, 105, 60, INK, lv["soft"])
    for j, lab in enumerate(["Usar", "Estudiar", "Modificar", "Compartir"]):
        cx = 130 + j * 213
        rr(d, (cx - 95, 225, cx + 95, 290), 32, lerp(lv["bg"], acc, k))
        ctext(d, lab, G["art_s"], lerp(INK, WHITE, k), cx, 257)


def art_transition(d, lv, k):
    acc = lv["accent"]

    def slide(x0, y0, title):
        d.rectangle((x0, y0, x0 + 300, y0 + 170), fill=WHITE, outline=lv["soft"], width=3)
        rr(d, (x0 + 24, y0 + 22, x0 + 180, y0 + 46), 6, INK)
        for m in range(3):
            rr(d, (x0 + 24, y0 + 70 + m * 26, x0 + 250 - (m % 2) * 60, y0 + 80 + m * 26), 5, lv["soft"])
        ctext(d, title, font("SemiBold", 24), DIM, x0 + 150, y0 + 195)

    slide(60, 70, "Diapositiva 1")
    slide(540, 70, "Diapositiva 2")
    if k > 0:
        # la diapositiva 2 entra con un barrido
        d.rectangle((542, 72, 542 + int(296 * k), 238), fill=lerp(WHITE, acc, 0.18))
        rr(d, (564, 92, 720, 116), 6, INK)
    col = lerp(DIM, acc, k)
    d.line([(390, 155), (515, 155)], fill=col, width=8)
    d.polygon([(515, 140), (535, 155), (515, 170)], fill=col)
    ctext(d, "Transición" if k > 0.5 else "?", font("Bold", 28) if k > 0.5 else G["art_l"], col, 462, 110)


def doc_icon(d, x, y, w, col, lines=WHITE):
    h = w * 1.3
    e = w * 0.28
    d.polygon([(x, y), (x + w - e, y), (x + w, y + e), (x + w, y + h), (x, y + h)], fill=col)
    for m in range(3):
        rr(d, (x + w * 0.16, y + h * (0.4 + m * 0.17), x + w * 0.84, y + h * (0.48 + m * 0.17)), 3, lines)


def folder(d, x0, y0, x1, y1, col):
    rr(d, (x0, y0, x0 + (x1 - x0) * 0.4, y0 + 30), 8, col)
    rr(d, (x0, y0 + 16, x1, y1), 12, col)


def art_ram(d, lv, k):
    acc = lv["accent"]
    red = (205, 90, 80)
    pc = lerp(INK, red, k)
    d.ellipse((90, 90, 250, 250), outline=pc, width=12)
    d.rectangle((90 + 64, 70, 90 + 96, 110), fill=WHITE)
    d.line([(170, 72), (170, 170)], fill=pc, width=12)
    ctext(d, "OFF" if k > 0.5 else "", G["art"], red, 170, 290)
    board = (66, 120, 84)
    rr(d, (320, 100, 840, 235), 14, board)
    for m in range(4):
        x = 350 + m * 120
        d.rectangle((x, 122, x + 95, 200), fill=INK)
        txt = "1011" if k < 0.5 else "····"
        ctext(d, txt, font("Bold", 24), lerp(WHITE, DIM, k), x + 47, 161)
    for m in range(26):
        x = 335 + m * 19
        d.rectangle((x, 215, x + 10, 235), fill=(212, 175, 55))
    if k > 0.5:
        ctext(d, "RAM: se vacía al apagar", G["art_s"], acc, 580, 285)


def bug(d, cx, cy, s, col):
    for dy in (-0.3, 0, 0.3):
        d.line([(cx - s, cy + dy * s * 2), (cx + s, cy + dy * s * 2)], fill=col, width=4)
    d.ellipse((cx - s * 0.55, cy - s * 0.8, cx + s * 0.55, cy + s * 0.8), fill=col)
    d.ellipse((cx - s * 0.35, cy - s * 1.15, cx + s * 0.35, cy - s * 0.6), fill=col)


def art_antivirus(d, lv, k):
    acc = lv["accent"]
    red = (205, 90, 80)
    cx, cy = 450, 165
    pts = [(cx, cy - 140), (cx + 120, cy - 95), (cx + 110, cy + 40), (cx, cy + 145),
           (cx - 110, cy + 40), (cx - 120, cy - 95)]
    d.polygon(pts, fill=lerp(lv["soft"], acc, k))
    if k > 0.5:
        check(d, cx, cy, 50, WHITE, 16)
    for bx, by in ((180, 90), (230, 250), (700, 80), (740, 240), (130, 180), (790, 165)):
        bug(d, bx, by, 26, lerp(INK, (220, 220, 220), 0.6 * k))
        if k > 0.5:
            cross(d, bx, by, 30, red, 7)


def art_cutcopy(d, lv, k):
    acc = lv["accent"]
    for r, lab in enumerate(["Copiar", "Cortar"]):
        y = 30 + r * 150
        d.text((40, y + 40), lab, font=G["art"], fill=INK)
        folder(d, 230, y, 420, y + 125, lv["soft"])
        folder(d, 600, y, 790, y + 125, lv["soft"])
        d.line([(440, y + 70), (560, y + 70)], fill=lerp(DIM, acc, k), width=7)
        d.polygon([(560, y + 58), (580, y + 70), (560, y + 82)], fill=lerp(DIM, acc, k))
        src_there = r == 0 or k < 0.5
        if src_there:
            doc_icon(d, 300, y + 38, 52, INK)
        else:
            d.rectangle((300, y + 38, 352, y + 106), outline=DIM, width=3)
        if k > 0.5:
            doc_icon(d, 670, y + 38, 52, acc)
        else:
            ctext(d, "?", G["art_l"], DIM, 695, y + 72)


def art_div0(d, lv, k):
    acc = lv["accent"]
    red = (205, 90, 80)
    rr(d, (60, 18, 840, 88), 18, WHITE, outline=lv["soft"], width=4)
    rr(d, (60, 18, 140, 88), 18, lv["soft"])
    d.rectangle((120, 20, 140, 86), fill=lv["soft"])
    ctext(d, "fx", G["art"], INK, 100, 53)
    d.text((165, 26), "=B2/C2", font=G["art"], fill=INK)
    x0, y0 = 110, 130
    cols = [("", 70), ("B", 190), ("C", 190), ("D", 230)]
    for r in range(2):
        x = x0
        for c, (head, w) in enumerate(cols):
            y = y0 + r * 70
            hi = r == 1 and c == 2
            fill = lv["soft"] if r == 0 or c == 0 else (lerp(WHITE, acc, k) if hi else WHITE)
            d.rectangle((x, y, x + w, y + 70), fill=fill, outline=lerp(lv["soft"], INK, 0.15), width=2)
            if r == 0:
                s, col = head, INK
            else:
                s, col = ["2", "120", "0" if k > 0.5 else "?", "#¡DIV/0!"][c], INK
                if c == 3:
                    col = red
                if hi and k > 0.5:
                    col = WHITE
            ctext(d, s, G["art"], col, x + w / 2, y + 35)
            x += w
    if k > 0.5:
        ctext(d, "120 ÷ 0 = error", G["art_s"], acc, 450, 300)


def art_freeze(d, lv, k):
    acc = lv["accent"]
    x0, y0, rh = 200, 20, 52
    rows = [str(n) for n in ((18, 19, 20, 21, 22) if k > 0.5 else (2, 3, 4, 5, 6))]
    names = ["Ana", "Marc", "Laia", "Pau", "Joan"] if k < 0.5 else ["Nil", "Clara", "Iker", "Sara", "Pol"]
    for r in range(6):
        y = y0 + r * rh
        head = r == 0
        for x, w, s in ((x0, 70, "1" if head else rows[r - 1]), (x0 + 70, 260, "Nombre" if head else names[r - 1]),
                        (x0 + 330, 170, "Nota" if head else str(5 + (r * 3) % 5))):
            num = x == x0
            fill = lv["soft"] if num else (lerp(lv["soft"], acc, k) if head else WHITE)
            col = lerp(INK, WHITE, k) if head and not num else INK
            d.rectangle((x, y, x + w, y + rh), fill=fill, outline=lerp(lv["soft"], INK, 0.15), width=2)
            ctext(d, s, G["art_s"], col, x + w / 2, y + rh / 2)
    if k > 0.5:
        d.line([(x0, y0 + rh), (x0 + 500, y0 + rh)], fill=acc, width=6)
        padlock(d, x0 + 545, y0 + rh / 2 + 4, 40, acc, WHITE)


def art_replyall(d, lv, k):
    acc = lv["accent"]
    rr(d, (40, 20, 500, 210), 22, lv["bg"])
    for j, (lab, val) in enumerate([("De:", "Ana"), ("Para:", "tú, Marc"), ("CC:", "Laia")]):
        d.text((70, 40 + j * 52), lab, font=G["art_s"], fill=DIM)
        d.text((170, 40 + j * 52), val, font=G["art_s"], fill=INK)
    rr(d, (40, 240, 230, 300), 30, lv["soft"])
    ctext(d, "Responder", G["art_s"], INK, 135, 270)
    rr(d, (250, 240, 520, 300), 30, lerp(lv["soft"], acc, k))
    ctext(d, "Responder a todos", font("SemiBold", 26), lerp(INK, WHITE, k), 385, 270)
    for j, n in enumerate(["Ana", "Marc", "Laia"]):
        cy = 60 + j * 95
        col = lerp(lv["soft"], acc, k)
        if k > 0.5:
            d.line([(525, 270), (690, cy)], fill=acc, width=5)
        d.ellipse((690, cy - 38, 766, cy + 38), fill=col)
        ctext(d, n[0], G["art"], lerp(INK, WHITE, k), 728, cy)
        d.text((785, cy - 18), n, font=G["art_s"], fill=INK)


def art_filter(d, lv, k):
    acc = lv["accent"]
    data = [("2", "Ana", "Girona"), ("3", "Marc", "Lleida"), ("4", "Laia", "Girona"),
            ("5", "Pau", "Tarragona"), ("6", "Joan", "Girona")]
    shown = [r for r in data if k < 0.5 or r[2] == "Girona"]
    x0, y0, rh = 170, 20, 50
    rows = [("1", "Nombre", "Ciudad")] + shown
    for r, (n, a, b) in enumerate(rows):
        y = y0 + r * rh
        head = r == 0
        for x, w, s in ((x0, 70, n), (x0 + 70, 230, a), (x0 + 300, 260, b)):
            num = x == x0
            d.rectangle((x, y, x + w, y + rh), fill=lv["soft"] if head or num else WHITE,
                        outline=lerp(lv["soft"], INK, 0.15), width=2)
            col = acc if (num and not head and k > 0.5) else INK
            ctext(d, s, G["art_s"], col, x + w / 2 - (14 if head and x == x0 + 300 else 0), y + rh / 2)
    # botón del filtro en la cabecera
    bx, by = x0 + 530, y0 + rh / 2
    if k > 0.5:
        funnel(d, bx, by, 13, acc)
    else:
        d.polygon([(bx - 9, by - 5), (bx + 9, by - 5), (bx, by + 7)], fill=INK)


def art_lossy(d, lv, k):
    acc = lv["accent"]

    def pic(x0, y0, size, cells):
        c = size / cells
        for gy in range(cells):
            for gx in range(cells):
                v = 0.5 + 0.5 * math.sin(gx * 4.8 / cells + gy * 2.4 / cells) * math.cos(gy * 3.6 / cells)
                d.rectangle((x0 + gx * c, y0 + gy * c, x0 + (gx + 1) * c, y0 + (gy + 1) * c),
                            fill=lerp(acc, WHITE, 0.15 + 0.7 * v))

    pic(110, 25, 220, 22)
    ctext(d, "foto.png · 5 MB", G["art_s"], INK, 220, 285)
    d.line([(370, 135), (500, 135)], fill=lerp(DIM, acc, k), width=7)
    d.polygon([(500, 122), (520, 135), (500, 148)], fill=lerp(DIM, acc, k))
    if k > 0.5:
        pic(570, 25, 220, 6)
        ctext(d, "foto.jpg · 0,8 MB", G["art_s"], acc, 680, 285)
    else:
        d.rectangle((570, 25, 790, 245), outline=DIM, width=4)
        ctext(d, "?", G["art_l"], DIM, 680, 135)


def art_onemany(d, lv, k):
    acc = lv["accent"]
    d.rectangle((70, 90, 310, 140), fill=lv["soft"], outline=lerp(lv["soft"], INK, 0.15), width=2)
    ctext(d, "Clientes", G["art_s"], INK, 190, 115)
    d.rectangle((70, 140, 310, 200), fill=lerp(WHITE, acc, k), outline=lerp(lv["soft"], INK, 0.15), width=2)
    ctext(d, "Ana", G["art"], lerp(INK, WHITE, k), 190, 170)
    d.rectangle((580, 20, 820, 70), fill=lv["soft"], outline=lerp(lv["soft"], INK, 0.15), width=2)
    ctext(d, "Pedidos", G["art_s"], INK, 700, 45)
    for j, n in enumerate(["#101 · Ana", "#102 · Ana", "#103 · Ana"]):
        y = 70 + j * 64
        d.rectangle((580, y, 820, y + 64), fill=WHITE, outline=lerp(lv["soft"], INK, 0.15), width=2)
        ctext(d, n, G["art_s"], INK, 700, y + 32)
        if k > 0.5:
            d.line([(310, 170), (580, y + 32)], fill=acc, width=5)
    if k > 0.5:
        ctext(d, "1", G["art"], acc, 335, 135)
        ctext(d, "N", G["art"], acc, 555, 290)
    else:
        ctext(d, "?", G["art_l"], DIM, 445, 165)


ARTS = dict(keys=art_keys, browser=art_browser, files=art_files, sheet=art_sheet, mail=art_mail,
            pdf=art_pdf, formula=art_formula, lock=art_lock, db=art_db, cursor=art_cursor,
            trash=art_trash, password=art_password, merge=art_merge, countif=art_countif,
            phish=art_phish, pie=art_pie, query=art_query, twofa=art_twofa, saveas=art_saveas,
            devices=art_devices, url=art_url, pagebreak=art_pagebreak, average=art_average,
            cloud=art_cloud, si=art_si, freesw=art_freesw, transition=art_transition,
            ram=art_ram, antivirus=art_antivirus, cutcopy=art_cutcopy, div0=art_div0,
            freeze=art_freeze, replyall=art_replyall, filter=art_filter, lossy=art_lossy,
            onemany=art_onemany)


def art_card(lv, name, k):
    img = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, CARD_W - 1, CARD_H - 1), 44, WHITE + (240,))
    ARTS[name](d, lv, k)
    return img


# --- línea de tiempo ---------------------------------------------------------

def load_voices(key):
    names = ["intro", "q1", "a1", "q2", "a2", "q3", "a3"]
    clips = {n: decode(VOZ / f"{key}_{n}.mp3") for n in names}
    clips["outro"] = decode(VOZ / "outro.mp3")
    return clips


def build_timeline(clips):
    dur = {n: len(c) / SR for n, c in clips.items()}
    tl = {"voice": [], "scenes": []}
    t = 0.0
    intro_end = 0.6 + dur["intro"] + 0.5
    tl["voice"].append((0.6, "intro"))
    tl["scenes"].append(dict(kind="intro", start=0.0, end=intro_end))
    t = intro_end
    for i in range(3):
        s = t
        vq = s + 0.45
        opts_done = s + 0.7 + 3 * 0.15 + 0.3
        cd = max(vq + dur[f"q{i + 1}"] + 0.35, opts_done)
        rv = cd + 3.0
        va = rv + 0.35
        end = va + dur[f"a{i + 1}"] + 0.8
        tl["voice"] += [(vq, f"q{i + 1}"), (va, f"a{i + 1}")]
        tl["scenes"].append(dict(kind="q", i=i, start=s, cd=cd, rv=rv, end=end))
        t = end
    tl["voice"].append((t + 0.4, "outro"))
    tl["scenes"].append(dict(kind="outro", start=t, end=t + 0.4 + dur["outro"] + 1.6))
    tl["dur"] = tl["scenes"][-1]["end"]
    return tl


# --- escenas -----------------------------------------------------------------

def scene_intro(c, lv, sc, t, a):
    acc = lv["accent"]
    tau = t - sc["start"]
    up = (1 - ease_out(tau / 0.5)) * 60
    text(c, "TEST", G["name"], INK, W / 2, 640 + up, a)
    k = ease_back((tau - 0.3) / 0.55)
    text(c, "ACTIC", font("ExtraBold", 190), acc, W / 2, 790, a * clamp(k * 2), 0.6 + 0.4 * k)
    k2 = ease_back((tau - 0.9) / 0.5)
    paste(c, pill_layer(f"NIVEL {lv['name']}", G["name"], WHITE, acc, 50, 24), W / 2, 975,
          a * clamp(k2 * 2), 0.7 + 0.3 * k2)
    k3 = ease_out((tau - 1.4) / 0.4)
    paste(c, pill_layer(lv["chip"], font("SemiBold", 44), acc, WHITE), W / 2, 1100 + (1 - k3) * 30, a * k3)
    k4 = ease_out((tau - 2.4) / 0.4)
    text(c, "3 preguntas tipo examen", G["body"], INK, W / 2, 1290 + (1 - k4) * 30, a * k4)
    text(c, "¿Cuántas aciertas?", font("Bold", 64), acc, W / 2, 1375 + (1 - k4) * 30, a * k4)


def option_layer(lv, letter, s, appear, reveal, ok):
    acc = lv["accent"]
    ow, oh = 900, 104
    img = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = lerp(WHITE, acc, reveal) if ok else WHITE
    rr(d, (0, 0, ow - 1, oh - 1), 34, bg + (255,))
    circ = WHITE if (ok and reveal > 0.5) else acc
    d.ellipse((22, 18, 90, 86), fill=circ)
    ctext(d, letter, G["letter"], acc if (ok and reveal > 0.5) else WHITE, 56, 52)
    fnt = fit_font(s, "SemiBold", 46, 660)
    fg = lerp(INK, WHITE, reveal) if ok else INK
    l, t, r, b = fnt.getbbox(s)
    d.text((118 - l, 52 - (b + t) / 2), s, font=fnt, fill=fg)
    if ok and reveal > 0:
        check(d, 838, 52, 22 * clamp(reveal * 1.5), WHITE)
    if not ok and reveal > 0:
        cross(d, 840, 52, 14, lerp(WHITE, (205, 110, 100), reveal), 7)
    alpha = appear * (1 - 0.5 * reveal if not ok else 1)
    return img, alpha


def scene_question(c, lv, sc, t, a):
    acc = lv["accent"]
    q = QUIZ_CUR[sc["i"]]
    tau = t - sc["start"]
    up = (1 - ease_out(tau / 0.5)) * 50
    text(c, f"PREGUNTA {sc['i'] + 1} DE 3", G["count"], acc, W / 2, 330 + up, a)
    lines = wrap(q["q"], G["q"], 960)
    y0 = 420 if len(lines) <= 2 else 400
    lh = 74 if len(lines) <= 3 else 66
    fq = G["q"] if len(lines) <= 3 else font("Bold", 52)
    if fq is not G["q"]:
        lines = wrap(q["q"], fq, 980)
    for j, ln in enumerate(lines):
        text(c, ln, fq, INK, W / 2, y0 + j * lh + up, a)
    art_y = 450 + len(lines) * lh + CARD_H / 2 - 10
    reveal = ease_out((t - sc["rv"]) / 0.35)
    k = ease_back((tau - 0.25) / 0.5)
    paste(c, art_card(lv, q["art"], reveal), W / 2, art_y, a * clamp(k * 2), 0.85 + 0.15 * k)
    opt_y0 = art_y + CARD_H / 2 + 90
    for j, s in enumerate(q["opts"]):
        ap = ease_out((tau - (0.7 + j * 0.15)) / 0.3)
        if ap <= 0:
            continue
        ok = j == q["ok"]
        layer, alpha = option_layer(lv, "ABCD"[j], s, ap, reveal, ok)
        bump = 1 + 0.05 * math.sin(math.pi * clamp((t - sc["rv"]) / 0.4)) if ok else 1
        paste(c, layer, W / 2 + (1 - ap) * 80, opt_y0 + j * 122, a * alpha, bump)
    # cuenta atrás -> pista
    wy = opt_y0 + 4 * 122 + 40
    if sc["cd"] <= t < sc["rv"] + 0.3:
        rem = sc["rv"] - t
        fa = a * ease_out((t - sc["cd"]) / 0.25) * (1 - ease_out((t - sc["rv"]) / 0.25))
        ring = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
        d = ImageDraw.Draw(ring)
        d.ellipse((5, 5, 145, 145), fill=WHITE)
        frac = clamp(rem / 3.0)
        if frac > 0:
            d.arc((5, 5, 145, 145), -90, -90 + 360 * frac, fill=acc, width=12)
        n = max(1, math.ceil(rem)) if rem > 0 else 1
        ctext(d, str(n), G["num"], INK, 75, 72)
        sub = (rem % 1.0)
        paste(c, ring, W / 2, wy, fa, 1 + 0.08 * ease_out((sub - 0.8) / 0.2))
    tk = ease_back((t - sc["rv"] - 0.25) / 0.45)
    if tk > 0:
        tip = pill_layer(q["tip"], G["tip"], WHITE, acc, 40, 22)
        sc_tip = min(1.0, 980 / tip.width)
        paste(c, tip, W / 2, wy, a * clamp(tk * 2), (0.7 + 0.3 * tk) * sc_tip)


def scene_outro(c, lv, sc, t, a):
    acc = lv["accent"]
    tau = t - sc["start"]
    up = (1 - ease_out(tau / 0.5)) * 60
    text(c, "¿Cuántas has", G["big"], INK, W / 2, 560 + up, a)
    text(c, "acertado?", G["big"], INK, W / 2, 670 + up, a)
    for j in range(3):
        k = ease_back((tau - 0.5 - j * 0.25) / 0.4)
        if k <= 0:
            continue
        circ = Image.new("RGBA", (170, 170), (0, 0, 0, 0))
        d = ImageDraw.Draw(circ)
        d.ellipse((5, 5, 165, 165), fill=acc)
        ctext(d, f"{j + 1}/3", font("ExtraBold", 56), WHITE, 85, 82)
        paste(c, circ, W / 2 + (j - 1) * 220, 880, a * clamp(k * 2), 0.6 + 0.4 * k)
    k = ease_out((tau - 1.5) / 0.4)
    text(c, "Déjalo en comentarios", G["body"], INK, W / 2, 1080 + (1 - k) * 30, a * k)
    k = ease_back((tau - 2.2) / 0.5)
    paste(c, pill_layer("Síguenos", G["btn"], WHITE, acc, 70, 28), W / 2, 1230, a * clamp(k * 2), 0.7 + 0.3 * k)
    k = ease_out((tau - 2.6) / 0.4)
    text(c, "para más preguntas tipo examen", font("Medium", 42), INK, W / 2, 1350, a * k)


QUIZ_CUR = None


def frame(lv, tl, t):
    c = background(lv, t)
    acc = lv["accent"]
    head_a = ease_out(t / 0.4)
    paste(c, pill_layer("ACTIC", font("Bold", 40), WHITE, acc), W / 2, 150, head_a)
    level_bars(c, lv, W / 2, 235, ease_out((t - 1.6) / 0.8), head_a)
    for sc in tl["scenes"]:
        a = window(t, sc["start"], sc["end"] + (1 if sc is tl["scenes"][-1] else 0))
        if a <= 0:
            continue
        if sc["kind"] == "intro":
            scene_intro(c, lv, sc, t, a)
        elif sc["kind"] == "q":
            scene_question(c, lv, sc, t, a)
        else:
            scene_outro(c, lv, sc, t, a)
    return c.convert("RGB")


# --- audio -------------------------------------------------------------------

def audio(lv, tl, clips):
    n = int(tl["dur"] * SR) + SR
    voice = np.zeros(n)
    for t0, name in tl["voice"]:
        s = int(t0 * SR)
        voice[s:s + len(clips[name])] += clips[name]
    ev = [(0.05, whoosh(), 0.6), (0.3, pop(), 1.0), (0.9, pop(520, 140, 0.15), 1.0),
          (1.4, pop(900, 500, 0.08), 0.6)]
    for i in range(lv["n"]):
        kf = 0.95 * (i + 1) / lv["n"]
        ev.append((1.6 + 0.8 * (1 - (1 - kf) ** (1 / 3)), tick(1600 + 300 * i), 1.0))
    for sc in tl["scenes"][1:]:
        ev.append((sc["start"] - 0.15, whoosh(), 0.6))
        if sc["kind"] == "q":
            ev.append((sc["start"] + 0.25, pop(700, 300, 0.1), 0.6))
            for j in range(4):
                ev.append((sc["start"] + 0.7 + j * 0.15, click(), 0.6))
            for s in range(3):
                ev.append((sc["cd"] + s, tick(1900), 1.0))
                ev.append((sc["cd"] + s + 0.5, tick(1250), 0.5))
            ev.append((sc["rv"] - 0.6, riser(), 0.8))
            ev.append((sc["rv"], chime(), 1.0))
            ev.append((sc["rv"] + 0.25, pop(), 0.8))
        else:
            for j in range(3):
                ev.append((sc["start"] + 0.5 + j * 0.25, pop(600 + j * 150, 250, 0.12), 0.9))
            ev.append((sc["start"] + 2.2, click(), 1.0))
    fx = np.zeros(n)
    for t0, snd, gain in ev:
        s = int(t0 * SR)
        fx[s:s + len(snd)] += snd[: n - s] * gain
    fx *= 0.6 / np.max(np.abs(fx))
    out = voice + fx * duck(voice, depth=0.55)
    out = out[: int(tl["dur"] * SR)]
    out *= 0.9 / np.max(np.abs(out))
    return np.stack([out, out], axis=1)


def render(key):
    global QUIZ_CUR
    QUIZ_CUR = QUIZ[key]
    lv = LEVELS[key]
    clips = load_voices(key)
    tl = build_timeline(clips)
    wav = OUT / f"quiz_{key}.wav"
    write_wav(wav, audio(lv, tl, clips))
    frame(lv, tl, tl["scenes"][0]["end"] - 0.6).save(OUT / f"portada_quiz_{key}.png")
    path = OUT / f"quiz_actic_{key}.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(path)],
        stdin=subprocess.PIPE)
    for i in range(int(tl["dur"] * FPS)):
        proc.stdin.write(frame(lv, tl, i / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print("ok", path, f"{tl['dur']:.1f}s")


if __name__ == "__main__":
    for key in sys.argv[1:] or list(QUIZ):
        render(key)
