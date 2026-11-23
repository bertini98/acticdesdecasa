// Planes de suscripción. Los precios reales viven en Stripe: aquí solo se muestran.
// Si cambias un precio en Stripe, cambia también `precio` y `detalle` para que la web coincida.

export type PlanId = "mensual" | "trimestral" | "anual";

export type Plan = {
  id: PlanId;
  nombre: string;
  precio: string;
  periodo: string;
  detalle: string;
  destacado?: boolean;
  /** Ahorro frente a pagar el mensual durante el mismo tiempo (comparación real, no un precio "antes"). */
  ahorro?: string;
  priceEnv: string;
};

export const PLANS: Plan[] = [
  {
    id: "mensual",
    nombre: "Mensual",
    precio: "6,99 €",
    periodo: "/mes",
    detalle: "Para quien tiene el examen ya",
    priceEnv: "STRIPE_PRICE_MENSUAL",
  },
  {
    id: "trimestral",
    nombre: "Trimestral",
    precio: "9,99 €",
    periodo: "/3 meses",
    detalle: "Sale a 3,33 €/mes · el tiempo justo para prepararlo",
    destacado: true,
    ahorro: "Ahorras 10,98 € (-52 %) frente al mensual",
    priceEnv: "STRIPE_PRICE_TRIMESTRAL",
  },
  {
    id: "anual",
    nombre: "Anual",
    precio: "19,99 €",
    periodo: "/año",
    detalle: "Sale a 1,67 €/mes · para sacarte los tres niveles",
    ahorro: "Ahorras 63,89 € (-76 %) frente al mensual",
    priceEnv: "STRIPE_PRICE_ANUAL",
  },
];

export function planById(id: string): Plan | undefined {
  return PLANS.find((p) => p.id === id);
}

export function priceIdFor(plan: Plan): string | undefined {
  return process.env[plan.priceEnv];
}

export function planByPriceId(priceId: string): PlanId | undefined {
  return PLANS.find((p) => process.env[p.priceEnv] === priceId)?.id;
}
