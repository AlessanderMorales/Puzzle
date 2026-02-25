import heapq
import random
import time
from dataclasses import dataclass

# 1. LAS REGLAS: Cómo se mueve el vacío (0)
def obtener_vecinos(tablero, n):
    vecinos = []
    z = tablero.index(0)
    x, y = z // n, z % n
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < n and 0 <= ny < n:
            nuevo_z = nx * n + ny
            lista = list(tablero)
            lista[z], lista[nuevo_z] = lista[nuevo_z], lista[z]
            vecinos.append(tuple(lista))
    return vecinos

# 2. LAS PISTAS: h1 (piezas mal) y h2 (distancia Manhattan)
def h1(tablero, meta):
    return sum(1 for i in range(len(tablero)) if tablero[i] != 0 and tablero[i] != meta[i])

def h2(tablero, n, pos_meta):
    dist = 0
    for i, val in enumerate(tablero):
        if val != 0:
            tx, ty = pos_meta[val]
            dist += abs(i // n - tx) + abs(i % n - ty)
    return dist

@dataclass
class ResultadoBusqueda:
    resuelto: bool
    nodos_expandidos: int
    pasos_solucion: int
    tiempo_segundos: float


@dataclass
class ResumenHeuristica:
    partidas: int = 0
    resueltas: int = 0
    tiempo_total: float = 0.0
    nodos_totales: int = 0
    pasos_totales: int = 0


# 3. EL CEREBRO: El buscador A*
def resolver(inicio, meta, n, tipo_h, max_nodos=None):
    inicio_tiempo = time.perf_counter()
    pos_meta = {v: (i // n, i % n) for i, v in enumerate(meta)}
    # Frontera guarda: (f, g, tablero)
    h_ini = h1(inicio, meta) if tipo_h == 'h1' else h2(inicio, n, pos_meta)
    frontera = [(h_ini, 0, inicio)]
    visitados = {inicio: 0}
    nodos = 0

    while frontera:
        f, g, actual = heapq.heappop(frontera)
        if actual == meta:
            return ResultadoBusqueda(True, nodos, g, time.perf_counter() - inicio_tiempo)

        nodos += 1
        if max_nodos is not None and nodos >= max_nodos:
            return ResultadoBusqueda(False, nodos, -1, time.perf_counter() - inicio_tiempo)

        for vecino in obtener_vecinos(actual, n):
            if vecino not in visitados or g + 1 < visitados[vecino]:
                visitados[vecino] = g + 1
                h_v = h1(vecino, meta) if tipo_h == 'h1' else h2(vecino, n, pos_meta)
                heapq.heappush(frontera, (g + 1 + h_v, g + 1, vecino))

    return ResultadoBusqueda(False, nodos, -1, time.perf_counter() - inicio_tiempo)


def generar_partida_aleatoria(meta, n, mezcla):
    actual = meta
    anterior = None

    for _ in range(mezcla):
        vecinos = obtener_vecinos(actual, n)
        if anterior in vecinos and len(vecinos) > 1:
            vecinos.remove(anterior)
        siguiente = random.choice(vecinos)
        anterior, actual = actual, siguiente

    return actual

# 4. LA PRUEBA: El Benchmark
def ejecutar_pruebas(n, vueltas, mezcla):
    print(f"\n--- PRUEBA {n}x{n} ({vueltas} veces) ---")
    meta = tuple(range(1, n*n)) + (0,)
    resumen = {
        'h1': ResumenHeuristica(),
        'h2': ResumenHeuristica(),
    }

    for _ in range(vueltas):
        partida = generar_partida_aleatoria(meta, n, mezcla)

        for heuristica in ('h1', 'h2'):
            resultado = resolver(partida, meta, n, heuristica, max_nodos=200000)
            datos = resumen[heuristica]
            datos.partidas += 1
            datos.tiempo_total += resultado.tiempo_segundos
            datos.nodos_totales += resultado.nodos_expandidos
            if resultado.resuelto:
                datos.resueltas += 1
                datos.pasos_totales += resultado.pasos_solucion

    for heuristica in ('h1', 'h2'):
        datos = resumen[heuristica]
        tiempo_promedio_ms = (datos.tiempo_total / datos.partidas) * 1000 if datos.partidas else 0
        nodos_promedio = datos.nodos_totales / datos.partidas if datos.partidas else 0
        pasos_promedio = (datos.pasos_totales / datos.resueltas) if datos.resueltas else 0

        print(
            f"{heuristica.upper()} | resueltas: {datos.resueltas}/{datos.partidas} | "
            f"tiempo total: {datos.tiempo_total:.2f}s | "
            f"tiempo prom: {tiempo_promedio_ms:.2f} ms/juego | "
            f"nodos prom: {nodos_promedio:.2f} | "
            f"pasos prom (resueltas): {pasos_promedio:.2f}"
        )

# 5. INICIO
if __name__ == "__main__":
    random.seed(42)
    ejecutar_pruebas(3, 5000, 20)
    ejecutar_pruebas(6, 5000, 10)
    ejecutar_pruebas(12, 5000, 5)