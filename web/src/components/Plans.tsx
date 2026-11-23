import Link from "next/link";

import { salesOpen } from "@/lib/config";
import { PLANS } from "@/lib/plans";

const INCLUYE = [
  "Tests de los 3 niveles con explicaciones",
  "Simulacros con cronómetro",
  "Temario por competencias",
  "Repaso de tus fallos y progreso",
  "Cancela cuando quieras",
];

export default function Plans() {
  return (
    <div className="grid cols-3">
      {PLANS.map((plan) => (
        <div key={plan.id} className={`card plan ${plan.destacado ? "destacado" : ""}`}>
          {plan.destacado && <span className="badge">Más elegido</span>}
          <h3>{plan.nombre}</h3>
          <div className="precio">
            {plan.precio} <small>{plan.periodo}</small>
          </div>
          <div className="muted">{plan.detalle}</div>
          {plan.ahorro && <div className="ahorro">{plan.ahorro}</div>}
          <ul>
            {INCLUYE.map((i) => (
              <li key={i}>{i}</li>
            ))}
          </ul>
          {salesOpen ? (
            <form action="/api/checkout" method="post">
              <input type="hidden" name="plan" value={plan.id} />
              <button className={`btn block ${plan.destacado ? "" : "secondary"}`}>Elegir {plan.nombre.toLowerCase()}</button>
            </form>
          ) : (
            <Link href="/lista-espera" className={`btn block ${plan.destacado ? "" : "secondary"}`}>
              Avísame cuando abra
            </Link>
          )}
        </div>
      ))}
    </div>
  );
}
