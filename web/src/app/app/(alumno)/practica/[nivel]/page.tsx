import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import Quiz from "@/components/QuizClient";
import { COMPETENCIAS, competenciaNombre, isNivel, nivelNombre, preguntasDe } from "@/lib/content";

export const metadata: Metadata = { title: "Práctica" };

export default async function Practica({
  params,
  searchParams,
}: {
  params: Promise<{ nivel: string }>;
  searchParams: Promise<{ tema?: string }>;
}) {
  const { nivel } = await params;
  const { tema } = await searchParams;
  if (!isNivel(nivel)) notFound();

  const temas = COMPETENCIAS.filter((c) => preguntasDe(nivel, c.id).length > 0);
  const preguntas = preguntasDe(nivel, tema);

  return (
    <div className={`nivel-${nivel}`}>
      <h1 style={{ fontSize: "1.8rem" }}>
        Práctica · {nivelNombre(nivel)}
        {tema ? ` · ${competenciaNombre(tema)}` : ""}
      </h1>
      <nav className="subnav">
        <Link href={`/app/practica/${nivel}`}>Todos los temas</Link>
        {temas.map((t) => (
          <Link key={t.id} href={`/app/practica/${nivel}?tema=${t.id}`}>
            {t.nombre}
          </Link>
        ))}
      </nav>
      <Quiz key={`${nivel}-${tema ?? ""}`} preguntas={preguntas} modo="practica" guardar limite={20} />
    </div>
  );
}
