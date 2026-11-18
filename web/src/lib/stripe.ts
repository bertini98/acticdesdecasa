import "server-only";

import Stripe from "stripe";

let client: Stripe | null = null;

export function stripe(): Stripe {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("Falta STRIPE_SECRET_KEY");
  client ??= new Stripe(key);
  return client;
}

// Desde la API 2025-03-31 la fecha de fin de periodo está en cada línea de la suscripción.
export function periodEnd(sub: Stripe.Subscription): string | null {
  const ends = sub.items.data.map((item) => item.current_period_end).filter(Boolean);
  return ends.length ? new Date(Math.max(...ends) * 1000).toISOString() : null;
}
