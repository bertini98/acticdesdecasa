# Igual que stripe-setup.mjs, pero con urllib: es el que se usa desde Claude Code, donde el proxy del
# entorno añade la clave de Stripe (guardada como credencial de api.stripe.com). Uso: python3 scripts/stripe_setup.py
# Para modo real: quitar la comprobación de livemode y guardar la clave sk_live como credencial.
import json, urllib.parse, urllib.request

API = "https://api.stripe.com/v1/"
HDR = {"Authorization": "Bearer sk_test_proxy-injected", "Content-Type": "application/x-www-form-urlencoded"}

def call(path, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(API + path, data=body, headers=HDR, method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Error en {path}: {e.read().decode()}")

assert call("balance")["livemode"] is False, "¡No es modo prueba!"

product = call("products", {
    "name": "acticdesdecasa · Acceso completo",
    "description": "Tests, simulacros y temario de los tres niveles del ACTIC.",
})
precios = [("MENSUAL", "Mensual", 699, "month", 1), ("TRIMESTRAL", "Trimestral", 999, "month", 3),
           ("ANUAL", "Anual", 1999, "year", 1)]
ids = {}
for plan, nombre, importe, interval, count in precios:
    p = call("prices", {
        "product": product["id"], "currency": "eur", "unit_amount": importe, "tax_behavior": "inclusive",
        "recurring[interval]": interval, "recurring[interval_count]": count,
        "nickname": nombre, "lookup_key": f"actic_{plan.lower()}",
    })
    ids[plan] = p["id"]

portal = {
    "business_profile[headline]": "acticdesdecasa · Gestiona tu suscripción",
    "default_return_url": "https://acticdesdecasa.vercel.app/app/cuenta",
    "features[customer_update][enabled]": "true",
    "features[customer_update][allowed_updates][0]": "email",
    "features[customer_update][allowed_updates][1]": "address",
    "features[invoice_history][enabled]": "true",
    "features[payment_method_update][enabled]": "true",
    "features[subscription_cancel][enabled]": "true",
    "features[subscription_cancel][mode]": "at_period_end",
    "features[subscription_update][enabled]": "true",
    "features[subscription_update][default_allowed_updates][0]": "price",
    "features[subscription_update][proration_behavior]": "create_prorations",
    "features[subscription_update][products][0][product]": product["id"],
}
for i, pid in enumerate(ids.values()):
    portal[f"features[subscription_update][products][0][prices][{i}]"] = pid
cfg = call("billing_portal/configurations", portal)

print("Producto:", product["id"])
print("Portal:", cfg["id"], "(por defecto:", cfg.get("is_default"), ")")
for plan, pid in ids.items():
    print(f"STRIPE_PRICE_{plan}={pid}")
