// Crea en Stripe el producto y los 3 precios (mensual, trimestral y anual) y configura el portal de cliente.
// Uso (modo prueba): STRIPE_SECRET_KEY=sk_test_... node scripts/stripe-setup.mjs
// Al final imprime las líneas que tienes que copiar en .env.local.
// Para cambiar precios, edita PRECIOS (en céntimos, IVA incluido) antes de ejecutarlo.

import Stripe from "stripe";

const PRECIOS = [
  { plan: "MENSUAL", nombre: "Mensual", importe: 499, interval: "month", count: 1 },
  { plan: "TRIMESTRAL", nombre: "Trimestral", importe: 999, interval: "month", count: 3 },
  { plan: "ANUAL", nombre: "Anual", importe: 1999, interval: "year", count: 1 },
];

const key = process.env.STRIPE_SECRET_KEY;
if (!key) {
  console.error("Falta STRIPE_SECRET_KEY. Ejemplo: STRIPE_SECRET_KEY=sk_test_... node scripts/stripe-setup.mjs");
  process.exit(1);
}
if (key.startsWith("sk_live")) console.warn("⚠ Estás usando la clave REAL (sk_live). Los precios se crearán en modo real.\n");

const stripe = new Stripe(key);

const product = await stripe.products.create({
  name: "acticdesdecasa · Acceso completo",
  description: "Tests, simulacros y temario de los tres niveles del ACTIC.",
});

const env = [];
const prices = [];
for (const p of PRECIOS) {
  const price = await stripe.prices.create({
    product: product.id,
    currency: "eur",
    unit_amount: p.importe,
    tax_behavior: "inclusive", // el precio ya incluye el IVA
    recurring: { interval: p.interval, interval_count: p.count },
    nickname: p.nombre,
    lookup_key: `actic_${p.plan.toLowerCase()}`,
  });
  prices.push(price.id);
  env.push(`STRIPE_PRICE_${p.plan}=${price.id}`);
}

// Portal: cancelar, cambiar de plan entre los 3 precios, actualizar tarjeta y ver facturas.
await stripe.billingPortal.configurations.create({
  business_profile: { headline: "acticdesdecasa · Gestiona tu suscripción" },
  features: {
    customer_update: { enabled: true, allowed_updates: ["email", "address", "tax_id"] },
    invoice_history: { enabled: true },
    payment_method_update: { enabled: true },
    subscription_cancel: { enabled: true, mode: "at_period_end" },
    subscription_update: {
      enabled: true,
      default_allowed_updates: ["price"],
      proration_behavior: "create_prorations",
      products: [{ product: product.id, prices }],
    },
  },
  default_return_url: `${process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"}/app/cuenta`,
});

console.log("\n✓ Producto, precios y portal creados. Copia esto en .env.local:\n");
console.log(env.join("\n"));
