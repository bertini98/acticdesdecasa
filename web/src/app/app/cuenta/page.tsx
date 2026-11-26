import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { activa, currentUser, suscripcion } from "@/lib/access";
import { planById } from "@/lib/plans";

export const metadata: Metadata = { title: "Mi cuenta" };

const ESTADOS: Record<string, string> = {
  active: "Activa",
  trialing: "En prueba",
  past_due: "Pago pendiente",
  unpaid: "Impagada",
  canceled: "Cancelada",
  incomplete: "Pago sin completar",
  incomplete_expired: "Caducada",
  paused: "En pausa",
};

// Accesible sin suscripción activa: desde aquí se gestiona o se renueva.
export default async function Cuenta() {
  const user = await currentUser();
  if (!user) redirect("/entrar?next=/app/cuenta");
  const sub = await suscripcion(user.id);
  const ok = activa(sub);
  const fecha = sub?.current_period_end
    ? new Date(sub.current_period_end).toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" })
    : null;

  return (
    <section className="section" style={{ paddingTop: 28 }}>
      <div className="wrap" style={{ maxWidth: 620 }}>
        {ok && (
          <nav className="subnav">
            <Link href="/app">Mi progreso</Link>
            <Link href="/app/temario">Temario</Link>
            <Link href="/app/fallos">Mis fallos</Link>
            <Link href="/app/cuenta">Mi cuenta</Link>
          </nav>
        )}
        <h1 style={{ fontSize: "1.8rem" }}>Mi cuenta</h1>
        <div className="card">
          <p>
            <strong>Email:</strong> {user.email}
          </p>
          {sub ? (
            <>
              <p>
                <strong>Plan:</strong> {planById(sub.plan ?? "")?.nombre ?? "—"} ·{" "}
                <strong>Estado:</strong> {ESTADOS[sub.status] ?? sub.status}
              </p>
              {fecha && (
                <p className="muted">
                  {sub.cancel_at_period_end ? `Acceso hasta el ${fecha} (no se renovará).` : `Próxima renovación: ${fecha}.`}
                </p>
              )}
              <form action="/api/portal" method="post">
                <button className="btn block">Gestionar suscripción y facturas</button>
              </form>
              <p className="muted" style={{ fontSize: "0.85rem", marginTop: 10 }}>
                Cambia de plan, actualiza tu tarjeta, descarga facturas o cancela. Te llevamos a la página segura de
                Stripe.
              </p>
              <p className="muted" style={{ fontSize: "0.85rem" }}>
                <Link href="/desistimiento">Desistir del contrato aquí</Link> (en los 14 días siguientes a la
                contratación, si procede).
              </p>
            </>
          ) : (
            <>
              <p className="muted">Todavía no tienes ningún plan.</p>
              <Link href="/precios" className="btn block">
                Ver planes
              </Link>
            </>
          )}
        </div>
        <form action="/salir" method="post" style={{ marginTop: 16 }}>
          <button className="btn secondary block">Cerrar sesión</button>
        </form>
      </div>
    </section>
  );
}
