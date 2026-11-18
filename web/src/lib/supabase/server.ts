import "server-only";

import { createServerClient } from "@supabase/ssr";
import { createClient as createAdminClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";

import { SUPABASE_ANON_KEY, SUPABASE_URL } from "@/lib/config";

// Cliente con la sesión del usuario (respeta las políticas RLS de la base de datos).
export async function supabaseServer() {
  const cookieStore = await cookies();
  return createServerClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    cookies: {
      getAll: () => cookieStore.getAll(),
      setAll: (cookiesToSet) => {
        try {
          cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options));
        } catch {
          // Desde un Server Component no se pueden escribir cookies; el proxy ya refresca la sesión.
        }
      },
    },
  });
}

// Cliente con permisos totales. Solo para el webhook de Stripe y la lista de espera.
export function supabaseAdmin() {
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!SUPABASE_URL || !key) throw new Error("Falta SUPABASE_SERVICE_ROLE_KEY");
  return createAdminClient(SUPABASE_URL, key, { auth: { persistSession: false } });
}
