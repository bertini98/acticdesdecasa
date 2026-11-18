import { NextResponse, type NextRequest } from "next/server";

import { activa, currentUser, suscripcion } from "@/lib/access";
import { SITE_URL, salesOpen } from "@/lib/config";
import { planById, priceIdFor } from "@/lib/plans";
import { stripe } from "@/lib/stripe";

// Formulario de /precios → página de pago de Stripe.
export async function POST(request: NextRequest) {
  const form = await request.formData();
  const plan = planById(String(form.get("plan") ?? ""));
  if (!salesOpen || !plan) return NextResponse.redirect(new URL("/precios", SITE_URL), 303);

  const user = await currentUser();
  if (!user) {
    return NextResponse.redirect(new URL(`/entrar?next=/precios&plan=${plan.id}`, SITE_URL), 303);
  }

  const price = priceIdFor(plan);
  if (!price) return NextResponse.json({ error: `Falta ${plan.priceEnv}` }, { status: 500 });

  const existing = await suscripcion(user.id);
  // Ya suscrito: los cambios de plan se hacen en el portal, no con una segunda suscripción.
  if (activa(existing)) return NextResponse.redirect(new URL("/app/cuenta", SITE_URL), 303);

  const session = await stripe().checkout.sessions.create({
    mode: "subscription",
    line_items: [{ price, quantity: 1 }],
    client_reference_id: user.id,
    ...(existing?.stripe_customer_id
      ? { customer: existing.stripe_customer_id }
      : { customer_email: user.email }),
    subscription_data: { metadata: { user_id: user.id } },
    allow_promotion_codes: true,
    automatic_tax: { enabled: process.env.STRIPE_AUTOMATIC_TAX === "true" },
    ...(process.env.STRIPE_AUTOMATIC_TAX === "true" && existing?.stripe_customer_id
      ? { customer_update: { address: "auto" as const } }
      : {}),
    // Casilla obligatoria de aceptación de condiciones (incluye la renuncia al desistimiento).
    // Requiere poner la URL de /legal/condiciones en Stripe → Configuración → Detalles públicos.
    ...(process.env.STRIPE_TERMS_CONSENT === "true"
      ? {
          consent_collection: { terms_of_service: "required" as const },
          custom_text: {
            terms_of_service_acceptance: {
              message:
                "Acepto las condiciones de compra y empezar a usar el contenido ya, por lo que pierdo el derecho de desistimiento.",
            },
          },
        }
      : {}),
    success_url: `${SITE_URL}/app?bienvenida=1`,
    cancel_url: `${SITE_URL}/precios`,
    locale: "es",
  });

  return NextResponse.redirect(session.url!, 303);
}
