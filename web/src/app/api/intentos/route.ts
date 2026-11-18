import { NextResponse, type NextRequest } from "next/server";

import { activa, currentUser, suscripcion } from "@/lib/access";
import { supabaseServer } from "@/lib/supabase/server";

type Intento = { id: string; correcta: boolean };

// Guarda las respuestas de práctica y simulacros para el progreso y el repaso de fallos.
export async function POST(request: NextRequest) {
  const user = await currentUser();
  if (!user || !activa(await suscripcion(user.id))) {
    return NextResponse.json({ error: "sin acceso" }, { status: 401 });
  }

  const body = (await request.json()) as { modo?: string; intentos?: Intento[] };
  const intentos = (body.intentos ?? []).slice(0, 100);
  if (!intentos.length) return NextResponse.json({ ok: true });

  const supabase = await supabaseServer();
  const { error } = await supabase.from("attempts").insert(
    intentos.map((i) => ({
      user_id: user.id,
      question_id: String(i.id),
      correct: Boolean(i.correcta),
      mode: body.modo === "simulacro" ? "simulacro" : "practica",
    })),
  );
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true });
}
