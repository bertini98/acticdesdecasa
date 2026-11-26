import { notFound } from "next/navigation";

import { markdownToHtml } from "@/lib/markdown";
import { PLANS } from "@/lib/plans";

// Textos redactados siguiendo la normativa española (LSSI, TRLGDCU, RGPD/LOPDGDD, Ley 10/2025 de atención a la
// clientela y Codi de consum de Catalunya). Revisarlos con un gestor o abogado.
// La LSSI obliga a mostrar nombre, NIF y domicilio del titular de una web que vende: rellenar TITULAR, NIF y DOMICILIO.
// Mientras estén vacíos se muestra solo el nombre comercial y el email.
const TITULAR = "";
const NIF = "";
const DOMICILIO = "";
const EMAIL = "synetispotify@gmail.com";
const WEB = "acticdesdecasa.vercel.app";
const ACTUALIZADO = "26 de noviembre de 2026";

const IDENTIDAD =
  [TITULAR, NIF && `con NIF ${NIF}`, DOMICILIO && `y domicilio en ${DOMICILIO}`].filter(Boolean).join(", ") ||
  "acticdesdecasa";

const PERIODO: Record<string, string> = { "/mes": "al mes", "/3 meses": "cada 3 meses", "/año": "al año" };
const PRECIOS = PLANS.map((p) => `- **${p.nombre}:** ${p.precio} ${PERIODO[p.periodo] ?? p.periodo}`).join("\n");

const DOCS: Record<string, { titulo: string; md: string }> = {
  "aviso-legal": {
    titulo: "Aviso legal",
    md: `
En cumplimiento de la Ley 34/2002, de servicios de la sociedad de la información y de comercio electrónico (LSSI), te informamos de que este sitio web (${WEB}), con el nombre comercial **acticdesdecasa**, es titularidad de ${IDENTIDAD}. Contacto: ${EMAIL}.

# Objeto

La web ofrece material de preparación (tests, simulacros y temario) para la acreditación de competencias digitales ACTIC.

# Web no oficial

acticdesdecasa es una iniciativa **independiente**. No está vinculada, patrocinada ni autorizada por la Generalitat de Catalunya. «ACTIC» es el nombre de la acreditación oficial y se menciona solo para describir el contenido. Las preguntas son de elaboración propia: no son las del examen oficial.

# Propiedad intelectual

Los textos, preguntas, explicaciones, imágenes y vídeos de la web son propiedad del titular. No se permite copiarlos, distribuirlos ni revenderlos sin autorización. Tu suscripción es personal: no compartas tu cuenta.

# Responsabilidad

El material se revisa con cuidado, pero puede contener errores y no garantiza el aprobado. Si encuentras un fallo, escríbenos y lo corregiremos.

# Ley aplicable

Se aplica la ley española. Si eres consumidor, para cualquier conflicto serán competentes los juzgados de tu domicilio.

*Última actualización: ${ACTUALIZADO}.*
`,
  },
  privacidad: {
    titulo: "Política de privacidad",
    md: `
**Responsable del tratamiento:** ${IDENTIDAD}. Contacto: ${EMAIL}.

# Qué datos tratamos, para qué y con qué base legal

- **Email y datos de acceso**, para crear tu cuenta y dejarte entrar. Base: ejecución del contrato.
- **Tus respuestas a los tests**, para mostrarte tu progreso y tus fallos. Base: ejecución del contrato.
- **Datos de la suscripción y del pago** (plan, fechas, importes, país). Los datos de la tarjeta los trata directamente Stripe: nosotros no los vemos ni los guardamos. Base: ejecución del contrato y obligaciones legales (fiscales y contables).
- **Lista de espera**: tu email, para avisarte del lanzamiento. Base: tu consentimiento, que puedes retirar cuando quieras.
- **Consultas, reclamaciones y solicitudes de desistimiento** que nos envíes, para atenderlas. Base: obligación legal y ejecución del contrato.

No tomamos decisiones automatizadas sobre ti ni hacemos perfiles con fines publicitarios. No vendemos tus datos.

# Cuánto tiempo los guardamos

- Los datos de la cuenta y del progreso, mientras tengas cuenta. Si la borras, se eliminan.
- Los datos de facturación, el tiempo que obliga la ley: 6 años (Código de Comercio) y los plazos de prescripción fiscal.
- La lista de espera, hasta el lanzamiento o hasta que pidas la baja.

# Con quién se comparten

Solo con los proveedores necesarios para que la web funcione, que actúan como encargados del tratamiento con contrato:

- **Supabase** (base de datos y acceso; servidores en la Unión Europea).
- **Stripe** (pagos; Irlanda y Estados Unidos).
- **Vercel** (alojamiento de la web; Estados Unidos).

Las transferencias fuera del Espacio Económico Europeo se hacen con las garantías del RGPD (Marco de Privacidad de Datos UE-EE. UU. o cláusulas contractuales tipo). También podemos comunicar datos a la Administración (por ejemplo, Hacienda) cuando la ley lo exija.

# Edad mínima

Para crear una cuenta debes tener al menos 14 años (art. 7 de la LOPDGDD). Para contratar un plan de pago debes ser mayor de edad o contar con autorización de tu madre, padre o tutor.

# Tus derechos

Puedes pedir el acceso, la rectificación, la supresión, la oposición, la limitación del tratamiento y la portabilidad de tus datos, y retirar tu consentimiento, escribiendo a ${EMAIL}. Te responderemos en un plazo máximo de un mes. Si no estás de acuerdo con nuestra respuesta, puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).

*Última actualización: ${ACTUALIZADO}.*
`,
  },
  cookies: {
    titulo: "Política de cookies",
    md: `
Esta web solo usa **cookies técnicas**, imprescindibles para que funcione: mantienen tu sesión iniciada (cookies de Supabase, que caducan al cerrar sesión o pasado un tiempo). Según la LSSI, estas cookies no necesitan tu consentimiento.

No usamos cookies de analítica ni de publicidad, ni compartimos tu navegación con terceros.

Al pagar, la página de Stripe puede usar sus propias cookies para procesar el pago de forma segura y prevenir el fraude. Puedes consultarlas en la política de cookies de Stripe.

Puedes borrar las cookies desde la configuración de tu navegador; si lo haces, tendrás que volver a iniciar sesión.

Si en el futuro añadimos analítica o publicidad, te pediremos permiso antes con un aviso.

*Última actualización: ${ACTUALIZADO}.*
`,
  },
  condiciones: {
    titulo: "Condiciones de contratación",
    md: `
Estas condiciones regulan la compra de suscripciones en acticdesdecasa (${WEB}), cuyo titular es ${IDENTIDAD}. Contacto: ${EMAIL}. Te recomendamos guardarlas o imprimirlas.

# 1. Qué contratas

Acceso personal a la zona de alumnos de acticdesdecasa (tests de los tres niveles, simulacros, repaso de fallos y temario) mientras tu suscripción esté activa. Es un servicio 100 % digital: no hay envíos. Es material de preparación no oficial y no incluye la inscripción ni las tasas del examen ACTIC.

# 2. Precios

Los precios incluyen el IVA y no hay gastos adicionales:

${PRECIOS}

Si algún día cambiamos el precio, te avisaremos por email con al menos 30 días de antelación y el nuevo precio solo se aplicará a partir de la siguiente renovación. Si no estás de acuerdo, podrás cancelar antes sin ningún coste.

# 3. Cómo se contrata

1. Eliges un plan en la página de precios.
2. Entras con tu email (te enviamos un enlace de acceso).
3. Pagas en la página segura de Stripe con tarjeta u otro método disponible. Antes de pagar puedes revisar el plan y el importe, y corregir cualquier dato.
4. Al pagar aceptas estas condiciones y, como se explica en el punto 6, pides empezar a usar el contenido de inmediato.
5. Recibirás por email la confirmación del pago y el recibo. El acceso se activa al momento.

El contrato se celebra en castellano. Guardamos un registro electrónico de tu compra, al que puedes acceder desde **Mi cuenta**.

# 4. Renovación automática y avisos

La suscripción **se renueva automáticamente** al final de cada periodo (mes, trimestre o año) por el mismo importe y con el mismo método de pago, hasta que la canceles. Te avisaremos por email **al menos 15 días antes** de cada renovación, recordándote la fecha, el importe y cómo cancelar.

# 5. Cancelación (baja)

Puedes cancelar **cuando quieras, sin penalización y en dos clics**: entra en **Mi cuenta → Gestionar suscripción → Cancelar**. También puedes pedirlo por email a ${EMAIL}. Al cancelar, no se te volverá a cobrar y mantendrás el acceso hasta el final del periodo ya pagado. No se devuelve la parte del periodo en curso, salvo en los casos de los puntos 6 y 7.

# 6. Derecho de desistimiento

Como consumidor, en los contratos a distancia tienes, por regla general, **14 días naturales** desde la contratación para desistir sin dar explicaciones.

**Excepción del contenido digital:** el acceso a la zona de alumnos es contenido digital que se te entrega de inmediato. Por eso, al pagar te pedimos que marques que **quieres empezar a usarlo ya** y que **sabes que así pierdes el derecho de desistimiento** (artículo 103.m del Texto refundido de la Ley General para la Defensa de los Consumidores y Usuarios). Te lo confirmamos por email junto con el recibo. Si diste ese consentimiento, no se aplica el desistimiento, pero puedes cancelar la renovación cuando quieras (punto 5).

**Si no diste ese consentimiento**, o no te informamos correctamente, puedes desistir en los 14 días siguientes a la contratación:

- Desde la página **Desistir del contrato** (enlace al pie de todas las páginas: ${WEB}/desistimiento), o
- Enviando a ${EMAIL} una declaración clara de que quieres desistir. Puedes usar este modelo: «Por la presente le comunico que desisto de mi contrato de suscripción a acticdesdecasa. Plan contratado: … Fecha de contratación: … Nombre y email de la cuenta: … Fecha: …».

Te confirmaremos la recepción por email y te devolveremos el importe en un plazo máximo de 14 días, por el mismo medio de pago, sin ningún coste para ti.

# 7. Si algo no funciona (conformidad)

Tienes derecho a que el servicio funcione y se corresponda con lo descrito durante todo el tiempo que estés suscrito. Si no es así, escríbenos: lo arreglaremos sin coste en un plazo razonable. Si no podemos arreglarlo, podrás pedir una rebaja proporcional del precio o resolver el contrato con la devolución de la parte correspondiente.

# 8. Uso de la cuenta

La cuenta es personal e intransferible. Está prohibido compartirla, copiar o difundir las preguntas, o acceder de forma automatizada. Si se incumple de forma grave, podremos suspender la cuenta tras avisarte.

# 9. Atención al cliente y reclamaciones

La atención al cliente es **gratuita**. Escríbenos a ${EMAIL} para cualquier consulta, incidencia o reclamación: te daremos un número de referencia y responderemos en un plazo máximo de **15 días hábiles**. Te atendemos en castellano o en catalán.

Tienes a tu disposición las **hojas oficiales de queja, reclamación y denuncia** de la Generalitat de Catalunya: pídenoslas por email y te las enviaremos. También puedes dirigirte a la oficina municipal de información al consumidor (OMIC) de tu localidad o a la Agència Catalana del Consum (consum.cat).

De momento no estamos adheridos a ningún sistema de resolución alternativa de conflictos ni al arbitraje de consumo, pero puedes acudir a ellos y valoraremos la solicitud.

# 10. Ley aplicable y tribunales

Estas condiciones se rigen por la ley española. Si eres consumidor, serán competentes los juzgados de tu domicilio.

*Última actualización: ${ACTUALIZADO}.*
`,
  },
};

export function generateStaticParams() {
  return Object.keys(DOCS).map((doc) => ({ doc }));
}

export async function generateMetadata({ params }: { params: Promise<{ doc: string }> }) {
  const { doc } = await params;
  return { title: DOCS[doc]?.titulo ?? "Legal" };
}

export default async function Legal({ params }: { params: Promise<{ doc: string }> }) {
  const { doc } = await params;
  const d = DOCS[doc];
  if (!d) notFound();
  return (
    <section className="section">
      <div className="wrap">
        <h1 style={{ fontSize: "2rem" }}>{d.titulo}</h1>
        <article className="prose" dangerouslySetInnerHTML={{ __html: markdownToHtml(d.md) }} />
      </div>
    </section>
  );
}
