import type { Metadata } from "next";
import localFont from "next/font/local";
import Image from "next/image";
import Link from "next/link";
import { Suspense } from "react";

import { currentUser } from "@/lib/access";
import { SITE_URL, supabaseReady } from "@/lib/config";

import "./globals.css";

const inter = localFont({
  src: [
    { path: "../fonts/Inter-Regular.otf", weight: "400" },
    { path: "../fonts/Inter-Medium.otf", weight: "500" },
    { path: "../fonts/Inter-SemiBold.otf", weight: "600" },
    { path: "../fonts/Inter-Bold.otf", weight: "700" },
    { path: "../fonts/Inter-ExtraBold.otf", weight: "800" },
  ],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: "acticdesdecasa · Prepara el ACTIC", template: "%s · acticdesdecasa" },
  description:
    "Tests tipo examen, temario y simulacros para preparar el ACTIC básico, medio y avanzado desde casa. Web no oficial.",
};

// Botón de la cabecera: depende de la sesión, así que se resuelve aparte del resto de la página.
async function NavUser() {
  const user = await currentUser();
  return user ? (
    <Link href="/app" className="btn small">
      Mi zona
    </Link>
  ) : (
    <Link href="/entrar" className="btn small">
      Entrar
    </Link>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={inter.variable}>
      <body>
        <header className="header">
          <div className="wrap">
            <Link href="/" className="logo">
              <Image src="/logo.png" alt="" width={36} height={36} priority />
              <span>
                actic<b>desdecasa</b>
              </span>
            </Link>
            <nav className="nav">
              <Link href="/test-gratis" className="hide-sm">
                Test gratis
              </Link>
              <Link href="/precios">Precios</Link>
              <Suspense
                fallback={
                  <Link href="/entrar" className="btn small">
                    Entrar
                  </Link>
                }
              >
                <NavUser />
              </Suspense>
            </nav>
          </div>
        </header>

        {!supabaseReady && process.env.NODE_ENV !== "production" && (
          <div className="wrap" style={{ marginTop: 16 }}>
            <div className="notice">
              <strong>Modo sin configurar:</strong> faltan las claves de Supabase en <code>.env.local</code>. La
              portada, el test gratis y los precios funcionan; el registro y la zona de alumnos no. Mira el README.
            </div>
          </div>
        )}

        <main>
          <Suspense fallback={<div className="wrap section muted">Cargando…</div>}>{children}</Suspense>
        </main>

        <footer className="footer">
          <div className="wrap">
            <div className="links">
              <Link href="/legal/aviso-legal">Aviso legal</Link>
              <Link href="/legal/privacidad">Privacidad</Link>
              <Link href="/legal/cookies">Cookies</Link>
              <Link href="/legal/condiciones">Condiciones de compra</Link>
            </div>
            <p>
              acticdesdecasa es una web de preparación independiente. No está vinculada a la Generalitat de
              Catalunya ni es material oficial del ACTIC.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
