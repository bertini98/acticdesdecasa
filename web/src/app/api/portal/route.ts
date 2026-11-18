import { NextResponse } from "next/server";

import { currentUser, suscripcion } from "@/lib/access";
import { SITE_URL } from "@/lib/config";
import { stripe } from "@/lib/stripe";

// Botón "Gestionar suscripción" → portal de cliente de Stripe (cambiar plan, cancelar, facturas).
export async function POST() {
  const user = await currentUser();
  if (!user) return NextResponse.redirect(new URL("/entrar", SITE_URL), 303);

  const sub = await suscripcion(user.id);
  if (!sub?.stripe_customer_id) return NextResponse.redirect(new URL("/precios", SITE_URL), 303);

  const portal = await stripe().billingPortal.sessions.create({
    customer: sub.stripe_customer_id,
    return_url: `${SITE_URL}/app/cuenta`,
    locale: "es",
  });
  return NextResponse.redirect(portal.url, 303);
}
