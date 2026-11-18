import type { Metadata } from "next";

import Plans from "@/components/Plans";
import { salesOpen } from "@/lib/config";

export const metadata: Metadata = { title: "Precios" };

export default async function Precios({ searchParams }: { searchParams: Promise<{ motivo?: string }> }) {
  const { motivo } = await searchParams;
  return (
    <section className="section">
      <div className="wrap">
        <h1 className="center">Elige tu plan</h1>
        <p className="muted center" style={{ marginBottom: 24 }}>
          Acceso completo a los tres niveles: tests, simulacros y temario.
        </p>
        {motivo === "sin-plan" && (
          <div className="notice" style={{ maxWidth: 640, margin: "0 auto 28px" }}>
            Para entrar en la zona de alumnos necesitas un plan activo.
          </div>
        )}
        {!salesOpen && (
          <div className="notice ok" style={{ maxWidth: 640, margin: "0 auto 28px" }}>
            Estamos a punto de abrir. Apúntate y te avisamos con un descuento de lanzamiento.
          </div>
        )}
        <Plans />
        <p className="muted center" style={{ marginTop: 28, fontSize: "0.9rem" }}>
          Pago seguro con Stripe. La suscripción se renueva automáticamente y puedes cancelarla en cualquier
          momento desde tu cuenta. Precios con IVA incluido.
        </p>
      </div>
    </section>
  );
}
