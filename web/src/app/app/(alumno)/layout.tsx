import Link from "next/link";

import { requireAlumno } from "@/lib/access";

// Todo lo que cuelga de aquí exige sesión y suscripción activa.
export default async function AlumnoLayout({ children }: { children: React.ReactNode }) {
  await requireAlumno();
  return (
    <section className="section" style={{ paddingTop: 28 }}>
      <div className="wrap">
        <nav className="subnav">
          <Link href="/app">Mi progreso</Link>
          <Link href="/app/temario">Temario</Link>
          <Link href="/app/fallos">Mis fallos</Link>
          <Link href="/app/cuenta">Mi cuenta</Link>
        </nav>
        {children}
      </div>
    </section>
  );
}
