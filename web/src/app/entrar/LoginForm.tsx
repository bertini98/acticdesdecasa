"use client";

import { useState } from "react";

import { supabaseReady } from "@/lib/config";
import { supabaseBrowser } from "@/lib/supabase/browser";

export default function LoginForm({ next }: { next: string }) {
  const [email, setEmail] = useState("");
  const [estado, setEstado] = useState<"idle" | "enviando" | "enviado" | "error">("idle");

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!supabaseReady) return setEstado("error");
    setEstado("enviando");
    const redirect = `${location.origin}/auth/callback?next=${encodeURIComponent(next)}`;
    const { error } = await supabaseBrowser().auth.signInWithOtp({
      email,
      options: { emailRedirectTo: redirect },
    });
    setEstado(error ? "error" : "enviado");
  };

  if (estado === "enviado") {
    return (
      <div className="notice ok">
        <strong>Revisa tu email.</strong> Te hemos enviado un enlace a {email}. Ábrelo en este mismo navegador.
      </div>
    );
  }

  return (
    <form onSubmit={enviar}>
      <label className="field">
        Email
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="tu@email.com"
          autoComplete="email"
        />
      </label>
      {estado === "error" && (
        <div className="notice error" style={{ marginBottom: 14 }}>
          No se ha podido enviar el enlace. Inténtalo de nuevo en un momento.
        </div>
      )}
      <button className="btn block" disabled={estado === "enviando"}>
        {estado === "enviando" ? "Enviando…" : "Enviarme el enlace"}
      </button>
    </form>
  );
}
