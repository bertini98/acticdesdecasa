import { NextResponse, type NextRequest } from "next/server";

import { SITE_URL } from "@/lib/config";
import { supabaseServer } from "@/lib/supabase/server";

// Enlace mágico del email → crea la sesión y lleva a donde iba el usuario.
export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const next = request.nextUrl.searchParams.get("next") ?? "/app";
  const safeNext = next.startsWith("/") && !next.startsWith("//") ? next : "/app";

  if (code) {
    const supabase = await supabaseServer();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) return NextResponse.redirect(new URL(safeNext, SITE_URL));
  }
  return NextResponse.redirect(new URL("/entrar?error=enlace", SITE_URL));
}
