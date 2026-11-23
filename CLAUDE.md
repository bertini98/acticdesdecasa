# acticdesdecasa — contexto para continuar

Proyecto de Albert (GitHub `bertini98`): cuenta de Instagram **@acticdesdecasa** con reels de preguntas tipo examen del ACTIC (acreditación de competencias digitales de la Generalitat de Catalunya) y una web con tests de pago. **Web no oficial**: no usar logos ni marca de la Generalitat. Todo en castellano. El usuario no es programador: explicar en lenguaje llano y darle pasos concretos.

## Estructura

- `actic/` — generador de vídeos (Python + PIL + ffmpeg + numpy)
  - `quiz.py` — banco de preguntas `QUIZ` (por nivel) y las ilustraciones (`ARTS`, una función `art_*` por pregunta; la ilustración no revela la respuesta hasta el final, parámetro `k` de 0 a 1).
  - `corto.py` — **formato actual de los reels**: una pregunta por vídeo, gancho inicial de ~3 s, cuenta atrás, respuesta con subtítulos, música sintetizada y cierre "Síguenos". `CAPTIONS` = subtítulos (grafía normal); `HOOKS` = estilo del gancho por vídeo (`classic`, `timer`, `pov`, `fail`, `trap_a`, `challenge`, `trap`, `versus`, `nota`, `comment`); un valor `("estilo", "archivo")` reutiliza una locución de gancho ya grabada (no gasta créditos). `VERSUS` = palabras del duelo.
    - Uso: `python3 corto.py basico:16 medio:16 ...` → `salida/cortos/actic_{nivel}_{n}.mp4` + portada.
  - `export_web.py` — vuelca las preguntas a `web/content/preguntas.json` (mapa `COMPETENCIA` por ilustración; `TEXTO_WEB` para preguntas que en el vídeo dependían del dibujo).
  - `teaser.py`, `sfx.py`, `voz.py`, `quiz.py` (vídeo largo de 3 preguntas) — formatos anteriores; `logo.py`, `logo2.py` — logos.
  - `salida/quiz_voz/` — locuciones (**guardadas en git: costaron créditos**). Nombres: `{nivel}_q{n}.mp3`, `{nivel}_a{n}.mp3`, `gancho.mp3`, `gancho_{nivel}_{n}.mp3`. El resto de `salida/` se regenera.
- `web/` — Next.js 16 (App Router, Cache Components, `proxy.ts` en vez de middleware) + Supabase + Stripe. Ver `web/README.md` y `web/AGENTS.md` (leer la doc de `node_modules/next/dist/docs/` antes de tocar APIs de Next).

## Voz (ElevenLabs)

- Voz **Pablo**, `voice_id` `TZ3pgF19H1pelFonL8Zq`, modelo `eleven_multilingual_v2`, **una sola toma** (`generations_count: 1`) para ahorrar créditos.
- Flow de ElevenLabs: `xeqDvkEaJesbAnLFhreL`. Los audios se descargan de `elevenlabsusercontent.com` (host permitido en el entorno).
- En la locución se escriben las siglas de forma fonética ("jota pe ge", "ce, ce, o", "u, erre, ele", "buscar uve"); los subtítulos van con la grafía normal.
- Una tanda de 9 reels cuesta ~1.200–1.700 créditos.

## Estado de los reels

45 reels hechos: preguntas 1–15 de cada nivel (básico verde, medio azul, avanzado rojo). Los 1–6 no tienen gancho (formato anterior); del 7 en adelante sí. Siguiente número libre: **16**. Al añadir preguntas: entrada en `QUIZ` + función `art_*` + registro en `ARTS` + subtítulo en `CAPTIONS` + (opcional) `HOOKS` + competencia en `export_web.py`. Revisar que las opciones quepan (si salen con letra pequeña, acortarlas) y previsualizar fotogramas antes de renderizar.

## Estado de la web (noviembre de 2026)

- Publicada en **https://acticdesdecasa.vercel.app** (Vercel Hobby, Root Directory `web`, despliegue automático con cada push a `main`). El usuario sabe que Hobby no permite uso comercial: antes de abrir ventas, pasar a Vercel Pro u otro hosting.
- Supabase: proyecto `acticdesdecasa` (región West EU), URL `https://msunpwqhlhmyhsynaoie.supabase.co`. `web/supabase/schema.sql` ya ejecutado (tablas `subscriptions`, `attempts`, `waitlist`).
- Variables en Vercel: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`. Ventas cerradas (`NEXT_PUBLIC_SALES_OPEN` sin poner = false): los botones llevan a la lista de espera.
- Lista de espera **funcionando** (`/api/estado` da claves publishable/secret y base de datos ok). En Vercel: las `NEXT_PUBLIC_*` son tipo Config y `SUPABASE_SERVICE_ROLE_KEY` tipo Secret; tras cambiar variables hay que hacer Redeploy. Los emails se ven en Supabase → Table Editor → `waitlist`.
- Páginas legales con titular **Xavier Estada** y contacto **synetispotify@gmail.com**; NIF y domicilio pendientes (obligatorios antes de vender).
- Pendiente:
  1. Supabase → Authentication → URL Configuration: Site URL `https://acticdesdecasa.vercel.app` y Redirect URL `https://acticdesdecasa.vercel.app/auth/callback`; probar el acceso por enlace mágico.
  2. Poner el enlace en la bio de Instagram.
  3. Dominio propio (opcional) y más preguntas para la web.
  4. Stripe (modo prueba): cuenta del usuario, `node scripts/stripe-setup.mjs` con su clave, webhook, IBAN de Wise para los pagos. Antes de vender: gestor (no es autónomo), IVA, condiciones legales, ~300 preguntas revisadas.
- Planes previstos: mensual 6,99 €, trimestral 9,99 € (destacado, «ahorras 52 %»), anual 19,99 € («ahorras 76 %») (`web/src/lib/plans.ts` y `PRECIOS` en `scripts/stripe-setup.mjs`).

## Entorno

Usar el entorno de Claude Code **"acticdesdecasa"** (permite `acticdesdecasa.vercel.app` y ElevenLabs). Commits con el nombre `albertreig998`.
