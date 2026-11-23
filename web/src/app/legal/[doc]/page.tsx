import { notFound } from "next/navigation";

import { markdownToHtml } from "@/lib/markdown";

// Revisar con un gestor o abogado antes de vender. NIF y domicilio son obligatorios al empezar a cobrar.
const TITULAR = "Xavier Estada";
const NIF = ""; // pendiente
const DOMICILIO = ""; // pendiente
const EMAIL = "synetispotify@gmail.com";

// "Xavier Estada, con NIF … y domicilio en …": solo los datos que ya tenemos
const IDENTIDAD = [TITULAR, NIF && `con NIF ${NIF}`, DOMICILIO && `y domicilio en ${DOMICILIO}`]
  .filter(Boolean)
  .join(", ");

const DOCS: Record<string, { titulo: string; md: string }> = {
  "aviso-legal": {
    titulo: "Aviso legal",
    md: `
Este sitio web, acticdesdecasa, es titularidad de ${IDENTIDAD}. Contacto: ${EMAIL}.

# Objeto

La web ofrece material de preparación (tests, simulacros y temario) para la acreditación ACTIC. Es una iniciativa independiente: **no está vinculada a la Generalitat de Catalunya** ni el material es oficial.

# Propiedad intelectual

Los textos, preguntas, explicaciones e imágenes de la web son propiedad del titular. No se permite su reproducción sin autorización.

# Responsabilidad

El material se revisa con cuidado, pero no se garantiza que coincida con las preguntas del examen oficial ni que su uso asegure el aprobado.
`,
  },
  privacidad: {
    titulo: "Política de privacidad",
    md: `
**Responsable:** ${IDENTIDAD}. Contacto: ${EMAIL}.

# Qué datos tratamos y para qué

- **Email**, para crear tu cuenta y darte acceso, y para avisarte del lanzamiento si te apuntas a la lista de espera.
- **Tus respuestas** a los tests, para mostrarte tu progreso y tus fallos.
- **Datos de pago**: los gestiona Stripe. Nosotros no vemos ni guardamos los datos de tu tarjeta.

# Base legal

La ejecución del contrato (tu suscripción) y, para la lista de espera, tu consentimiento.

# Con quién se comparten

Con los proveedores necesarios para que la web funcione: Supabase (base de datos y acceso), Stripe (pagos) y el proveedor de alojamiento. Algunos pueden tratar datos fuera del Espacio Económico Europeo con las garantías que exige el RGPD.

# Cuánto tiempo

Mientras tengas cuenta. Si la borras, eliminamos tus datos salvo los que la ley obligue a conservar (por ejemplo, facturas).

# Tus derechos

Puedes acceder, rectificar, suprimir, oponerte, limitar el tratamiento y pedir la portabilidad escribiendo a ${EMAIL}. También puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).
`,
  },
  cookies: {
    titulo: "Política de cookies",
    md: `
Esta web solo usa **cookies técnicas**, imprescindibles para que funcione: mantienen tu sesión iniciada. No usamos cookies de analítica ni de publicidad.

Al pagar, la página de Stripe puede usar sus propias cookies para procesar el pago de forma segura y prevenir el fraude.

Si en el futuro añadimos analítica o publicidad, te pediremos permiso antes.
`,
  },
  condiciones: {
    titulo: "Condiciones de compra",
    md: `
# Qué compras

Acceso a la zona de alumnos de acticdesdecasa (tests, simulacros y temario) durante el periodo del plan elegido: mensual, trimestral o anual.

# Precio y renovación

Los precios incluyen IVA. La suscripción **se renueva automáticamente** al final de cada periodo por el mismo importe, hasta que la canceles.

# Cancelación

Puedes cancelar en cualquier momento desde **Mi cuenta → Gestionar suscripción**. Mantendrás el acceso hasta el final del periodo ya pagado y no se te volverá a cobrar.

# Derecho de desistimiento

Al tratarse de contenido digital al que accedes de forma inmediata, al contratar das tu consentimiento expreso para empezar a usarlo y aceptas que, por ello, **pierdes el derecho de desistimiento** de 14 días.

# Contacto

Para cualquier problema con tu suscripción escribe a ${EMAIL}.
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
