import time
import heapq
import random
from collections import deque

class PuzzleState:
    def __init__(self, board, n, parent=None, action=None, cost=0, depth=0):
        self.board = board
        self.n = n
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = depth
        self.zero_pos = board.index(0)

    def __lt__(self, other):
        return self.cost < other.cost

    def get_neighbors(self):
        neighbors = []
        x, y = self.zero_pos // self.n, self.zero_pos % self.n
        directions = [(-1, 0, "Arriba"), (1, 0, "Abajo"), (0, -1, "Izquierda"), (0, 1, "Derecha")]
        
        for dx, dy, action in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.n and 0 <= ny < self.n:
                new_pos = nx * self.n + ny
                new_board = list(self.board)
                new_board[self.zero_pos], new_board[new_pos] = new_board[new_pos], new_board[self.zero_pos]
                neighbors.append(PuzzleState(tuple(new_board), self.n, self, action, self.cost + 1, self.depth + 1))
        return neighbors

    def is_goal(self, goal):
        return self.board == goal

    def get_path_states(self):
        states = []
        current = self
        while current:
            states.append(current)
            current = current.parent
        return states[::-1]

def render_board(board):
    n = int(len(board)**0.5)
    line = "+---" * n + "+"
    print(line)
    for i in range(0, n*n, n):
        row = [str(x) if x != 0 else " " for x in board[i:i+n]]
        print(f"| {' | '.join(row)} |")
        print(line)

def h1_misplaced_tiles(board, goal):
    count = 0
    for i in range(len(board)):
        if board[i] != 0 and board[i] != goal[i]:
            count += 1
    return count

def h2_manhattan_distance(board, goal):
    distance = 0
    n = int(len(board)**0.5)
    goal_positions = {val: (i // n, i % n) for i, val in enumerate(goal)}
    for i, val in enumerate(board):
        if val != 0:
            target_x, target_y = goal_positions[val]
            current_x, current_y = i // n, i % n
            distance += abs(current_x - target_x) + abs(current_y - target_y)
    return distance

class Solver:
    def __init__(self, initial_board, goal_board):
        self.n = int(len(initial_board)**0.5)
        self.initial_state = PuzzleState(initial_board, self.n)
        self.goal = goal_board

    def _solve(self, algorithm_name, search_func, show_results=True, show_animation=False):
        start_time = time.time()
        result = search_func()
        end_time = time.time()
        
        execution_time = end_time - start_time
        final_state, expanded_nodes, max_depth = result
        
        if show_results:
            print(f"\n{'='*40}")
            print(f"Agente: {algorithm_name}")
            print(f"{'='*40}")
            
            if final_state is not None:
                path_states = final_state.get_path_states()
                actions = [s.action for s in path_states if s.action]
                print(f"Pasos de la solución: {' -> '.join(actions)}")
                print(f"Distancia total (Pasos): {len(actions)}")
                
                if show_animation:
                    print("\n--- Reproduciendo movimientos ---")
                    for i, state in enumerate(path_states):
                        if state.action:
                            print(f"\nMovimiento {i}: {state.action}")
                        else:
                            print("\nEstado Inicial:")
                        render_board(state.board)
                        time.sleep(0.3)
                    print("\n--- ¡Objetivo alcanzado! ---")
            else:
                print("No se encontró solución.")

            print(f"Nodos expandidos: {expanded_nodes}")
            print(f"Profundidad máxima: {max_depth}")
            print(f"Tiempo de ejecución: {execution_time:.4f} s")
        
        return {
            "execution_time": execution_time,
            "steps": len(final_state.get_path_states()) - 1 if final_state else -1,
            "expanded_nodes": expanded_nodes
        }

    def bfs(self):
        cola = deque([self.initial_state])
        visitados = {self.initial_state.board}
        nodos_expandidos = 0
        max_depth = 0
        
        while cola:
            actual = cola.popleft()
            max_depth = max(max_depth, actual.depth)
            
            if actual.is_goal(self.goal):
                return actual, nodos_expandidos, max_depth
            
            nodos_expandidos += 1
            for vecino in actual.get_neighbors():
                if vecino.board not in visitados:
                    visitados.add(vecino.board)
                    cola.append(vecino)
        return None, nodos_expandidos, max_depth

    def dfs(self, limit=20):
        pila = [self.initial_state]
        visitados = {self.initial_state.board: 0}
        nodos_expandidos = 0
        max_depth = 0
        
        while pila:
            actual = pila.pop()
            max_depth = max(max_depth, actual.depth)
            
            if actual.is_goal(self.goal):
                return actual, nodos_expandidos, max_depth
            
            if actual.depth < limit:
                nodos_expandidos += 1
                for vecino in reversed(actual.get_neighbors()):
                    if vecino.board not in visitados or vecino.depth < visitados[vecino.board]:
                        visitados[vecino.board] = vecino.depth
                        pila.append(vecino)
        return None, nodos_expandidos, max_depth

    def ucs(self):
        frontera = [(0, self.initial_state)]
        visitados = {self.initial_state.board: 0}
        nodos_expandidos = 0
        max_depth = 0
        
        while frontera:
            costo, actual = heapq.heappop(frontera)
            max_depth = max(max_depth, actual.depth)
            
            if actual.is_goal(self.goal):
                return actual, nodos_expandidos, max_depth
            
            nodos_expandidos += 1
            for vecino in actual.get_neighbors():
                if vecino.board not in visitados or vecino.cost < visitados[vecino.board]:
                    visitados[vecino.board] = vecino.cost
                    heapq.heappush(frontera, (vecino.cost, vecino))
        return None, nodos_expandidos, max_depth

    def a_star(self, heuristic_func, w=1.0):
        h = heuristic_func(self.initial_state.board, self.goal)
        frontera = [(h, self.initial_state)]
        visitados = {self.initial_state.board: 0}
        nodos_expandidos = 0
        max_depth = 0
        
        while frontera:
            f, actual = heapq.heappop(frontera)
            max_depth = max(max_depth, actual.depth)
            
            if actual.is_goal(self.goal):
                return actual, nodos_expandidos, max_depth
            
            nodos_expandidos += 1
            for vecino in actual.get_neighbors():
                if vecino.board not in visitados or vecino.cost < visitados[vecino.board]:
                    visitados[vecino.board] = vecino.cost
                    h_n = heuristic_func(vecino.board, self.goal)
                    f_n = vecino.cost + (w * h_n)
                    heapq.heappush(frontera, (f_n, vecino))
        return None, nodos_expandidos, max_depth

    def greedy_bfs(self, heuristic_func):
        h = heuristic_func(self.initial_state.board, self.goal)
        frontera = [(h, self.initial_state)]
        visitados = {self.initial_state.board}
        nodos_expandidos = 0
        max_depth = 0
        
        while frontera:
            h_n, actual = heapq.heappop(frontera)
            max_depth = max(max_depth, actual.depth)
            
            if actual.is_goal(self.goal):
                return actual, nodos_expandidos, max_depth
            
            nodos_expandidos += 1
            for vecino in actual.get_neighbors():
                if vecino.board not in visitados:
                    visitados.add(vecino.board)
                    h_v = heuristic_func(vecino.board, self.goal)
                    heapq.heappush(frontera, (h_v, vecino))
        return None, nodos_expandidos, max_depth

def generate_random_solvable_board(n, shuffle_steps=50):
    goal = tuple(range(1, n*n)) + (0,)
    current = PuzzleState(goal, n)
    for _ in range(shuffle_steps):
        neighbors = current.get_neighbors()
        if neighbors:
            current = random.choice(neighbors)
    return current.board, goal

def run_benchmarks(n=3, iterations=5000, shuffle_steps=20):
    print(f"\n--- Iniciando Benchmark: {iterations} iteraciones ({n}x{n}) ---")
    metrics_h1 = {"time": 0, "steps": 0, "expanded": 0}
    metrics_h2 = {"time": 0, "steps": 0, "expanded": 0}
    
    for i in range(iterations):
        initial, goal = generate_random_solvable_board(n, shuffle_steps)
        solver = Solver(initial, goal)
        
        # Benchmark h1
        res1 = solver._solve("h1", lambda: solver.a_star(h1_misplaced_tiles), show_results=False)
        metrics_h1["time"] += res1["execution_time"]
        metrics_h1["steps"] += res1["steps"]
        metrics_h1["expanded"] += res1["expanded_nodes"]
        
        # Benchmark h2
        res2 = solver._solve("h2", lambda: solver.a_star(h2_manhattan_distance), show_results=False)
        metrics_h2["time"] += res2["execution_time"]
        metrics_h2["steps"] += res2["steps"]
        metrics_h2["expanded"] += res2["expanded_nodes"]
        
        if (i + 1) % 500 == 0:
            print(f"Progreso {n}x{n}: {i + 1}/{iterations}...")

    print(f"\nRESULTADOS PROMEDIO ({n}x{n}, {iterations} iteraciones):")
    print(f"{'-'*40}")
    print(f"Heurística h1 (Misplaced Tiles):")
    print(f"  Tiempo promedio: {metrics_h1['time']/iterations:.6f} s")
    print(f"  Pasos promedio:  {metrics_h1['steps']/iterations:.2f}")
    print(f"  Nodos expandidos: {metrics_h1['expanded']/iterations:.2f}")
    
    print(f"\nHeurística h2 (Manhattan Distance):")
    print(f"  Tiempo promedio: {metrics_h2['time'] / iterations:.6f} s")
    print(f"  Pasos promedio:  {metrics_h2['steps'] / iterations:.2f}")
    print(f"  Nodos expandidos: {metrics_h2['expanded'] / iterations:.2f}")

def main():
    run_benchmarks(n=3, iterations=5000, shuffle_steps=20)
    

    run_benchmarks(n=6, iterations=5000, shuffle_steps=10)
    
    run_benchmarks(n=12, iterations=5000, shuffle_steps=5)

if __name__ == "__main__":
    main()
