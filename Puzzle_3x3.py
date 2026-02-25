import time, heapq, random

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

# 2. LAS PISTAS: h1 (piezas mal) y h2 (distancia)
def h1(tablero, meta):
    return sum(1 for i in range(len(tablero)) if tablero[i] != 0 and tablero[i] != meta[i])

def h2(tablero, n, pos_meta):
    dist = 0
    for i, val in enumerate(tablero):
        if val != 0:
            tx, ty = pos_meta[val]
            dist += abs(i // n - tx) + abs(i % n - ty)
    return dist

# 3. EL CEREBRO: El buscador A*
def resolver(inicio, meta, n, tipo_h):
    pos_meta = {v: (i // n, i % n) for i, v in enumerate(meta)}
    # Frontera guarda: (f, g, tablero)
    h_ini = h1(inicio, meta) if tipo_h == 'h1' else h2(inicio, n, pos_meta)
    frontera = [(h_ini, 0, inicio)]
    visitados = {inicio: 0}
    nodos = 0

    while frontera:
        f, g, actual = heapq.heappop(frontera)
        if actual == meta: return nodos
        nodos += 1
        for vecino in obtener_vecinos(actual, n):
            if vecino not in visitados or g + 1 < visitados[vecino]:
                visitados[vecino] = g + 1
                h_v = h1(vecino, meta) if tipo_h == 'h1' else h2(vecino, n, pos_meta)
                heapq.heappush(frontera, (g + 1 + h_v, g + 1, vecino))
    return nodos

# 4. LA PRUEBA: El Benchmark
def ejecutar_pruebas(n, vueltas, mezcla):
    print(f"\n--- PRUEBA {n}x{n} ({vueltas} veces) ---")
    meta = tuple(range(1, n*n)) + (0,)
    total_t1, total_t2, total_n1, total_n2 = 0, 0, 0, 0

    for _ in range(vueltas):
        # Crear tablero mezclado
        temp = meta
        for _ in range(mezcla):
            temp = random.choice(obtener_vecinos(temp, n))
        
        # Probar H1
        t = time.time()
        total_n1 += resolver(temp, meta, n, 'h1')
        total_t1 += (time.time() - t)

        # Probar H2
        t = time.time()
        total_n2 += resolver(temp, meta, n, 'h2')
        total_t2 += (time.time() - t)

    print(f"H1 (Básica): {total_t1:.2f}s | Nodos: {total_n1//vueltas}")
    print(f"H2 (Lista):  {total_t2:.2f}s | Nodos: {total_n2//vueltas}")

# 5. INICIO
if __name__ == "__main__":
    ejecutar_pruebas(3, 5000, 20)
    ejecutar_pruebas(6, 5000, 10)
    ejecutar_pruebas(12, 5000, 5)