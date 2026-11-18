"use client";

import dynamic from "next/dynamic";

// El test baraja las preguntas al montarse, así que solo se renderiza en el navegador.
const Quiz = dynamic(() => import("./Quiz"), {
  ssr: false,
  loading: () => <div className="quiz card">Cargando preguntas…</div>,
});

export default Quiz;
