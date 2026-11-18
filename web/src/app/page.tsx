import Link from "next/link";

import Bars from "@/components/Bars";
import Plans from "@/components/Plans";
import { NIVELES, preguntasDe } from "@/lib/content";

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="wrap">
          <span className="pill">Prepara el ACTIC desde casa</span>
          <h1 style={{ marginTop: 16 }}>
            Aprueba el ACTIC
            <br />a la primera.
          </h1>
          <p className="lead">
            Tests tipo examen con explicaciones, simulacros con cronómetro y el temario que de verdad cae. Nivel
            básico, medio y avanzado.
          </p>
          <div className="ctas">
            <Link href="/test-gratis" className="btn">
              Haz el test gratis →
            </Link>
            <Link href="/precios" className="btn secondary">
              Ver precios
            </Link>
          </div>
          <p className="muted" style={{ marginTop: 12, fontSize: "0.9rem" }}>
            10 preguntas · sin registrarte · 3 minutos
          </p>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 16 }}>
        <div className="wrap">
          <div className="grid cols-3">
            {NIVELES.map((n) => (
              <div key={n.id} className={`card nivel-card nivel-${n.id}`}>
                <Bars nivel={n.id} />
                <h3 style={{ marginTop: 12 }}>Nivel {n.nombre.toLowerCase()}</h3>
                <p className="muted">{n.detalle}</p>
                <div className="stat">{preguntasDe(n.id).length}</div>
                <div className="muted">preguntas tipo examen (y subiendo)</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <h2>Cómo funciona</h2>
          <div className="grid cols-3" style={{ marginTop: 24 }}>
            <div className="card feature">
              <div className="icon">📝</div>
              <h3>Practica por temas</h3>
              <p className="muted">Cada respuesta viene con su explicación, para que entiendas el porqué y no solo memorices.</p>
            </div>
            <div className="card feature">
              <div className="icon">⏱</div>
              <h3>Simulacros</h3>
              <p className="muted">Ponte a prueba con cronómetro, como el día del examen, y mira tu nota al final.</p>
            </div>
            <div className="card feature">
              <div className="icon">🎯</div>
              <h3>Repasa tus fallos</h3>
              <p className="muted">Guardamos lo que fallas para que lo repases hasta que lo tengas dominado.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section" id="precios">
        <div className="wrap">
          <h2 className="center">Elige tu plan</h2>
          <p className="muted center" style={{ marginBottom: 32 }}>
            Acceso completo a los tres niveles. Cancela cuando quieras.
          </p>
          <Plans />
        </div>
      </section>
    </>
  );
}
