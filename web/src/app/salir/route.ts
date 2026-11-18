import { NextResponse } from "next/server";

import { SITE_URL, supabaseReady } from "@/lib/config";
import { supabaseServer } from "@/lib/supabase/server";

export async function POST() {
  if (supabaseReady) await (await supabaseServer()).auth.signOut();
  return NextResponse.redirect(new URL("/", SITE_URL), 303);
}
