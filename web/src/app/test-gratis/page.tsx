import type { Metadata } from "next";

import Quiz from "@/components/QuizClient";
import { preguntasGratis } from "@/lib/content";

export const metadata: Metadata = {
  title: "Test ACTIC gratis",
  description: "10 preguntas tipo examen del ACTIC, con explicaciones. Sin registro.",
};

export default function TestGratis() {
  // Las preguntas gratis son las mismas que salen en los reels: no pasa nada si son públicas.
  const preguntas = preguntasGratis().map(({ id, nivel, pregunta, opciones, correcta, explicacion }) => ({
    id,
    nivel,
    pregunta,
    opciones,
    correcta,
    explicacion,
  }));
  return (
    <section className="section">
      <div className="wrap">
        <h1 className="center" style={{ fontSize: "2rem" }}>
          Test ACTIC gratis
        </h1>
        <p className="muted center" style={{ marginBottom: 28 }}>
          Preguntas tipo examen de los tres niveles. Responde y mira la explicación de cada una.
        </p>
        <Quiz preguntas={preguntas} modo="gratis" limite={10} />
      </div>
    </section>
  );
}
