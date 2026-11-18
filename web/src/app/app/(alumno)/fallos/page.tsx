import type { Metadata } from "next";
import Link from "next/link";

import Quiz from "@/components/QuizClient";
import { requireAlumno } from "@/lib/access";
import { preguntasPorId } from "@/lib/content";
import { fallos } from "@/lib/progress";

export const metadata: Metadata = { title: "Mis fallos" };

export default async function Fallos() {
  const user = await requireAlumno();
  const preguntas = preguntasPorId(await fallos(user.id));

  return (
    <>
      <h1 style={{ fontSize: "1.8rem" }}>Mis fallos</h1>
      {preguntas.length ? (
        <>
          <p className="muted">
            {preguntas.length} preguntas que fallaste la última vez. Acierta y desaparecerán de aquí.
          </p>
          <Quiz preguntas={preguntas} modo="practica" guardar limite={20} />
        </>
      ) : (
        <div className="card">
          <p>No tienes fallos pendientes. 💪</p>
          <Link href="/app" className="btn">
            Seguir practicando
          </Link>
        </div>
      )}
    </>
  );
}
