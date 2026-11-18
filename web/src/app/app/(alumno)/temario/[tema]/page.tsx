import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { COMPETENCIAS, NIVELES, competenciaNombre, preguntasDe, temario } from "@/lib/content";
import { markdownToHtml } from "@/lib/markdown";

export function generateStaticParams() {
  return COMPETENCIAS.map((c) => ({ tema: c.id }));
}

// Página privada: basta con un título fijo (un título por tema obligaría a renderizar el <head> en cada petición).
export const metadata: Metadata = { title: "Temario" };

export default async function Tema({ params }: { params: Promise<{ tema: string }> }) {
  const { tema } = await params;
  const md = temario(tema);
  if (!md) notFound();
  const niveles = NIVELES.filter((n) => preguntasDe(n.id, tema).length > 0);

  return (
    <>
      <Link href="/app/temario" className="muted">
        ← Temario
      </Link>
      <h1 style={{ fontSize: "2rem", marginTop: 12 }}>{competenciaNombre(tema)}</h1>
      <article className="prose" dangerouslySetInnerHTML={{ __html: markdownToHtml(md) }} />
      {niveles.length > 0 && (
        <div className="card" style={{ marginTop: 32, maxWidth: 720 }}>
          <h3>Ponte a prueba con este tema</h3>
          <div className="grid cols-3" style={{ marginTop: 12 }}>
            {niveles.map((n) => (
              <Link key={n.id} href={`/app/practica/${n.id}?tema=${tema}`} className={`btn small nivel-${n.id}`}>
                {n.nombre}
              </Link>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
