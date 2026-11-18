import "server-only";

import { NIVELES, preguntasDe, type Nivel } from "@/lib/content";
import { supabaseServer } from "@/lib/supabase/server";

export type Progreso = {
  nivel: Nivel;
  total: number;
  vistas: number; // preguntas respondidas al menos una vez
  dominadas: number; // preguntas cuya última respuesta fue correcta
};

// Última respuesta de cada pregunta (true = acertada).
async function ultimas(userId: string): Promise<Map<string, boolean>> {
  const supabase = await supabaseServer();
  const { data } = await supabase
    .from("attempts")
    .select("question_id, correct")
    .eq("user_id", userId)
    .order("created_at", { ascending: false })
    .limit(5000);
  const map = new Map<string, boolean>();
  for (const row of data ?? []) if (!map.has(row.question_id)) map.set(row.question_id, row.correct);
  return map;
}

export async function progreso(userId: string): Promise<Progreso[]> {
  const last = await ultimas(userId);
  return NIVELES.map(({ id }) => {
    const ids = preguntasDe(id).map((p) => p.id);
    return {
      nivel: id,
      total: ids.length,
      vistas: ids.filter((q) => last.has(q)).length,
      dominadas: ids.filter((q) => last.get(q) === true).length,
    };
  });
}

export async function fallos(userId: string): Promise<string[]> {
  const last = await ultimas(userId);
  return [...last.entries()].filter(([, ok]) => !ok).map(([id]) => id);
}
