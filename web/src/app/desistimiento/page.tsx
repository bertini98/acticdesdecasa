import type { Metadata } from "next";
import Link from "next/link";

import { PLANS } from "@/lib/plans";

export const metadata: Metadata = { title: "Desistir del contrato" };

const EMAIL = "synetispotify@gmail.com";

export default async function Desistimiento({
  searchParams,
}: {
  searchParams: Promise<{ ref?: string; t?: string; error?: string }>;
}) {
  const { ref, t, error } = await searchParams;
  const cuando = t
    ? new Date(t).toLocaleString("es-ES", { dateStyle: "long", timeStyle: "short", timeZone: "Europe/Madrid" })
    : null;

  return (
    <section className="section">
      <div className="wrap" style={{ maxWidth: 560 }}>
        <div className="card">
          {ref ? (
            <>
              <h1 style={{ fontSize: "1.8rem" }}>Solicitud recibida</h1>
              <p>
                Hemos recibido tu solicitud de desistimiento{cuando ? ` el ${cuando}` : ""}.
              </p>
              <p>
                <strong>Referencia: {ref}</strong>
              </p>
              <p className="muted">
                Guarda esta pantalla. Te enviaremos la confirmación por email y, si procede, te devolveremos el importe
                en un plazo máximo de 14 días por el mismo medio de pago.
              </p>
              <Link href="/" className="btn block secondary">
                Volver al inicio
              </Link>
            </>
          ) : (
            <>
              <h1 style={{ fontSize: "1.8rem" }}>Desistir del contrato</h1>
              <p className="muted">
                Usa este formulario si quieres desistir de tu suscripción en los 14 días siguientes a la contratación.
                Lee antes el punto 6 de las <Link href="/legal/condiciones">condiciones</Link>: si al pagar pediste
                empezar a usar el contenido de inmediato, no se aplica el desistimiento.
              </p>
              <p className="muted">
                ¿Solo quieres que no se renueve? Cancela en <Link href="/app/cuenta">Mi cuenta</Link>: mantienes el
                acceso hasta el final del periodo pagado.
              </p>
              {error && (
                <div className="notice error" style={{ marginBottom: 14 }}>
                  {error === "email"
                    ? "Revisa el email."
                    : `No hemos podido registrar la solicitud. Envíala por email a ${EMAIL} y la atenderemos igual.`}
                </div>
              )}
              <form action="/api/desistimiento" method="post">
                <label className="field">
                  Email de tu cuenta *
                  <input type="email" name="email" required autoComplete="email" placeholder="tu@email.com" />
                </label>
                <label className="field">
                  Nombre
                  <input type="text" name="nombre" autoComplete="name" />
                </label>
                <label className="field">
                  Plan contratado
                  <select name="plan" defaultValue="">
                    <option value="">—</option>
                    {PLANS.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nombre} ({p.precio})
                      </option>
                    ))}
                  </select>
                </label>
                <label className="field">
                  Fecha de contratación
                  <input type="date" name="fecha" />
                </label>
                <label className="field">
                  Comentario (opcional)
                  <input type="text" name="comentario" />
                </label>
                <button className="btn block">Confirmar desistimiento</button>
              </form>
              <p className="muted" style={{ fontSize: "0.85rem", marginTop: 12 }}>
                También puedes desistir escribiendo a {EMAIL}. Tratamos estos datos solo para gestionar tu solicitud (
                <Link href="/legal/privacidad">privacidad</Link>).
              </p>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
