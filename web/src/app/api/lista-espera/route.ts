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
  if (supabaseReady) {
    await supabaseAdmin().from("waitlist").upsert({ email, source }, { onConflict: "email", ignoreDuplicates: true });
  }
  back.searchParams.set("ok", "1");
  return NextResponse.redirect(back, 303);
}
