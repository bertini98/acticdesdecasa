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

# Lo básico

- Las celdas se nombran por **columna + fila**: C5 = columna C, fila 5.
- **Orden de las operaciones**: primero multiplicaciones y divisiones, después sumas y restas (`=2+3*2` da 8). Usa paréntesis para cambiarlo.
- **Controlador de relleno**: el cuadradito de la esquina; copia fórmulas o continúa series.
- Al copiar una fórmula, las **referencias relativas** se ajustan (`=A1*2` pasa a `=A2*2`).

# Más funciones

- `=MIN()` y `=MAX()`: el menor y el mayor valor.
- `=HOY()`: fecha actual (`=AHORA()` incluye la hora).
- `=CONTAR()` cuenta números; `=CONTARA()` cuenta celdas no vacías; `=CONTAR.BLANCO()` las vacías.
- `=SUMAR.SI(rango;">5")` suma solo lo que cumple la condición.
- `=REDONDEAR(3,456;1)` da 3,5.
- `=Y(...)` exige que se cumplan todas las condiciones; `=O(...)`, al menos una.
- `=SI.ERROR(fórmula;valor)` muestra un valor alternativo si hay error.
- `=BUSCARV(valor;tabla;columna;FALSO)` busca en la primera columna y devuelve un dato de esa fila.

# Referencias absolutas y mixtas

- `$A$1` fija columna y fila; `$A1` fija solo la columna; `A$1` fija solo la fila.

# Más errores

- `#¿NOMBRE?`: función mal escrita o texto sin comillas.

# Herramientas avanzadas

- **Formato condicional**: cambia el formato según el valor (por ejemplo, notas < 5 en rojo).
- **Validación de datos**: limita lo que se puede escribir (rango de números, lista desplegable).
- **Tabla dinámica**: resume y agrupa muchos datos de forma interactiva.
- **Gráficos**: de líneas para la evolución en el tiempo; circular para partes de un total.
- Si escribes `1/2`, la hoja lo convierte en una **fecha**; para la fracción, escribe `0 1/2`.
