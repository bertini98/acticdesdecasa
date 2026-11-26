import type { Metadata } from "next";
import Link from "next/link";

import { COMPETENCIAS, temario } from "@/lib/content";

export const metadata: Metadata = { title: "Temario" };

export default function Temario() {
  return (
    <>
      <h1 style={{ fontSize: "1.8rem" }}>Temario</h1>
      <p className="muted">Lo esencial de cada competencia, con lo que más cae en el examen.</p>
      <div className="list-links" style={{ marginTop: 20 }}>
        {COMPETENCIAS.filter((c) => temario(c.id)).map((c) => (
          <Link key={c.id} href={`/app/temario/${c.id}`}>
            <span>
              {c.nombre}
              <br />
              <small className="muted" style={{ fontWeight: 500 }}>{c.oficial}</small>
            </span>
            <span aria-hidden>→</span>
          </Link>
        ))}
      </div>
    </>
  );
}
