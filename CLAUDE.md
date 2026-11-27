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

## Reels de promoción con personajes

- `actic/personajes.py`: Casi (mascota casita con las barras de nivel) y Marta (estudiante), dibujados con PIL y animables (boca, parpadeo, expresiones, poses). `actic/promo.py`: guiones en `REELS` (líneas con quién habla, audio, texto del bocadillo y estado de los personajes/efectos); la boca sigue el volumen de cada voz. Uso: `python3 promo.py 1 5` (o `--preview` para fotogramas) → `salida/promo/promo_{n}.mp4`.
- Voz de Marta: **Gala** (`Wi5NZQRxyOb3Jx4r0hrI`, castellano joven); Casi: Pablo. Audios `salida/quiz_voz/promo{n}_{m|c}{k}.mp3`.
- Hechos (5): 1 «POV: el ACTIC es mañana», 2 «Academia vs. desde casa» (prop `compare`), 3 «POV: estudias el ACTIC en el bus» (línea muda con `rapid`: preguntas en el móvil), 4 «¿Qué nivel del ACTIC necesitas?» (prop `level`, barras de Casi con `bars`), 5 «El error que suspende a todos» (`question`). Todos acaban con la tarjeta «Haz el test gratis · enlace en la bio» (`end` / `end_at`).

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
- Variables en Vercel: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`. Ventas abiertas (ver Stripe modo REAL más abajo).
- Lista de espera **funcionando** (`/api/estado` da claves publishable/secret y base de datos ok). En Vercel: las `NEXT_PUBLIC_*` son tipo Config y `SUPABASE_SERVICE_ROLE_KEY` tipo Secret; tras cambiar variables hay que hacer Redeploy. Los emails se ven en Supabase → Table Editor → `waitlist`.
- Páginas legales: sin nombre de titular (el usuario no quiere que se vea su nombre; la cuenta de Wise está a nombre de Albert Reig), solo «acticdesdecasa» y contacto **synetispotify@gmail.com**. **Antes de cobrar** hay que poner nombre, NIF y domicilio del titular real (LSSI): ya se le ha explicado; alternativa: sociedad (SL) o plataforma que venda por él, consultar con gestor.
- Pendiente:
  1. Supabase → Authentication → URL Configuration: Site URL `https://acticdesdecasa.vercel.app` y Redirect URL `https://acticdesdecasa.vercel.app/auth/callback`; probar el acceso por enlace mágico.
  2. Poner el enlace en la bio de Instagram.
  3. Dominio propio (opcional).
- **Producto (contenido de la web):** 150 preguntas, 50 por nivel = 45 de los reels (`content/preguntas.json`, generado con `export_web.py`) + 105 propias de la web (`content/banco.json`, se edita a mano: misma estructura). Temario ampliado en `content/temario/*.md` (el conversor no admite tablas Markdown). Nombres "oficiales" de las competencias en `COMPETENCIAS` de `src/lib/content.ts`, sin verificar contra actic.gencat.cat (el dominio no era accesible desde el entorno). Simulacro: 20 preguntas / 30 min, orientativo.
  4. Stripe (modo prueba): cuenta del usuario, `node scripts/stripe-setup.mjs` con su clave, webhook, IBAN de Wise para los pagos. Antes de vender: gestor (no es autónomo), IVA, condiciones legales, ~300 preguntas revisadas.
- **Stripe (modo prueba) creado** por Claude con `web/scripts/stripe_setup.py`: producto `prod_VhNmpj4vVgg0fn`, precios mensual `price_1Ufz0lDprsOnpOHL2fHLEfCq`, trimestral `price_1Ufz0lDprsOnpOHLhiwBZYWO`, anual `price_1Ufz0mDprsOnpOHLyB5TmZgE`, portal `bpc_1Ufz0mDprsOnpOHLjXiKjVqu`. La clave sk_test está guardada como credencial de `api.stripe.com` en el entorno Default (el proxy la añade; usar `Bearer sk_test_proxy-injected`). La librería stripe de Node no pasa por el proxy: usar curl o urllib. Webhook creado (`we_1UfzEODprsOnpOHLC2cAxdNC`, 4 eventos) y variables STRIPE_* en Vercel (tipo Secret). **Compra de prueba OK** (26/11/2026): checkout → suscripción activa en la web, webhooks entregados.
- **Stripe modo REAL** (26/11/2026): cuenta activada (persona física, cobros a Wise IBAN belga; verificación de identidad pendiente, límite 10/12/2026). Producto copiado del sandbox (mismo `prod_VhNmpj4vVgg0fn`), precios mensual `price_1Ug06aDU1ywNpf7By327sNPj`, trimestral `price_1Ug06ZDU1ywNpf7BUVaIEuaN`, anual `price_1Ug06YDU1ywNpf7BHTXSReO6`, portal `bpc_1Ug0ALDU1ywNpf7BVVaPSZgT`. La credencial de `api.stripe.com` del entorno es ahora la clave **real** (restringida, sin operaciones sensibles): cuidado, todo lo que se haga con ella es real. `scripts/stripe_setup.py --live` para modo real. Webhook real `we_1Ug0BNDU1ywNpf7Brd39o8mx` (creado por API). **Ventas ABIERTAS en modo real desde el 26/11/2026** (`NEXT_PUBLIC_SALES_OPEN=true`; `/api/estado` muestra modo, webhook y precios). Pendiente del usuario: verificación de identidad en Stripe (antes del 10/12), email de soporte y URLs de condiciones/privacidad en Stripe, después `STRIPE_TERMS_CONSENT=true` en Vercel; Vercel Pro; gestor/autónomo; datos del titular en páginas legales.
- Planes previstos: mensual 6,99 €, trimestral 9,99 € (destacado, «ahorras 52 %»), anual 19,99 € («ahorras 76 %») (`web/src/lib/plans.ts` y `PRECIOS` en `scripts/stripe-setup.mjs`).

## Entorno

Usar el entorno de Claude Code **"acticdesdecasa"** (permite `acticdesdecasa.vercel.app` y ElevenLabs). Commits como `bertini98` con el email noreply de GitHub (no usar el email personal).

## Normativa aplicada en la web (26/11/2026)

- Páginas legales reescritas (`web/src/app/legal/[doc]/page.tsx`): aviso legal (LSSI), privacidad (RGPD/LOPDGDD, edad 14, encargados Supabase/Stripe/Vercel), cookies (solo técnicas), condiciones de contratación (precios desde `plans.ts`, renovación con aviso 15 días —Ley 10/2025, plazo de adaptación hasta ~28/12/2026—, baja en dos clics, desistimiento 14 días con excepción art. 103.m por consentimiento en el checkout, conformidad, atención gratuita con respuesta en 15 días hábiles, hojas oficiales de reclamación de la Generalitat, castellano/catalán, sin ADR).
- Función de desistimiento online (Directiva 2023/2673; en España RDL 44/2026, art. 106 bis TRLGDCU, en vigor 25/01/2027 según fuentes secundarias): `/desistimiento` + `/api/desistimiento` → tabla `withdrawals` (añadida a `schema.sql`; **el usuario debe ejecutar ese bloque en Supabase**). Enlace «Desistir del contrato aquí» en el pie y en Mi cuenta. El titular revisa la tabla, confirma por email y reembolsa desde Stripe.
- Hecho en Stripe (26/11/2026): emails de próxima renovación, tarjetas caducadas y pagos fallidos; recibos y reembolsos por email; email de soporte y URLs de condiciones/privacidad en Public details; `STRIPE_TERMS_CONSENT=true` en Vercel (casilla obligatoria comprobada con una sesión de prueba). Tabla `withdrawals` creada en Supabase. Aviso de renovación a 15 días: hecho. Pendiente: verificación de identidad en Stripe (antes del 10/12/2026). El usuario hará Vercel Pro, gestor/autónomo y datos del titular cuando entre el primer cliente.
- Fiscal: autónomo (tarifa plana ~80-89 €/mes primer año), IVA 21 % servicios digitales, Verifactu obligatorio para autónomos desde 1/07/2027 (posibles nuevos aplazamientos).
