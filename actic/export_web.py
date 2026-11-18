"""Exporta las preguntas de los vídeos (quiz.QUIZ + corto.CAPTIONS) a la web.

Uso: python3 export_web.py  ->  ../web/content/preguntas.json
"""
import json
import re
from pathlib import Path

from corto import CAPTIONS
from quiz import QUIZ

# competencia de cada pregunta, según la ilustración que usa
COMPETENCIA = {
    "keys": "equipo", "files": "equipo", "cursor": "equipo", "trash": "equipo", "saveas": "equipo",
    "devices": "equipo", "ram": "equipo", "cutcopy": "equipo",
    "password": "civismo", "phish": "civismo", "lock": "civismo", "twofa": "civismo",
    "antivirus": "civismo", "freesw": "civismo",
    "browser": "navegacion", "url": "navegacion", "mail": "navegacion", "replyall": "navegacion",
    "cloud": "navegacion",
    "merge": "textos", "pagebreak": "textos", "pdf": "textos",
    "lossy": "multimedia",
    "sheet": "calculo", "formula": "calculo", "countif": "calculo", "average": "calculo",
    "si": "calculo", "div0": "calculo", "freeze": "calculo", "filter": "calculo", "pie": "calculo",
    "db": "datos", "query": "datos", "onemany": "datos",
    "transition": "presentaciones", "master": "presentaciones",
    "os": "equipo", "shift": "equipo", "backup": "civismo",
    "spacing": "textos", "txt": "textos",
    "date": "calculo", "vlookup": "calculo",
    "report": "datos",
}
GRATIS = 4  # las primeras N de cada nivel salen en el test gratis (ya son públicas en los reels)

# En el vídeo el dibujo completa la pregunta ("esta referencia", "este error"); en la web no hay dibujo.
TEXTO_WEB = {
    "avanzado-1": "En una hoja de cálculo, ¿para qué sirve el símbolo $ en una referencia como =$A$1?",
    "medio-10": "En una hoja de cálculo, ¿qué significa el error #¡DIV/0!?",
}

out = []
for nivel, items in QUIZ.items():
    for i, q in enumerate(items):
        out.append({
            "id": f"{nivel}-{i + 1}",
            "nivel": nivel,
            "competencia": COMPETENCIA[q["art"]],
            "pregunta": TEXTO_WEB.get(f"{nivel}-{i + 1}", q["q"]),
            "opciones": q["opts"],
            "correcta": q["ok"],
            "explicacion": re.sub(r"^¡La [A-D]!\s*", "", CAPTIONS[nivel][i]),
            "gratis": i < GRATIS,
        })

dst = Path(__file__).parent.parent / "web" / "content" / "preguntas.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
print(len(out), "preguntas ->", dst)
