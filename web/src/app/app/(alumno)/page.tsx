import type { Metadata } from "next";
import Link from "next/link";

import Bars from "@/components/Bars";
import { requireAlumno } from "@/lib/access";
import { nivelNombre } from "@/lib/content";
import { progreso } from "@/lib/progress";

export const metadata: Metadata = { title: "Mi progreso" };

export default async function Panel({ searchParams }: { searchParams: Promise<{ bienvenida?: string }> }) {
  const user = await requireAlumno();
  const { bienvenida } = await searchParams;
  const datos = await progreso(user.id);

  return (
    <>
      {bienvenida && (
        <div className="notice ok" style={{ marginBottom: 20 }}>
          <strong>¡Bienvenido/a!</strong> Tu suscripción está activa. Empieza por tu nivel.
        </div>
      )}
      <h1 style={{ fontSize: "2rem" }}>Mi progreso</h1>
      <div className="grid cols-3" style={{ marginTop: 20 }}>
        {datos.map((d) => {
          const pct = d.total ? Math.round((d.dominadas / d.total) * 100) : 0;
          return (
            <div key={d.nivel} className={`card nivel-card nivel-${d.nivel}`}>
              <Bars nivel={d.nivel} />
              <h3 style={{ marginTop: 10 }}>Nivel {nivelNombre(d.nivel).toLowerCase()}</h3>
              <div className="stat">{pct}%</div>
              <div className="progress" style={{ margin: "8px 0 10px" }}>
                <div style={{ width: `${pct}%` }} />
              </div>
              <p className="muted" style={{ fontSize: "0.9rem" }}>
                {d.dominadas} de {d.total} preguntas dominadas · {d.vistas} vistas
              </p>
              <div className="grid">
                <Link href={`/app/practica/${d.nivel}`} className="btn small">
                  Practicar
                </Link>
                <Link href={`/app/simulacro/${d.nivel}`} className="btn small secondary">
                  Simulacro ⏱
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
