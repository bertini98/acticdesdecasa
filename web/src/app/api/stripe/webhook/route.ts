import { NextResponse, type NextRequest } from "next/server";
import type Stripe from "stripe";

import { planByPriceId } from "@/lib/plans";
import { periodEnd, stripe } from "@/lib/stripe";
import { supabaseAdmin } from "@/lib/supabase/server";

// Stripe avisa aquí de cada cambio (pago, renovación, cancelación...) y actualizamos el acceso.
export async function POST(request: NextRequest) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  const signature = request.headers.get("stripe-signature");
  if (!secret || !signature) return NextResponse.json({ error: "sin firma" }, { status: 400 });

  let event: Stripe.Event;
  try {
    event = stripe().webhooks.constructEvent(await request.text(), signature, secret);
  } catch {
    return NextResponse.json({ error: "firma no válida" }, { status: 400 });
  }

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object;
      if (session.mode === "subscription" && session.subscription) {
        const id = typeof session.subscription === "string" ? session.subscription : session.subscription.id;
        await saveSubscription(await stripe().subscriptions.retrieve(id), session.client_reference_id);
      }
      break;
    }
    case "customer.subscription.created":
    case "customer.subscription.updated":
    case "customer.subscription.deleted":
      await saveSubscription(event.data.object, null);
      break;
  }
  return NextResponse.json({ received: true });
}

async function saveSubscription(sub: Stripe.Subscription, fallbackUserId: string | null) {
  const userId = sub.metadata?.user_id || fallbackUserId;
  if (!userId) return; // suscripción creada fuera de la web: no sabemos de qué usuario es

  const customer = typeof sub.customer === "string" ? sub.customer : sub.customer.id;
  const { error } = await supabaseAdmin()
    .from("subscriptions")
    .upsert({
      user_id: userId,
      stripe_customer_id: customer,
      stripe_subscription_id: sub.id,
      plan: planByPriceId(sub.items.data[0]?.price.id ?? "") ?? null,
      status: sub.status,
      current_period_end: periodEnd(sub),
      cancel_at_period_end: sub.cancel_at_period_end,
      updated_at: new Date().toISOString(),
    });
  if (error) throw new Error(`No se pudo guardar la suscripción: ${error.message}`);
}
