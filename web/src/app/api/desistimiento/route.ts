import { NextResponse, type NextRequest } from "next/server";

import { SITE_URL, supabaseReady } from "@/lib/config";
import { supabaseAdmin } from "@/lib/supabase/server";

// Función de desistimiento online (Directiva 2023/2673, art. 106 bis TRLGDCU). Se guarda la solicitud y se
// muestra un acuse con referencia y hora; el titular la revisa en Supabase (tabla withdrawals), confirma por
// email y, si procede, devuelve el importe desde Stripe en 14 días como máximo.
export async function POST(request: NextRequest) {
  const form = await request.formData();
  const get = (k: string, max: number) => String(form.get(k) ?? "").trim().slice(0, max);
  const email = get("email", 200).toLowerCase();
  const back = new URL("/desistimiento", SITE_URL);

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    back.searchParams.set("error", "email");
    return NextResponse.redirect(back, 303);
  }
  try {
    if (!supabaseReady) throw new Error("Supabase sin configurar");
    const { data, error } = await supabaseAdmin()
      .from("withdrawals")
      .insert({
        email,
        nombre: get("nombre", 120) || null,
        plan: get("plan", 20) || null,
        fecha_contrato: get("fecha", 10) || null,
        comentario: get("comentario", 1000) || null,
      })
      .select("id, created_at")
      .single();
    if (error) throw new Error(error.message);
    back.searchParams.set("ref", data.id.slice(0, 8).toUpperCase());
    back.searchParams.set("t", data.created_at);
  } catch (e) {
    console.error("desistimiento:", e);
    back.searchParams.set("error", "guardar");
  }
  return NextResponse.redirect(back, 303);
}
