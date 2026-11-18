import "server-only";

import type { User } from "@supabase/supabase-js";
import { redirect } from "next/navigation";
import { connection } from "next/server";

import { supabaseReady } from "@/lib/config";
import { supabaseServer } from "@/lib/supabase/server";

export type Suscripcion = {
  plan: string | null;
  status: string;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  stripe_customer_id: string | null;
};

export async function currentUser(): Promise<User | null> {
  await connection(); // siempre por petición, nunca en la compilación (aunque falten las claves)
  if (!supabaseReady) return null;
  const supabase = await supabaseServer();
  const { data } = await supabase.auth.getUser();
  return data.user;
}

export async function suscripcion(userId: string): Promise<Suscripcion | null> {
  const supabase = await supabaseServer();
  const { data } = await supabase
    .from("subscriptions")
    .select("plan, status, current_period_end, cancel_at_period_end, stripe_customer_id")
    .eq("user_id", userId)
    .maybeSingle();
  return data;
}

export function activa(s: Suscripcion | null): boolean {
  if (!s || !["active", "trialing"].includes(s.status)) return false;
  return !s.current_period_end || new Date(s.current_period_end) > new Date();
}

// Para páginas de la zona de alumnos: exige sesión y suscripción activa.
export async function requireAlumno(): Promise<User> {
  const user = await currentUser();
  if (!user) redirect("/entrar?next=/app");
  if (!activa(await suscripcion(user.id))) redirect("/precios?motivo=sin-plan");
  return user;
}
