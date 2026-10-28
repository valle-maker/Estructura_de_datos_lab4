"""
Quadtreetree.py
---------------
Quadtree (para K dimensiones) hecho desde cero, más la solución por fuerza
bruta para poder compararlos.

Contenido:
    generar_puntos          -> crea los datos (tuplas de coordenadas)
    NodoQuadtree            -> un nodo del árbol (una región del espacio)
    distancia               -> distancia entre dos puntos
    distancia_a_region      -> distancia de un punto a una región
    fuerza_bruta_radio      -> puntos dentro de un radio, revisando todos
    fuerza_bruta_vecino     -> vecino más cercano, revisando todos
    Quadtree                -> el árbol: construir, buscar por radio, vecino más cercano

Unidades: las coordenadas están en metros (la zona es un cuadrado de
10,000 m x 10,000 m), así que un radio de 500 son 500 metros.
"""

import math
import random


# =====================================================================
# 1. DATOS
# =====================================================================

def generar_puntos(cantidad, dimensiones=2, lado=10000, semilla=None):
    """
    Genera 'cantidad' puntos al azar dentro de un cuadrado (o cubo...) de
    lado 'lado'. Cada punto es una tupla con 'dimensiones' números.
    Si se da una semilla, los puntos siempre son los mismos.
    """
    if semilla is not None:
        random.seed(semilla)

    puntos = []
    for _ in range(cantidad):
        coordenadas = []
        for _ in range(dimensiones):
            coordenadas.append(random.uniform(0, lado))
        puntos.append(tuple(coordenadas))

    return puntos


# =====================================================================
# 2. EL NODO
# =====================================================================

class NodoQuadtree:
    """
    Un nodo del árbol: representa una región (cuadrado, cubo...) del espacio.
    Si es hoja, guarda puntos. Si no, guarda sus 2^K hijos.
    """

    def __init__(self, minimos, maximos, nivel=0):
        self.minimos = minimos    # mínimo de cada eje, por ejemplo (0, 0)
        self.maximos = maximos    # máximo de cada eje, por ejemplo (100, 100)
        self.nivel = nivel        # profundidad: la raíz es 0
        self.puntos = []          # solo se usa si el nodo es hoja
        self.hijos = None         # None = es hoja; si no, lista de 2^K hijos

    def es_hoja(self):
        return self.hijos is None

    def centro(self):
        """Punto medio de la región, eje por eje."""
        centro = []
        for eje in range(len(self.minimos)):
            centro.append((self.minimos[eje] + self.maximos[eje]) / 2)
        return tuple(centro)

    def numero_de_hijo(self, punto):
        """
        En qué casilla de la lista de hijos va un punto.
        Por cada eje: si el punto es mayor o igual que el centro, suma 2**eje
        (1 para el eje 0, 2 para el eje 1, 4 para el eje 2...).
        """
        centro = self.centro()
        numero = 0
        for eje in range(len(centro)):
            if punto[eje] >= centro[eje]:
                numero += 2 ** eje
        return numero

    def limites_de_hijo(self, numero):
        """Límites (minimos, maximos) del hijo que va en la casilla 'numero'."""
        centro = self.centro()
        minimos_hijo = []
        maximos_hijo = []
        for eje in range(len(centro)):
            if (numero // 2 ** eje) % 2 == 1:
                # en este eje le toca la mitad de arriba: de centro a máximo
                minimos_hijo.append(centro[eje])
                maximos_hijo.append(self.maximos[eje])
            else:
                # en este eje le toca la mitad de abajo: de mínimo a centro
                minimos_hijo.append(self.minimos[eje])
                maximos_hijo.append(centro[eje])
        return tuple(minimos_hijo), tuple(maximos_hijo)

    def dividir(self):
        """Parte este nodo: crea sus 2^K hijos y reparte sus puntos entre ellos."""
        cantidad_de_hijos = 2 ** len(self.minimos)

        self.hijos = []
        for numero in range(cantidad_de_hijos):
            minimos, maximos = self.limites_de_hijo(numero)
            self.hijos.append(NodoQuadtree(minimos, maximos, self.nivel + 1))

        for punto in self.puntos:
            self.hijos[self.numero_de_hijo(punto)].puntos.append(punto)

        self.puntos = []


# =====================================================================
# 3. DISTANCIAS Y FUERZA BRUTA
# =====================================================================

def distancia(a, b):
    """Distancia entre dos puntos (a y b son tuplas con las coordenadas)."""
    suma = 0
    for eje in range(len(a)):
        suma += (a[eje] - b[eje]) ** 2
    return math.sqrt(suma)


def distancia_a_region(punto, minimos, maximos):
    """
    Distancia del punto al punto más cercano de la región.
    Si el punto está dentro de la región, la distancia es 0.
    """
    suma = 0
    for eje in range(len(punto)):
        if punto[eje] < minimos[eje]:
            diferencia = minimos[eje] - punto[eje]
        elif punto[eje] > maximos[eje]:
            diferencia = punto[eje] - maximos[eje]
        else:
            diferencia = 0
        suma += diferencia ** 2
    return math.sqrt(suma)


def fuerza_bruta_radio(puntos, q, radio):
    """Puntos a 'radio' o menos de q, revisando TODOS los puntos."""
    encontrados = []
    for punto in puntos:
        if distancia(punto, q) <= radio:
            encontrados.append(punto)
    return encontrados


def fuerza_bruta_vecino(puntos, q):
    """Punto más cercano a q, revisando TODOS. Devuelve (punto, distancia)."""
    mejor = None
    mejor_distancia = float("inf")
    for punto in puntos:
        d = distancia(punto, q)
        if d < mejor_distancia:
            mejor = punto
            mejor_distancia = d
    return mejor, mejor_distancia


# =====================================================================
# 4. EL ÁRBOL
# =====================================================================

class Quadtree:
    """El árbol completo: guarda la raíz y las reglas (capacidad, nivel máximo)."""

    def __init__(self, puntos, dimensiones=2, capacidad=4, nivel_maximo=20):
        self.dimensiones = dimensiones
        self.capacidad = capacidad
        self.nivel_maximo = nivel_maximo

        # La región de la raíz sale de los datos: el mínimo y el máximo de cada eje
        if len(puntos) > 0:
            minimos = []
            maximos = []
            for eje in range(dimensiones):
                valores = []
                for punto in puntos:
                    valores.append(punto[eje])
                minimos.append(min(valores))
                maximos.append(max(valores))
        else:
            minimos = [0] * dimensiones
            maximos = [1] * dimensiones

        self.raiz = NodoQuadtree(tuple(minimos), tuple(maximos))

        for punto in puntos:
            self.insertar(punto)

    def insertar(self, punto):
        """Baja hasta la hoja que le toca al punto, lo guarda, y parte si hace falta."""
        nodo = self.raiz
        while not nodo.es_hoja():
            nodo = nodo.hijos[nodo.numero_de_hijo(punto)]

        nodo.puntos.append(punto)
        self._partir_si_hace_falta(nodo)

    def _partir_si_hace_falta(self, nodo):
        """Si la hoja se pasó de la capacidad, la parte (y revisa a sus hijos)."""
        if len(nodo.puntos) > self.capacidad and nodo.nivel < self.nivel_maximo:
            nodo.dividir()
            for hijo in nodo.hijos:
                self._partir_si_hace_falta(hijo)

    def contar_puntos(self):
        """Cuenta cuántos puntos hay en todo el árbol (sirve para las pruebas)."""
        return self._contar(self.raiz)

    def _contar(self, nodo):
        if nodo.es_hoja():
            return len(nodo.puntos)
        total = 0
        for hijo in nodo.hijos:
            total += self._contar(hijo)
        return total

    # ---------------- búsqueda por radio ----------------

    def buscar_radio(self, q, radio):
        """Todos los puntos a 'radio' o menos de q."""
        encontrados = []
        self._buscar_radio(self.raiz, q, radio, encontrados)
        return encontrados

    def _buscar_radio(self, nodo, q, radio, encontrados):
        # 1. Si el círculo no toca esta región, se descarta todo lo de adentro
        if distancia_a_region(q, nodo.minimos, nodo.maximos) > radio:
            return

        if nodo.es_hoja():
            # 2. Hoja: se mide la distancia a cada punto real
            for punto in nodo.puntos:
                if distancia(punto, q) <= radio:
                    encontrados.append(punto)
        else:
            # 3. Nodo interno: se repite lo mismo con cada hijo
            for hijo in nodo.hijos:
                self._buscar_radio(hijo, q, radio, encontrados)

    # ---------------- vecino más cercano ----------------

    def buscar_vecino(self, q):
        """El punto más cercano a q. Devuelve (punto, distancia)."""
        self._mejor = None
        self._mejor_distancia = float("inf")
        self._buscar_vecino(self.raiz, q)
        return self._mejor, self._mejor_distancia

    def _buscar_vecino(self, nodo, q):
        # 1. Si esta región está más lejos que el mejor que ya tenemos, se descarta
        if distancia_a_region(q, nodo.minimos, nodo.maximos) >= self._mejor_distancia:
            return

        if nodo.es_hoja():
            # 2. Hoja: si algún punto es mejor que el mejor actual, lo reemplaza
            for punto in nodo.puntos:
                d = distancia(punto, q)
                if d < self._mejor_distancia:
                    self._mejor = punto
                    self._mejor_distancia = d
        else:
            # 3. Nodo interno: visitar los hijos del más cercano al más lejano
            candidatos = []
            for numero in range(len(nodo.hijos)):
                hijo = nodo.hijos[numero]
                candidatos.append((distancia_a_region(q, hijo.minimos, hijo.maximos), numero))
            candidatos.sort()
            for distancia_hijo, numero in candidatos:
                self._buscar_vecino(nodo.hijos[numero], q)


# =====================================================================
# PRUEBA RÁPIDA (solo se ejecuta si corres este archivo directamente)
# =====================================================================

if __name__ == "__main__":
    # Los datos
    print(generar_puntos(5, semilla=12345))

    # El nodo
    nodo = NodoQuadtree((0, 0), (100, 100))
    print(nodo.es_hoja(), nodo.centro())
    print(nodo.numero_de_hijo((70, 20)), nodo.numero_de_hijo((30, 80)), nodo.numero_de_hijo((60, 90)))

    # Un mapa pequeño de 8 puntos para verificar a mano
    puntos_ejemplo = [(15, 85), (35, 70), (20, 60), (80, 80), (65, 55), (30, 20), (60, 10), (85, 25)]
    arbol_pequeno = Quadtree(puntos_ejemplo, capacidad=2)
    print(arbol_pequeno.buscar_radio((80, 15), 12))      # [(85, 25)]
    print(arbol_pequeno.buscar_vecino((45, 45)))          # ((65, 55), 22.36...)

    # El árbol con 10,000 puntos
    puntos = generar_puntos(10000, semilla=12345)
    arbol = Quadtree(puntos)
    print(arbol.contar_puntos())                          # 10000
    q = (5000, 5000)
    print(len(arbol.buscar_radio(q, 500)), len(fuerza_bruta_radio(puntos, q, 500)))
    print(arbol.buscar_vecino(q)[1], fuerza_bruta_vecino(puntos, q)[1])