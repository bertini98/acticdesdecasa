// Configuración leída de las variables de entorno (.env.local en desarrollo).
// La web arranca aunque falten claves: las partes que dependen de ellas avisan en pantalla.

// En Vercel, si no se indica, se usa el dominio de producción del proyecto (variable de sistema de Vercel).
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ??
  (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : "http://localhost:3000");

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";
export const supabaseReady = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

// Mientras sea "false", los botones de compra apuntan a la lista de espera en vez de a Stripe.
export const salesOpen = process.env.NEXT_PUBLIC_SALES_OPEN === "true";

export const stripeReady = Boolean(process.env.STRIPE_SECRET_KEY);
