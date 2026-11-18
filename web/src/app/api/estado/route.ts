import { NextResponse } from "next/server";

import { SITE_URL, salesOpen, stripeReady, supabaseReady } from "@/lib/config";
import { supabaseAdmin } from "@/lib/supabase/server";

// Diagnóstico de la configuración (sin mostrar ninguna clave): abre /api/estado en el navegador.
export async function GET() {
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

  return NextResponse.json({
    web: SITE_URL,
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? "ok" : "falta",
    clavePublica: tipo(anon),
    claveSecreta: tipo(secret),
    baseDeDatos,
    ventasAbiertas: salesOpen,
    stripe: stripeReady ? "configurado" : "sin configurar",
  });
}
