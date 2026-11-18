import "server-only";

import fs from "node:fs";
import path from "node:path";

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

// Bloques de contenido del temario. Revisa los nombres con el temario oficial del ACTIC.
export const COMPETENCIAS: { id: string; nombre: string }[] = [
  { id: "civismo", nombre: "Cultura y seguridad digital" },
  { id: "equipo", nombre: "El ordenador y el sistema operativo" },
  { id: "navegacion", nombre: "Navegación y comunicación" },
  { id: "textos", nombre: "Procesador de textos" },
  { id: "multimedia", nombre: "Imagen, sonido y vídeo" },
  { id: "calculo", nombre: "Hoja de cálculo" },
  { id: "datos", nombre: "Bases de datos" },
  { id: "presentaciones", nombre: "Presentaciones" },
];

const TODAS = preguntas as Pregunta[];

export function isNivel(s: string): s is Nivel {
  return NIVELES.some((n) => n.id === s);
}

export function nivelNombre(id: Nivel): string {
  return NIVELES.find((n) => n.id === id)!.nombre;
}

export function competenciaNombre(id: string): string {
  return COMPETENCIAS.find((c) => c.id === id)?.nombre ?? id;
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
