import type { Metadata } from "next";
import { notFound } from "next/navigation";

import Quiz from "@/components/QuizClient";
import { isNivel, nivelNombre, preguntasDe } from "@/lib/content";

export const metadata: Metadata = { title: "Simulacro" };

// Formato del simulacro. Ajústalo al formato oficial del examen de cada nivel.
const PREGUNTAS = 20;
const MINUTOS = 30;

export default async function Simulacro({ params }: { params: Promise<{ nivel: string }> }) {
  const { nivel } = await params;
  if (!isNivel(nivel)) notFound();
  const preguntas = preguntasDe(nivel);
  const n = Math.min(PREGUNTAS, preguntas.length);

  return (
    <div className={`nivel-${nivel}`}>
      <h1 style={{ fontSize: "1.8rem" }}>Simulacro · {nivelNombre(nivel)}</h1>
      <p className="muted">
        {n} preguntas · {MINUTOS} minutos. No verás si aciertas hasta entregar, como en el examen.
      </p>
      <Quiz preguntas={preguntas} modo="simulacro" tiempo={MINUTOS * 60} guardar limite={n} />
    </div>
  );
}
