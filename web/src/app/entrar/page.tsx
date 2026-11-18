import type { Metadata } from "next";

import LoginForm from "./LoginForm";

export const metadata: Metadata = { title: "Entrar" };

export default async function Entrar({
  searchParams,
}: {
  searchParams: Promise<{ next?: string; error?: string }>;
}) {
  const { next, error } = await searchParams;
  return (
    <section className="section">
      <div className="wrap" style={{ maxWidth: 480 }}>
        <div className="card">
          <h1 style={{ fontSize: "1.8rem" }}>Entrar</h1>
          <p className="muted">Sin contraseñas: te mandamos un enlace al email y entras con un clic.</p>
          {error && (
            <div className="notice error" style={{ marginBottom: 14 }}>
              El enlace ha caducado o ya se usó. Pide uno nuevo.
            </div>
          )}
          <LoginForm next={next?.startsWith("/") ? next : "/app"} />
        </div>
      </div>
    </section>
  );
}
