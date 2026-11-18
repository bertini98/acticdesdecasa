import { NextResponse, type NextRequest } from "next/server";

import { SITE_URL, supabaseReady } from "@/lib/config";
import { supabaseAdmin } from "@/lib/supabase/server";

// Formulario "Avísame cuando abra" (mientras NEXT_PUBLIC_SALES_OPEN no sea "true").
export async function POST(request: NextRequest) {
  const form = await request.formData();
  const email = String(form.get("email") ?? "").trim().toLowerCase();
  const source = String(form.get("source") ?? "web").slice(0, 40);
  const back = new URL("/lista-espera", SITE_URL);

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 200) {
    back.searchParams.set("error", "email");
    return NextResponse.redirect(back, 303);
  }
  // Nunca decir "apuntado" si no se ha guardado: se perderían emails sin enterarnos.
  try {
    if (!supabaseReady) throw new Error("Supabase sin configurar");
    const { error } = await supabaseAdmin()
      .from("waitlist")
      .upsert({ email, source }, { onConflict: "email", ignoreDuplicates: true });
    if (error) throw new Error(error.message);
  } catch (e) {
    console.error("lista de espera:", e);
    back.searchParams.set("error", "guardar");
    return NextResponse.redirect(back, 303);
  }
  back.searchParams.set("ok", "1");
  return NextResponse.redirect(back, 303);
}
