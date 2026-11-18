"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

export type QuizPregunta = {
  id: string;
  nivel: string;
  pregunta: string;
  opciones: string[];
  correcta: number;
  explicacion: string;
};

type Modo = "gratis" | "practica" | "simulacro";

type Props = {
  preguntas: QuizPregunta[];
  modo: Modo;
  /** Simulacro: segundos totales. */
  tiempo?: number;
  /** Guardar respuestas en el servidor (zona de alumnos). */
  guardar?: boolean;
  /** Número de preguntas que se sacan, al azar, de `preguntas`. */
  limite?: number;
};

const LETRAS = "ABCD";

function mezclar<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function mmss(s: number): string {
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, "0")}`;
}

// Se renderiza solo en el navegador (ver QuizClient), así el orden aleatorio no choca con el del servidor.
// Para empezar otra tanda con preguntas distintas, cambia la `key` del componente o recarga.
export default function Quiz({ preguntas, modo, tiempo, guardar = false, limite }: Props) {
  const [orden] = useState(() => mezclar(preguntas).slice(0, limite ?? preguntas.length));
  const [actual, setActual] = useState(0);
  const [respuestas, setRespuestas] = useState<(number | null)[]>(() => orden.map(() => null));
  const [revelada, setRevelada] = useState(false);
  const [entregado, setEntregado] = useState(false);
  const [restante, setRestante] = useState(tiempo ?? 0);
  const guardado = useRef(false);

  const simulacro = modo === "simulacro";
  const terminado = entregado || (simulacro && !!tiempo && restante === 0);

  useEffect(() => {
    if (!simulacro || !tiempo || terminado) return;
    const id = setInterval(() => setRestante((r) => Math.max(0, r - 1)), 1000);
    return () => clearInterval(id);
  }, [simulacro, tiempo, terminado]);

  const aciertos = useMemo(
    () => orden.filter((p, i) => respuestas[i] === p.correcta).length,
    [orden, respuestas],
  );

  useEffect(() => {
    if (!terminado || !guardar || guardado.current) return;
    guardado.current = true;
    const intentos = orden
      .map((p, i) => ({ id: p.id, correcta: respuestas[i] === p.correcta, respondida: respuestas[i] !== null }))
      .filter((i) => i.respondida)
      .map(({ id, correcta }) => ({ id, correcta }));
    fetch("/api/intentos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modo, intentos }),
    }).catch(() => {});
  }, [terminado, guardar, orden, respuestas, modo]);

  if (!orden.length) return <div className="quiz card">Todavía no hay preguntas aquí.</div>;

  if (terminado) {
    const nota = Math.round((aciertos / orden.length) * 100) / 10;
    return (
      <div className="quiz">
        <div className="card center">
          <p className="muted">{simulacro ? "Resultado del simulacro" : "Tu resultado"}</p>
          <div className="score">
            {aciertos}/{orden.length}
          </div>
          <p style={{ marginTop: 12 }}>
            {simulacro ? <>Nota: <strong>{nota.toFixed(1)}</strong> sobre 10. </> : null}
            {aciertos === orden.length
              ? "¡Perfecto! Vas muy bien."
              : aciertos >= orden.length / 2
                ? "Buen nivel, pero hay cosas que repasar."
                : "Toca repasar: mira las explicaciones de abajo."}
          </p>
          {modo === "gratis" ? (
            <div className="grid" style={{ marginTop: 16 }}>
              <Link href="/precios" className="btn block">
                Desbloquear todos los tests y el temario
              </Link>
              <button className="btn secondary block" onClick={() => location.reload()}>
                Repetir el test gratis
              </button>
            </div>
          ) : (
            <div className="grid" style={{ marginTop: 16 }}>
              <button className="btn block" onClick={() => location.reload()}>
                Repetir con otras preguntas
              </button>
              <Link href="/app" className="btn secondary block">
                Volver a mi zona
              </Link>
            </div>
          )}
        </div>

        <ul className="review">
          {orden.map((p, i) => {
            const ok = respuestas[i] === p.correcta;
            return (
              <li key={p.id} className={ok ? "" : "ko"}>
                <strong>{p.pregunta}</strong>
                <div>
                  {ok ? "✓ " : "✗ "}
                  {respuestas[i] === null ? "Sin responder. " : null}
                  Correcta: {LETRAS[p.correcta]}) {p.opciones[p.correcta]}
                </div>
                <div className="muted">{p.explicacion}</div>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }

  const p = orden[actual];
  const elegida = respuestas[actual];
  const ultima = actual === orden.length - 1;

  const elegir = (i: number) => {
    if (revelada) return;
    setRespuestas((r) => r.map((v, k) => (k === actual ? i : v)));
    if (!simulacro) setRevelada(true);
  };

  const siguiente = () => {
    setRevelada(false);
    if (ultima) setEntregado(true);
    else setActual((a) => a + 1);
  };

  return (
    <div className={`quiz nivel-${p.nivel}`}>
      <div className="quiz-top">
        <span>
          Pregunta {actual + 1} de {orden.length}
        </span>
        {simulacro && tiempo ? (
          <span className={`timer ${restante < 60 ? "low" : ""}`}>⏱ {mmss(restante)}</span>
        ) : (
          <span className="pill soft">{p.nivel === "basico" ? "Básico" : p.nivel === "medio" ? "Medio" : "Avanzado"}</span>
        )}
      </div>
      <div className="progress" style={{ marginBottom: 20 }}>
        <div style={{ width: `${(actual / orden.length) * 100}%` }} />
      </div>

      <div className="card">
        <div className="quiz-q">{p.pregunta}</div>
        <div className="options">
          {p.opciones.map((op, i) => {
            let cls = "option";
            if (revelada && i === p.correcta) cls += " correct";
            else if (revelada && i === elegida) cls += " wrong";
            else if (!revelada && i === elegida) cls += " selected";
            return (
              <button key={i} className={cls} onClick={() => elegir(i)} disabled={revelada}>
                <span className="letter">{LETRAS[i]}</span>
                {op}
              </button>
            );
          })}
        </div>

        {revelada && (
          <div className="explain">
            <strong>{elegida === p.correcta ? "¡Correcto!" : `Era la ${LETRAS[p.correcta]}`}</strong>
            {p.explicacion}
          </div>
        )}

        <div className="quiz-actions">
          {simulacro && (
            <button className="btn secondary" onClick={() => setEntregado(true)}>
              Entregar
            </button>
          )}
          <button className="btn" onClick={siguiente} disabled={simulacro ? false : !revelada}>
            {ultima ? "Ver resultado" : simulacro && elegida === null ? "Saltar" : "Siguiente"}
          </button>
        </div>
      </div>
    </div>
  );
}
