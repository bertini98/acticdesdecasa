> Borrador: revísalo con el temario oficial del ACTIC antes de publicar.

# Conceptos básicos

- Una **tabla** guarda datos en **registros** (filas) y **campos** (columnas).
- La **clave primaria** es el campo que identifica cada registro **sin repetirse**, como el DNI de una persona.

# Relaciones

En una relación **uno a varios**, un registro de una tabla se relaciona con varios de otra. Por ejemplo, un cliente puede tener muchos pedidos, pero cada pedido es de un solo cliente.

# Objetos de una base de datos

- **Consulta:** pide a la base de datos solo los registros que cumplen unos criterios (por ejemplo, los clientes de Girona).
- **Formulario:** pantalla para introducir o ver datos cómodamente.
- **Informe:** presentación de los datos lista para imprimir.

# Más conceptos

- **Clave externa (foránea)**: campo que enlaza con la clave primaria de otra tabla.
- **Integridad referencial**: impide que un registro apunte a datos que no existen.
- **Relación varios a varios**: se resuelve con una tabla intermedia (por ejemplo, alumnos–matrículas–asignaturas).
- **Normalización**: no repetir datos en varias tablas para evitar incoherencias.
- **Tipos de datos**: texto, número, fecha, moneda, sí/no… Usa el adecuado (una fecha de nacimiento, tipo Fecha).

# Consultas

- **Criterios**: con **O** basta con que se cumpla uno (Girona O Lleida); con **Y** deben cumplirse todos.
- **Ordenar** los resultados (A–Z, de mayor a menor…).
- **Campo calculado**: se obtiene con una expresión, como `Precio * Cantidad`.
- **Consulta de actualización**: modifica muchos registros a la vez.
