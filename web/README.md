# acticdesdecasa · web

Web de preparación del ACTIC: test gratis, lista de espera, suscripción con Stripe (mensual, trimestral y anual) y zona de alumnos con temario, práctica por temas, simulacros y repaso de fallos.

**Tecnología:** Next.js 16 · Supabase (acceso por enlace al email y base de datos) · Stripe Checkout + Portal de cliente.

## Qué hay dentro

| Ruta | Qué es |
|---|---|
| `/` | Portada con niveles y precios |
| `/test-gratis` | 10 preguntas al azar, sin registro |
| `/precios` | Los 3 planes (o "Avísame cuando abra" si las ventas están cerradas) |
| `/lista-espera` | Formulario de email antes del lanzamiento |
| `/entrar` | Acceso sin contraseña (enlace mágico al email) |
| `/app` | Zona de alumnos: progreso por nivel (exige suscripción activa) |
| `/app/practica/[nivel]` | Práctica con explicación tras cada respuesta, filtrable por tema |
| `/app/simulacro/[nivel]` | Simulacro con cronómetro (20 preguntas, 30 min: ajústalo en el archivo) |
| `/app/fallos` | Las preguntas que fallaste la última vez |
| `/app/temario` | Temario por competencias (archivos `content/temario/*.md`) |
| `/app/cuenta` | Estado del plan y botón al portal de Stripe |
| `/legal/*` | Plantillas de aviso legal, privacidad, cookies y condiciones |

**Contenido:**
- `content/preguntas.json`: las preguntas. Se genera desde el proyecto de vídeos con `python3 ../actic/export_web.py` (así cada pregunta nueva sirve para un reel y para la web).
- `content/temario/*.md`: el temario, en Markdown. Son borradores: revísalos.

## Puesta en marcha (en este orden)

### 1. Supabase (base de datos y acceso)

1. Crea un proyecto gratis en supabase.com (región: Europa).
2. **SQL Editor** → pega el contenido de `supabase/schema.sql` → **Run**.
3. **Authentication → URL Configuration**: en *Site URL* pon la URL de la web y en *Redirect URLs* añade `https://TU-DOMINIO/auth/callback` (y `http://localhost:3000/auth/callback` para probar en local).
4. **Project Settings → API**: copia la URL, la *anon key* y la *service_role key* en `.env.local`.
5. (Recomendado) **Authentication → Emails**: traduce el email del enlace mágico al castellano. Con mucho volumen, configura un SMTP propio (el de Supabase tiene un límite bajo de envíos por hora).

### 2. Stripe (pagos, en modo prueba)

1. Crea la cuenta en stripe.com. Puedes registrarte como **particular**.
2. Con el **modo prueba** activado, copia la clave secreta (`sk_test_...`).
3. Crea producto, precios y portal: `STRIPE_SECRET_KEY=sk_test_... node scripts/stripe-setup.mjs` y copia las 3 líneas `STRIPE_PRICE_...` en `.env.local`.
4. **Webhook**, para que la web se entere de los pagos:
   - En producción: *Desarrolladores → Webhooks → Añadir endpoint* con `https://TU-DOMINIO/api/stripe/webhook` y los eventos `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated` y `customer.subscription.deleted`. Copia el *signing secret* en `STRIPE_WEBHOOK_SECRET`.
   - En local: instala la Stripe CLI y ejecuta `stripe listen --forward-to localhost:3000/api/stripe/webhook`.
5. Prueba un pago con la tarjeta `4242 4242 4242 4242`, cualquier fecha futura y cualquier CVC.

### 3. Cobrar en Wise

En Stripe → *Configuración → Pagos a cuenta bancaria*, añade el **IBAN de tu cuenta Wise en euros** (el que empieza por BE o el que te dé Wise). Stripe te transferirá ahí lo cobrado, menos sus comisiones. Comprueba en tu cuenta que Stripe acepta ese IBAN antes de abrir las ventas.

### 4. En local

```bash
cp .env.example .env.local   # y rellénalo
npm install
npm run dev                  # http://localhost:3000
```

Sin claves, la portada, el test gratis y los precios funcionan. El registro y la zona de alumnos necesitan Supabase.

### 5. Publicar

La forma más sencilla es **Vercel**: importa el repositorio de GitHub y añade las variables de `.env.local` en *Settings → Environment Variables* (con `NEXT_PUBLIC_SITE_URL` = tu dominio). Ojo: el plan gratuito de Vercel es para uso no comercial; cuando cobres, pasa al plan Pro o usa otro hosting compatible con Next.js.

## Antes de abrir las ventas (`NEXT_PUBLIC_SALES_OPEN=true`)

- [ ] Hablar con un gestor: alta, IVA y facturas. Si cobras tú con Stripe, eres el vendedor.
- [ ] Rellenar las plantillas de `src/app/legal/[doc]/page.tsx` con tus datos y revisarlas.
- [ ] En Stripe → *Configuración → Detalles públicos*: nombre comercial, email de soporte y URL de condiciones (`/legal/condiciones`). Después, poner `STRIPE_TERMS_CONSENT=true`.
- [ ] Decidir sobre el IVA: activar Stripe Tax (`STRIPE_AUTOMATIC_TAX=true`) o usar una plataforma que haga de vendedor (por ejemplo, Paddle o Lemon Squeezy, que cambiaría `/api/checkout` y el webhook).
- [ ] Tener bastantes preguntas revisadas (objetivo: unas 100 por nivel) y el temario revisado.
- [ ] Hacer una compra completa en modo prueba: pagar, entrar en la zona, cancelar desde el portal y comprobar que el acceso termina al final del periodo.
- [ ] Cambiar a las claves reales (`sk_live`), repetir el paso 2.3 en modo real y crear el webhook real.
