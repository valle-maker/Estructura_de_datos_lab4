import math
import os
import time
import statistics

import matplotlib
matplotlib.use("Agg")   # solo guardamos imágenes, no abrimos ventanas
import matplotlib.pyplot as plt

from Quadtreetree import (Quadtree, generar_puntos,
                          fuerza_bruta_radio, fuerza_bruta_vecino)


def medir_tiempo(buscar, consultas, repeticiones=5):
    """
    Tiempo promedio de UNA búsqueda, en microsegundos.
    'buscar' es una función que recibe un punto de consulta q.
    Se hacen todas las consultas, se mide el tiempo total y se divide
    entre cuántas consultas fueron. Eso se repite varias veces y se
    devuelve la mediana (así un resultado raro no estropea el dato).
    """
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        for q in consultas:
            buscar(q)
        fin = time.perf_counter()
        por_busqueda = (fin - inicio) / len(consultas)
        tiempos.append(por_busqueda * 1_000_000)   # de segundos a microsegundos
    return statistics.median(tiempos)


RADIO = 500
TAMANOS = [10, 30, 100, 300, 1000, 3000, 10000, 30000]


def medir_construccion(puntos, repeticiones=3):
    """Cuánto tarda construir el árbol con estos puntos, en milisegundos (mediana)."""
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        Quadtree(puntos)
        fin = time.perf_counter()
        tiempos.append((fin - inicio) * 1000)
    return statistics.median(tiempos)


def experimento(tamanos=TAMANOS, cantidad_de_consultas=100):
    """
    Para cada tamaño: genera los puntos, construye el árbol y mide el tiempo de
    una búsqueda (radio y vecino) con fuerza bruta y con el árbol.
    Devuelve una lista con un resultado por tamaño.
    """
    consultas = generar_puntos(cantidad_de_consultas, semilla=99)
    resultados = []

    for n in tamanos:
        puntos = generar_puntos(n, semilla=12345)
        arbol = Quadtree(puntos)

        resultado = {
            "n": n,
            "radio_bruta": medir_tiempo(lambda q: fuerza_bruta_radio(puntos, q, RADIO), consultas),
            "radio_arbol": medir_tiempo(lambda q: arbol.buscar_radio(q, RADIO), consultas),
            "vecino_bruta": medir_tiempo(lambda q: fuerza_bruta_vecino(puntos, q), consultas),
            "vecino_arbol": medir_tiempo(lambda q: arbol.buscar_vecino(q), consultas),
            "construccion_ms": medir_construccion(puntos),
        }
        resultados.append(resultado)
        print("listo n =", n)

    return resultados


CARPETA_GRAFICAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficas")


def pendiente(resultados, clave, n_minimo=1000):
    """
    Pendiente de la línea en la gráfica con ejes logarítmicos, entre el primer
    tamaño >= n_minimo y el último. Dice cómo crece el tiempo al crecer n:
    cerca de 1 = lineal (se duplica n, se duplica el tiempo); cerca de 0 = casi plano.
    Se ignoran los tamaños chicos porque ahí el ruido de la medición pesa demasiado.
    """
    usados = []
    for r in resultados:
        if r["n"] >= n_minimo:
            usados.append(r)
    primero = usados[0]
    ultimo = usados[-1]
    return math.log(ultimo[clave] / primero[clave]) / math.log(ultimo["n"] / primero["n"])


def tamano_donde_gana_el_arbol(resultados, clave_bruta, clave_arbol):
    """
    Primer tamaño a partir del cual el árbol es más rápido que la fuerza bruta
    y se mantiene más rápido en todos los tamaños mayores. Si nunca, devuelve None.
    """
    for i in range(len(resultados)):
        gana_desde_aqui = True
        for r in resultados[i:]:
            if r[clave_arbol] >= r[clave_bruta]:
                gana_desde_aqui = False
        if gana_desde_aqui:
            return resultados[i]["n"]
    return None


def busquedas_para_compensar(r, clave_bruta, clave_arbol):
    """
    Cuántas búsquedas hacen falta para que el árbol recupere lo que costó construirlo.
    = tiempo de construir / lo que se ahorra en cada búsqueda.
    Si el árbol no ahorra nada en este tamaño, devuelve None.
    """
    ahorro_por_busqueda = r[clave_bruta] - r[clave_arbol]      # en microsegundos
    if ahorro_por_busqueda <= 0:
        return None
    construccion_us = r["construccion_ms"] * 1000               # ms -> microsegundos
    return construccion_us / ahorro_por_busqueda


def graficar_busqueda(resultados, clave_bruta, clave_arbol, titulo, nombre_archivo):
    """Gráfica: tamaño de los datos (x) contra tiempo de una búsqueda (y)."""
    tamanos = []
    bruta = []
    arbol = []
    for r in resultados:
        tamanos.append(r["n"])
        bruta.append(r[clave_bruta])
        arbol.append(r[clave_arbol])

    figura, eje = plt.subplots(figsize=(8, 5.5))
    eje.plot(tamanos, bruta, marker="o", color="red",
             label="Fuerza bruta (pendiente %.2f)" % pendiente(resultados, clave_bruta))
    eje.plot(tamanos, arbol, marker="o", color="blue",
             label="Quadtree (pendiente %.2f)" % pendiente(resultados, clave_arbol))

    cruce = tamano_donde_gana_el_arbol(resultados, clave_bruta, clave_arbol)
    if cruce is not None:
        eje.axvline(cruce, linestyle="--", color="gray", label="El árbol gana desde n = %d" % cruce)

    # Ejes logarítmicos: los tamaños van de 10 a 30,000 y así se ven todos
    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_xlabel("Tamaño de los datos (número de puntos)")
    eje.set_ylabel("Tiempo de una búsqueda (microsegundos)")
    eje.set_title(titulo)
    eje.grid(True, which="both", alpha=0.3)
    eje.legend()

    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
    ruta = os.path.join(CARPETA_GRAFICAS, nombre_archivo)
    figura.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(figura)
    print("Guardado:", ruta)


def graficar_compensacion(resultados, nombre_archivo):
    """Gráfica: cuántas búsquedas hacen falta para que valga la pena construir el árbol."""
    figura, eje = plt.subplots(figsize=(8, 5.5))

    for clave_bruta, clave_arbol, nombre, color in [
        ("radio_bruta", "radio_arbol", "Búsqueda por radio", "green"),
        ("vecino_bruta", "vecino_arbol", "Vecino más cercano", "purple"),
    ]:
        tamanos = []
        busquedas = []
        for r in resultados:
            cantidad = busquedas_para_compensar(r, clave_bruta, clave_arbol)
            if cantidad is not None:
                tamanos.append(r["n"])
                busquedas.append(cantidad)
        eje.plot(tamanos, busquedas, marker="o", color=color, label=nombre)

    eje.set_xscale("log")
    eje.set_ylim(bottom=0)
    eje.set_xlabel("Tamaño de los datos (número de puntos)")
    eje.set_ylabel("Búsquedas necesarias para compensar la construcción")
    eje.set_title("¿Cuántas búsquedas hacen falta para que valga la pena construir el árbol?")
    eje.grid(True, which="both", alpha=0.3)
    eje.legend()

    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
    ruta = os.path.join(CARPETA_GRAFICAS, nombre_archivo)
    figura.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(figura)
    print("Guardado:", ruta)


def imprimir_tabla(resultados):
    print()
    print("%7s | %-26s | %-26s | %s" % ("n", "radio: bruta / árbol (us)", "vecino: bruta / árbol (us)", "construir (ms)"))
    for r in resultados:
        print("%7d | %10.1f / %-13.1f | %10.1f / %-13.1f | %.1f" % (
            r["n"], r["radio_bruta"], r["radio_arbol"],
            r["vecino_bruta"], r["vecino_arbol"], r["construccion_ms"]))


if __name__ == "__main__":
    resultados = experimento()
    imprimir_tabla(resultados)

    print()
    print("Radio:  el árbol gana desde n =",
          tamano_donde_gana_el_arbol(resultados, "radio_bruta", "radio_arbol"))
    print("Vecino: el árbol gana desde n =",
          tamano_donde_gana_el_arbol(resultados, "vecino_bruta", "vecino_arbol"))
    print()
    for clave in ["radio_bruta", "radio_arbol", "vecino_bruta", "vecino_arbol"]:
        print("Pendiente de %-13s %.2f" % (clave + ":", pendiente(resultados, clave)))
    print()

    graficar_busqueda(resultados, "radio_bruta", "radio_arbol",
                      "Búsqueda por radio (500 m): fuerza bruta vs Quadtree",
                      "tiempo_radio.png")
    graficar_busqueda(resultados, "vecino_bruta", "vecino_arbol",
                      "Vecino más cercano: fuerza bruta vs Quadtree",
                      "tiempo_vecino.png")
    graficar_compensacion(resultados, "compensacion_construccion.png")