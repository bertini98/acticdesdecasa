import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Lista de espera" };

export default async function ListaEspera({
  searchParams,
}: {
  searchParams: Promise<{ ok?: string; error?: string }>;
}) {
  const { ok, error } = await searchParams;
  return (
    <section className="section">
      <div className="wrap" style={{ maxWidth: 520 }}>
        <div className="card">
          {ok ? (
            <>
              <h1 style={{ fontSize: "1.8rem" }}>¡Apuntado! 🎉</h1>
              <p>Te escribiremos en cuanto abramos, con un descuento de lanzamiento.</p>
              <p className="muted">Mientras tanto, ponte a prueba:</p>
              <Link href="/test-gratis" className="btn block">
                Hacer el test gratis
              </Link>
            </>
          ) : (
            <>
              <h1 style={{ fontSize: "1.8rem" }}>Avísame cuando abra</h1>
              <p className="muted">
                Estamos terminando los tests de los tres niveles. Déjanos tu email y te avisamos el primero, con un
                descuento de lanzamiento.
              </p>
              {error && <div className="notice error" style={{ marginBottom: 14 }}>Revisa el email.</div>}
              <form action="/api/lista-espera" method="post">
                <input type="hidden" name="source" value="web" />
                <label className="field">
                  Email
                  <input type="email" name="email" required placeholder="tu@email.com" autoComplete="email" />
                </label>
                <button className="btn block">Apuntarme</button>
              </form>
              <p className="muted" style={{ fontSize: "0.85rem", marginTop: 12 }}>
                Solo usaremos tu email para avisarte del lanzamiento. Más info en la{" "}
                <Link href="/legal/privacidad">política de privacidad</Link>.
              </p>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
