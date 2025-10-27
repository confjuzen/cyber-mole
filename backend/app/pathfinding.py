import heapq
from typing import List, Tuple
import random
import math

class Grid:
    def __init__(self, width: int, height: int, obstacles: set = None):
        self.width = width
        self.height = height
        self.obstacles = obstacles or set()

    def is_valid(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.obstacles

    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return [(x + dx, y + dy) for dx, dy in directions if self.is_valid(x + dx, y + dy)]

def a_star(grid: Grid, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        current = heapq.heappop(frontier)[1]
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for neighbor in grid.neighbors(*current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + math.hypot(neighbor[0] - goal[0], neighbor[1] - goal[1])
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current
    return []

# Genetic Algorithm for multi-stop optimization (TSP-like)
class GAOptimizer:
    def __init__(self, grid: Grid, population_size: int = 100, generations: int = 100):
        self.grid = grid
        self.population_size = population_size
        self.generations = generations

    def distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        path = a_star(self.grid, a, b)
        return len(path) if path else float('inf')

    def fitness(self, route: List[Tuple[int, int]]) -> float:
        if not route:
            return float('inf')
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.distance(route[i], route[i + 1])
        return total_distance

    def create_individual(self, points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        return random.sample(points, len(points))  # Random permutation

    def mutate(self, individual: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(individual) < 2:
            return individual
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
        return individual

    def crossover(self, parent1: List[Tuple[int, int]], parent2: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(parent1) < 2:
            return parent1
        cut = random.randint(1, len(parent1) - 1)
        child = parent1[:cut] + [p for p in parent2 if p not in parent1[:cut]]
        return child

    def optimize(self, points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        population = [self.create_individual(points) for _ in range(self.population_size)]
        for _ in range(self.generations):
            population.sort(key=self.fitness)
            new_population = population[:10]  # Elite
            while len(new_population) < self.population_size:
                parent1, parent2 = random.choices(population[:50], k=2)
                child = self.crossover(parent1, parent2)
                if random.random() < 0.1:
                    child = self.mutate(child)
                new_population.append(child)
            population = new_population
        return min(population, key=self.fitness)

# Example usage
def get_robot_path(grid: Grid, start: Tuple[int, int], pick_list: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not pick_list:
        return []
    optimizer = GAOptimizer(grid)
    optimized_route = optimizer.optimize(pick_list)
    full_path = [start]
    for point in optimized_route:
        path = a_star(grid, full_path[-1], point)
        if path:
            full_path.extend(path[1:])
    return full_path