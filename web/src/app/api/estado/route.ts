import { NextResponse, connection } from "next/server";

import { SITE_URL, salesOpen, stripeReady, supabaseReady } from "@/lib/config";
import { PLANS, priceIdFor } from "@/lib/plans";
import { stripe } from "@/lib/stripe";
import { supabaseAdmin } from "@/lib/supabase/server";

// Diagnóstico de la configuración (sin mostrar ninguna clave): abre /api/estado en el navegador.
export async function GET() {
  await connection(); // comprobarlo en cada visita, no guardar la respuesta de la compilación
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";
  const secret = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
  const tipo = (k: string) =>
    !k ? "falta" : k.startsWith("sb_publishable_") ? "publishable" : k.startsWith("sb_secret_") ? "secret"
      : k.startsWith("eyJ") ? "legacy (eyJ…)" : `formato raro (${k.length} caracteres)`;

  let baseDeDatos = "sin comprobar";
  if (supabaseReady && secret) {
    try {
      const { error } = await supabaseAdmin().from("waitlist").select("email", { count: "exact", head: true });
      baseDeDatos = error ? `error: ${error.message}` : "ok";
    } catch (e) {
      baseDeDatos = `error: ${(e as Error).message}`;
    }
  }

  // Modo de la clave (sin mostrarla) y si cada precio existe con esa clave (un precio de prueba no vale con clave real).
  const sk = process.env.STRIPE_SECRET_KEY ?? "";
  const modoStripe = !sk ? "falta" : /^(sk|rk)_live_/.test(sk) ? "REAL" : /^(sk|rk)_test_/.test(sk) ? "prueba"
    : `formato raro (${sk.slice(0, 3)}…)`;
  const precios: Record<string, string> = {};
  for (const plan of PLANS) {
    const id = priceIdFor(plan);
    if (!id) { precios[plan.id] = "falta"; continue; }
    if (!sk) { precios[plan.id] = "sin comprobar"; continue; }
    try {
      const p = await stripe().prices.retrieve(id);
      precios[plan.id] = p.active ? `ok (${(p.unit_amount ?? 0) / 100} €)` : "inactivo";
    } catch (e) {
      precios[plan.id] = `error: ${(e as Error).message}`;
    }
  }

  return NextResponse.json({
    web: SITE_URL,
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? "ok" : "falta",
    clavePublica: tipo(anon),
    claveSecreta: tipo(secret),
    baseDeDatos,
    ventasAbiertas: salesOpen,
    stripe: stripeReady ? "configurado" : "sin configurar",
    modoStripe,
    webhook: process.env.STRIPE_WEBHOOK_SECRET?.startsWith("whsec_") ? "ok" : "falta o formato raro",
    precios,
  });
}
