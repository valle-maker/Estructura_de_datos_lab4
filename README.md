# Laboratorio 4: Quadtree para búsqueda espacial

**Estudiante:** Diego Alejandro Valle Valencia
**Curso:** Estructuras de Datos y Laboratorio, Universidad de Antioquia

## Qué es este proyecto

Implementación desde cero de un **Quadtree** (árbol que parte el espacio en regiones) para 10,000 puntos de entrega estáticos, sin usar librerías de árboles ni de búsqueda espacial. El árbol responde dos consultas:

- **Búsqueda por radio:** todos los puntos a 500 m o menos de un punto de consulta.
- **Vecino más cercano:** el punto de entrega más cercano a un punto de consulta.

Cada búsqueda se compara contra **fuerza bruta** (revisar todos los puntos), que sirve de referencia de corrección y de línea base de tiempo. El árbol funciona para **K dimensiones**: en 2D cada región se parte en 4 hijos, en 3D en 8, y en general en 2^K.

Pregunta del laboratorio: *¿desde qué tamaño de datos el Quadtree empieza a ser más rápido que la fuerza bruta?* La respuesta está en la sección **Resultados**.

## Contenido del repositorio

| Archivo / carpeta | Qué contiene |
|---|---|
| `Quadtreetree.py` | Generador de puntos, nodo, Quadtree (construcción, búsqueda por radio, vecino más cercano) y las dos búsquedas por fuerza bruta |
| `test.py` | 6 pruebas unitarias contra fuerza bruta y las 2 verificaciones visuales |
| `analisis.py` | Mide tiempos para distintos tamaños de datos, calcula pendientes y dibuja las gráficas de rendimiento |
| `graficas/` | Las 5 gráficas (ya están generadas) |

## Decisiones de diseño

- **Datos:** sintéticos, puntos al azar con distribución uniforme en un cuadrado de 10,000 × 10,000, con decimales. Semilla fija (12345) para que sean repetibles.
- **Unidades:** 1 unidad = 1 metro, sin conversión. Un radio de 500 son 500 metros.
- **Región de la raíz:** el mínimo y el máximo de cada eje de los datos.
- **División:** una región se parte por su centro en 2^K hijos iguales. El punto que cae justo en el centro va a la mitad de arriba (`>=`).
- **Puntos solo en las hojas:** los nodos internos no guardan puntos.
- **Capacidad de hoja = 4:** una hoja se parte cuando tiene más de 4 puntos.
- **Nivel máximo = 20:** evita que el árbol se divida sin parar cuando hay muchos puntos repetidos.
- **Poda:** una región se descarta si la distancia del punto de consulta a la región es mayor que el radio (búsqueda por radio) o mayor o igual que el mejor vecino encontrado (vecino más cercano). En el vecino más cercano, los hijos se visitan del más cercano al más lejano.
- **Limitación:** los puntos insertados deben caer dentro de la región de la raíz, porque esta se calcula con los datos iniciales. Con muchas dimensiones (K mayor a 10 o 15) el árbol deja de ser práctico, porque cada nodo tiene 2^K hijos.

## Pruebas

`test.py` ejecuta 6 pruebas y compara siempre contra fuerza bruta:

1. Búsqueda por radio de 500 m en el centro del mapa.
2. Vecino más cercano en el centro del mapa.
3. El árbol conserva los 10,000 puntos (no pierde ninguno al partir).
4. 200 consultas al azar, algunas fuera del mapa, con radio y vecino.
5. Tres dimensiones (3,000 puntos): la raíz tiene 8 hijos y las búsquedas coinciden.
6. Árbol vacío: no falla y devuelve resultados vacíos.

Además dibuja dos verificaciones visuales:

- `graficas/verificacion_radio.png`: el círculo de 500 m con los puntos que encuentra el árbol (77 en el ejemplo, igual que fuerza bruta).
- `graficas/verificacion_vecinos.png`: 6 puntos de consulta unidos a su vecino más cercano; el círculo punteado de cada uno no contiene otros puntos.

No hay prueba automática para puntos repetidos ni para radio 0; el primer caso se cubre con el nivel máximo del árbol.

## Resultados

Se midió el tiempo de **una búsqueda** (promedio de 100 consultas al azar, mediana de 5 repeticiones) con tamaños de 10 a 30,000 puntos, y el costo de construir el árbol (mediana de 3 repeticiones). Los números son de una corrida y **cambian un poco** entre corridas y entre computadores; lo estable es la forma.

**¿Desde qué tamaño es más rápido el Quadtree?**

- **Búsqueda por radio:** el árbol ya gana desde el tamaño más pequeño probado (10 puntos), así que el cruce, si existe, queda por debajo de 10 puntos.
- **Vecino más cercano:** el árbol gana desde unos **100 puntos**. Con 10 y 30 puntos la fuerza bruta es igual o más rápida, porque revisar pocos puntos es más barato que recorrer el árbol.
- **Con 30,000 puntos:** la fuerza bruta tarda alrededor de 10,000 microsegundos por búsqueda; el árbol, alrededor de 400 en radio y 40 en vecino.

**Cómo crece el tiempo** (pendiente de la línea en ejes logarítmicos, entre 1,000 y 30,000 puntos; 1 = lineal, 0 = casi plano):

- Fuerza bruta: pendiente cercana a 1 en las dos búsquedas, o sea crecimiento lineal, O(n).
- Vecino más cercano con árbol: pendiente cercana a 0.2, casi plano, comportamiento tipo O(log n).
- Radio con árbol: pendiente cercana a 0.6. Crece más que el vecino porque, con radio fijo, al haber más puntos caen más dentro del círculo y hay que devolverlos todos.

**Costo de construir el árbol:** se paga una sola vez. Con 10,000 puntos tarda unos 50 a 90 ms. Se recupera, frente a fuerza bruta, con entre 8 y 30 búsquedas aproximadamente. Si solo se hiciera una consulta, la fuerza bruta saldría más barata en total.

Estos resultados valen para puntos repartidos de forma pareja. Si los puntos estuvieran muy amontonados, el árbol quedaría más profundo y la ventaja bajaría.

## Gráficas

| Gráfica | Qué muestra |
|---|---|
| `verificacion_radio.png` | Círculo de 500 m y los puntos que encuentra el árbol |
| `verificacion_vecinos.png` | Consultas unidas a su vecino más cercano |
| `tiempo_radio.png` | Tiempo de una búsqueda por radio vs tamaño de los datos (fuerza bruta vs Quadtree) |
| `tiempo_vecino.png` | Tiempo de una búsqueda de vecino vs tamaño de los datos |
| `compensacion_construccion.png` | Cuántas búsquedas hacen falta para compensar el costo de construir el árbol |

Las gráficas de tiempo usan ejes logarítmicos (los tamaños van de 10 a 30,000) e indican la pendiente de cada línea y el tamaño desde el cual el árbol gana.

## Cómo ejecutar

Requisitos: Python 3 y `matplotlib`.

```
pip install matplotlib
python Quadtreetree.py   # prueba rápida del árbol con datos pequeños y con 10,000 puntos
python test.py           # corre las 6 pruebas y genera las 2 verificaciones visuales
python analisis.py       # mide tiempos (tarda unos 20 segundos) y genera las gráficas
```

Los tres archivos deben estar en la misma carpeta. Las gráficas se guardan en `graficas/`, junto a los archivos.

## Código de honor y uso de herramientas de IA

Declaro que este trabajo es mío y que puedo explicar su contenido: cómo se construye el árbol, cómo funcionan la poda, la búsqueda por radio y el vecino más cercano, qué prueban los tests y qué significan las gráficas y las pendientes.

Para desarrollarlo usé una herramienta de inteligencia artificial (**Claude, de Anthropic**). La usé para:

- **Entender el tema:** explicar el Quadtree, la generalización a K dimensiones y la búsqueda por radio y vecino más cercano antes de escribir código.
- **Generar y explicar código:** el árbol, las pruebas, los dibujos y el experimento de rendimiento, revisados por partes y función por función.
- **Diseñar el experimento y analizar resultados:** tamaños de datos, forma de medir, pendientes y la discusión de los resultados.

Los tiempos, tablas y gráficas salen de mediciones reales hechas con el código del repositorio, y revisé que las conclusiones corresponden a lo medido.
