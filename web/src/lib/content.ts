import "server-only";

import fs from "node:fs";
import path from "node:path";

import banco from "../../content/banco.json";
import preguntas from "../../content/preguntas.json";

export type Nivel = "basico" | "medio" | "avanzado";

export type Pregunta = {
  id: string;
  nivel: Nivel;
  competencia: string;
  pregunta: string;
  opciones: string[];
  correcta: number;
  explicacion: string;
  gratis: boolean;
};

export const NIVELES: { id: Nivel; nombre: string; detalle: string }[] = [
  { id: "basico", nombre: "Básico", detalle: "Nivel 1 de 3 · Fácil" },
  { id: "medio", nombre: "Medio", detalle: "Nivel 2 de 3 · Intermedio" },
  { id: "avanzado", nombre: "Avanzado", detalle: "Nivel 3 de 3 · Difícil" },
];

// Las 8 competencias del ACTIC. `nombre` es el corto que se ve en botones; `oficial`, el del temario.
// Pendiente de contrastar los nombres exactos con la web oficial (actic.gencat.cat).
export const COMPETENCIAS: { id: string; nombre: string; oficial: string }[] = [
  { id: "civismo", nombre: "Cultura y seguridad digital", oficial: "Cultura, participación y civismo digital" },
  { id: "equipo", nombre: "El ordenador y el sistema operativo", oficial: "Tecnología digital y uso del ordenador y del sistema operativo" },
  { id: "navegacion", nombre: "Navegación y comunicación", oficial: "Navegación y comunicación en el mundo digital" },
  { id: "textos", nombre: "Procesador de textos", oficial: "Tratamiento de la información escrita" },
  { id: "multimedia", nombre: "Imagen, sonido y vídeo", oficial: "Tratamiento de la información gráfica, sonora y de la imagen en movimiento" },
  { id: "calculo", nombre: "Hoja de cálculo", oficial: "Tratamiento de la información numérica" },
  { id: "datos", nombre: "Bases de datos", oficial: "Tratamiento de los datos" },
  { id: "presentaciones", nombre: "Presentaciones", oficial: "Presentación de contenidos" },
];

// Preguntas de los reels (generadas desde ../actic con export_web.py) + banco propio de la web.
const TODAS = [...preguntas, ...banco] as Pregunta[];

export function isNivel(s: string): s is Nivel {
  return NIVELES.some((n) => n.id === s);
}

export function nivelNombre(id: Nivel): string {
  return NIVELES.find((n) => n.id === id)!.nombre;
}

export function competenciaNombre(id: string): string {
  return COMPETENCIAS.find((c) => c.id === id)?.nombre ?? id;
}

export function competenciaOficial(id: string): string {
  return COMPETENCIAS.find((c) => c.id === id)?.oficial ?? "";
}

export function preguntasDe(nivel?: Nivel, competencia?: string): Pregunta[] {
  return TODAS.filter((p) => (!nivel || p.nivel === nivel) && (!competencia || p.competencia === competencia));
}

export function preguntasPorId(ids: string[]): Pregunta[] {
  const set = new Set(ids);
  return TODAS.filter((p) => set.has(p.id));
}

export function preguntasGratis(): Pregunta[] {
  return TODAS.filter((p) => p.gratis);
}

export function totalPreguntas(): number {
  return TODAS.length;
}

const TEMARIO_DIR = path.join(process.cwd(), "content", "temario");

export function temario(id: string): string | null {
  const file = path.join(TEMARIO_DIR, `${id}.md`);
  if (!COMPETENCIAS.some((c) => c.id === id) || !fs.existsSync(file)) return null;
  return fs.readFileSync(file, "utf8");
}
