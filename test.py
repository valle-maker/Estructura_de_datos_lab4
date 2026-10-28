import os
import random
import unittest

import matplotlib
matplotlib.use("Agg")   # solo guardamos imágenes, no abrimos ventanas
import matplotlib.pyplot as plt
from Quadtreetree import (Quadtree, generar_puntos,
                          fuerza_bruta_radio, fuerza_bruta_vecino)


class PruebasContraFuerzaBruta(unittest.TestCase):

    def setUp(self):
        # Esto se ejecuta antes de cada prueba: datos y árbol listos
        self.puntos = generar_puntos(10000, semilla=12345)
        self.arbol = Quadtree(self.puntos)

    def test_radio_500_en_el_centro(self):
        q = (5000, 5000)
        del_arbol = self.arbol.buscar_radio(q, 500)
        de_fuerza_bruta = fuerza_bruta_radio(self.puntos, q, 500)
        # sorted: el orden no importa, solo que sean los mismos puntos
        self.assertEqual(sorted(del_arbol), sorted(de_fuerza_bruta))

    def test_vecino_mas_cercano_en_el_centro(self):
        q = (5000, 5000)
        punto_arbol, distancia_arbol = self.arbol.buscar_vecino(q)
        punto_bruta, distancia_bruta = fuerza_bruta_vecino(self.puntos, q)
        self.assertEqual(punto_arbol, punto_bruta)
        self.assertEqual(distancia_arbol, distancia_bruta)

    def test_el_arbol_no_pierde_puntos(self):
        self.assertEqual(self.arbol.contar_puntos(), 10000)

    def test_200_consultas_al_azar(self):
        azar = random.Random(7)   # su propia semilla, para que sea repetible
        for _ in range(200):
            # puntos de consulta: también caen un poco fuera del mapa
            q = (azar.uniform(-500, 10500), azar.uniform(-500, 10500))

            del_arbol = self.arbol.buscar_radio(q, 500)
            de_fuerza_bruta = fuerza_bruta_radio(self.puntos, q, 500)
            self.assertEqual(sorted(del_arbol), sorted(de_fuerza_bruta))

            punto_arbol, _ = self.arbol.buscar_vecino(q)
            punto_bruta, _ = fuerza_bruta_vecino(self.puntos, q)
            self.assertEqual(punto_arbol, punto_bruta)

    def test_tres_dimensiones(self):
        puntos_3d = generar_puntos(3000, dimensiones=3, semilla=12345)
        arbol_3d = Quadtree(puntos_3d, dimensiones=3)
        q = (5000, 5000, 5000)

        self.assertEqual(arbol_3d.contar_puntos(), 3000)
        self.assertEqual(len(arbol_3d.raiz.hijos), 8)   # 2^3 hijos

        del_arbol = arbol_3d.buscar_radio(q, 1500)
        de_fuerza_bruta = fuerza_bruta_radio(puntos_3d, q, 1500)
        self.assertEqual(sorted(del_arbol), sorted(de_fuerza_bruta))

        punto_arbol, _ = arbol_3d.buscar_vecino(q)
        punto_bruta, _ = fuerza_bruta_vecino(puntos_3d, q)
        self.assertEqual(punto_arbol, punto_bruta)

    def test_arbol_vacio(self):
        arbol_vacio = Quadtree([])
        self.assertEqual(arbol_vacio.contar_puntos(), 0)
        self.assertEqual(arbol_vacio.buscar_radio((5, 5), 500), [])
        self.assertEqual(arbol_vacio.buscar_vecino((5, 5)), (None, float("inf")))


# =====================================================================
# VISUALIZACIONES (se guardan como imagen en la carpeta "graficas")
# =====================================================================

CARPETA_GRAFICAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficas")


def separar_x_y(puntos):
    """Convierte una lista de puntos [(x, y), ...] en dos listas: todas las x y todas las y."""
    xs = []
    ys = []
    for punto in puntos:
        xs.append(punto[0])
        ys.append(punto[1])
    return xs, ys


def dibujar_radio():
    """Dibujo 1: el círculo de 500 m y los puntos que encuentra el árbol."""
    puntos = generar_puntos(10000, semilla=12345)
    arbol = Quadtree(puntos)
    q = (5000, 5000)
    radio = 500

    encontrados = arbol.buscar_radio(q, radio)
    coinciden = sorted(encontrados) == sorted(fuerza_bruta_radio(puntos, q, radio))

    todos_x, todos_y = separar_x_y(puntos)
    enc_x, enc_y = separar_x_y(encontrados)

    figura, (izquierda, derecha) = plt.subplots(1, 2, figsize=(14, 6.5))

    for eje, tamano_punto, titulo in [
        (izquierda, 1, "Todo el mapa (10,000 puntos)"),
        (derecha, 14, "Zoom alrededor del círculo"),
    ]:
        eje.scatter(todos_x, todos_y, s=tamano_punto, color="lightgray", label="Puntos no encontrados")
        eje.scatter(enc_x, enc_y, s=tamano_punto * 3, color="red", label="Encontrados por el árbol")
        eje.add_patch(plt.Circle(q, radio, fill=False, color="blue", linewidth=2))
        eje.scatter([q[0]], [q[1]], marker="*", s=200, color="blue", label="Punto de consulta")
        eje.set_aspect("equal")
        eje.set_title(titulo)
        eje.set_xlabel("x (metros)")
        eje.set_ylabel("y (metros)")

    margen = radio * 1.4
    derecha.set_xlim(q[0] - margen, q[0] + margen)
    derecha.set_ylim(q[1] - margen, q[1] + margen)
    derecha.legend(loc="upper right", fontsize=8)

    veredicto = "igual que fuerza bruta" if coinciden else "DIFERENTE a fuerza bruta"
    figura.suptitle("Búsqueda por radio de %d m: %d puntos encontrados (%s)"
                    % (radio, len(encontrados), veredicto))

    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
    ruta = os.path.join(CARPETA_GRAFICAS, "verificacion_radio.png")
    figura.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(figura)
    print("Guardado:", ruta)


def dibujar_vecinos():
    """Dibujo 2: varios puntos de consulta, cada uno unido a su vecino más cercano."""
    puntos = generar_puntos(10000, semilla=12345)
    arbol = Quadtree(puntos)

    # Para que se vean las líneas, miramos solo un cuadro de 1000 m x 1000 m del mapa
    x_min, x_max = 4000, 5000
    y_min, y_max = 4000, 5000

    en_el_cuadro = []
    for punto in puntos:
        if x_min <= punto[0] <= x_max and y_min <= punto[1] <= y_max:
            en_el_cuadro.append(punto)
    cuadro_x, cuadro_y = separar_x_y(en_el_cuadro)

    azar = random.Random(21)
    consultas = []
    for _ in range(6):
        consultas.append((azar.uniform(x_min, x_max), azar.uniform(y_min, y_max)))

    figura, eje = plt.subplots(figsize=(8, 8))
    eje.scatter(cuadro_x, cuadro_y, s=14, color="lightgray", label="Puntos de entrega")

    todos_coinciden = True
    for q in consultas:
        vecino, d = arbol.buscar_vecino(q)
        if vecino != fuerza_bruta_vecino(puntos, q)[0]:
            todos_coinciden = False

        # círculo con radio = distancia al vecino: adentro no debe haber ningún otro punto
        eje.add_patch(plt.Circle(q, d, fill=False, color="gray", linestyle="--"))
        eje.plot([q[0], vecino[0]], [q[1], vecino[1]], color="red", linewidth=1.5)
        eje.scatter([vecino[0]], [vecino[1]], s=45, color="red", zorder=3)
        eje.scatter([q[0]], [q[1]], marker="*", s=220, color="blue", zorder=3)

    # entradas de leyenda (una sola vez)
    eje.scatter([], [], marker="*", s=120, color="blue", label="Punto de consulta")
    eje.scatter([], [], s=45, color="red", label="Vecino más cercano (árbol)")

    eje.set_xlim(x_min, x_max)
    eje.set_ylim(y_min, y_max)
    eje.set_aspect("equal")
    eje.set_xlabel("x (metros)")
    eje.set_ylabel("y (metros)")
    eje.legend(loc="upper right", fontsize=8)

    veredicto = "iguales a fuerza bruta" if todos_coinciden else "DIFERENTES a fuerza bruta"
    eje.set_title("Vecino más cercano de 6 consultas (%s)\nEl círculo punteado no contiene otros puntos"
                  % veredicto)

    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
    ruta = os.path.join(CARPETA_GRAFICAS, "verificacion_vecinos.png")
    figura.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(figura)
    print("Guardado:", ruta)


if __name__ == "__main__":
    unittest.main(exit=False)   # primero las pruebas
    dibujar_radio()             # luego los dos dibujos
    dibujar_vecinos()
