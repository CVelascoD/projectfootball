import heapq
import math
from typing import Tuple, List, Optional

class AStarPlanner:
    """
    Planificador A* en grilla coarse.
    Se usa como fallback cuando hay muchos oponentes bloqueando.
    """
    
    def __init__(self, cell_size=2.0):
        """
        cell_size: tamaño de cada celda en metros (por defecto 2m)
        Campo RoboCup: [-52.5, 52.5] x [-34, 34]
        """
        self.cell_size = cell_size
        self.field_x_min, self.field_x_max = -52.5, 52.5
        self.field_y_min, self.field_y_max = -34.0, 34.0
        
        self.grid_width = int((self.field_x_max - self.field_x_min) / cell_size)
        self.grid_height = int((self.field_y_max - self.field_y_min) / cell_size)
    
    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convierte coordenadas mundo a índices grilla"""
        gx = int((world_x - self.field_x_min) / self.cell_size)
        gy = int((world_y - self.field_y_min) / self.cell_size)
        
        gx = max(0, min(gx, self.grid_width - 1))
        gy = max(0, min(gy, self.grid_height - 1))
        return gx, gy
    
    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        """Convierte índices grilla a coordenadas mundo"""
        wx = self.field_x_min + gx * self.cell_size + self.cell_size / 2
        wy = self.field_y_min + gy * self.cell_size + self.cell_size / 2
        return wx, wy
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Distancia Chebyshev (8-conectividad)"""
        return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Obtiene vecinos válidos (8-conectividad)"""
        gx, gy = pos
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = gx + dx
                ny = gy + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    neighbors.append((nx, ny))
        return neighbors
    
    def plan(self, 
             start_world: Tuple[float, float], 
             goal_world: Tuple[float, float],
             obstacles_world: Optional[List[Tuple[float, float]]] = None) -> Optional[List[Tuple[float, float]]]:
        """
        Planifica ruta desde start a goal evitando obstáculos.
        
        Args:
            start_world: (x, y) posición inicial en mundo
            goal_world: (x, y) posición objetivo en mundo
            obstacles_world: lista de (x, y) de obstáculos (oponentes)
        
        Returns:
            Lista de waypoints (coords mundo) o None si no hay ruta
        """
        if obstacles_world is None:
            obstacles_world = []
        
        start_grid = self.world_to_grid(*start_world)
        goal_grid = self.world_to_grid(*goal_world)
        
        # Convertir obstáculos a grilla con zona de seguridad
        obstacles = set()
        for ox, oy in obstacles_world:
            ogx, ogy = self.world_to_grid(ox, oy)
            # Marcar celda y vecinos como obstáculo
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    obs_cell = (ogx + dx, ogy + dy)
                    if 0 <= obs_cell[0] < self.grid_width and 0 <= obs_cell[1] < self.grid_height:
                        obstacles.add(obs_cell)
        
        # A* estándar
        open_set = [(0, start_grid)]
        came_from = {}
        g_score = {start_grid: 0}
        closed_set = set()
        
        iteration = 0
        max_iterations = self.grid_width * self.grid_height  # Límite para evitar loops
        
        while open_set and iteration < max_iterations:
            iteration += 1
            _, current = heapq.heappop(open_set)
            
            if current in closed_set:
                continue
            closed_set.add(current)
            
            if current == goal_grid:
                # Reconstruir ruta
                path = []
                node = current
                while node in came_from:
                    path.append(self.grid_to_world(*node))
                    node = came_from[node]
                path.append(start_world)
                return list(reversed(path))
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set or neighbor in obstacles:
                    continue
                
                # Costo de movimiento (diagonal = 1.41, ortogonal = 1)
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                move_cost = 1.41 if dx == 1 and dy == 1 else 1.0
                
                tentative_g = g_score[current] + move_cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, goal_grid)
                    heapq.heappush(open_set, (f, neighbor))
        
        return None  # Sin ruta encontrada