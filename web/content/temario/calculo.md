> Borrador: revísalo con el temario oficial del ACTIC antes de publicar.

# Fórmulas y rangos

- Toda fórmula empieza por `=`.
- Los **dos puntos** marcan un rango: `=SUMA(A1:A5)` suma de A1 a A5. Con punto y coma, `=SUMA(A1;A5)`, solo sumarías dos celdas.

# Funciones que más caen

- `=SUMA(rango)` suma. `=PROMEDIO(4;6;8)` da 6: suma 18 y lo divide entre 3.
- `=CONTAR.SI(rango;"Sí")` cuenta las celdas que cumplen una condición.
- `=SI(condición; valor si se cumple; valor si no)`. Por ejemplo: `=SI(B2>=5;"Aprobado";"Suspendido")`.

# Referencias absolutas

El símbolo `$` **fija** la referencia al copiar la fórmula: `=B2*$A$1` siempre apunta a A1, aunque copies la fórmula hacia abajo.

# Errores típicos

- `#¡DIV/0!`: estás dividiendo entre cero o entre una celda vacía.
- `####`: la columna es demasiado estrecha para mostrar el número.

# Trabajar con datos

- **Filtrar** oculta las filas que no cumplen un criterio. **Ordenar** solo cambia el orden, no oculta nada.
- **Inmovilizar paneles** deja fijas filas o columnas (por ejemplo, los títulos) mientras te desplazas.
- Para mostrar qué parte del total representa cada dato, usa un **gráfico circular**.
