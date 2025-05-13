import numpy as np
from app.schemas.graph import Graph, PathResult

# Класс для реализации алгоритма муравьиной колонии (ACO) для поиска кратчайшего пути
class AntColonyOptimization:
    # Инициализация с графом, количеством муравьёв и итераций
    def __init__(self, graph: Graph):
        self.graph = graph  # Граф с узлами и рёбрами
        self.num_cities = len(graph.nodes)  # Количество узлов (городов)
        self.distance_matrix = self.create_distance_matrix()  # Матрица расстояний между узлами
        self.num_ants = 10  # Количество муравьёв
        self.num_iterations = 50  # Количество итераций алгоритма

    # Создание матрицы расстояний на основе рёбер графа
    def create_distance_matrix(self):
        # Создаём матрицу, заполненную бесконечностями
        matrix = np.full((self.num_cities, self.num_cities), np.inf)
        # Для каждого ребра устанавливаем расстояние 1 (неориентированный граф)
        for edge in self.graph.edges:
            i, j = edge  # Ребро между узлами i и j
            matrix[i-1, j-1] = 1  # Расстояние от i к j
            matrix[j-1, i-1] = 1  # Расстояние от j к i
        # Устанавливаем диагональные элементы в 0 (расстояние от узла к самому себе)
        np.fill_diagonal(matrix, 0)
        return matrix

    # Запуск алгоритма для поиска кратчайшего гамильтонова пути
    def run(self):
        best_route = None  # Лучший найденный маршрут
        best_distance = float('inf')  # Лучшее найденное расстояние (минимизируем)

        # Выполняем заданное количество итераций
        for _ in range(self.num_iterations):
            # Для каждого муравья строим маршрут
            for _ in range(self.num_ants):
                # Начинаем с случайного узла
                route = [np.random.randint(self.num_cities)]
                # Множество непосещённых узлов
                unvisited = set(range(self.num_cities)) - {route[0]}

                # Пока есть непосещённые узлы
                while unvisited:
                    current = route[-1]  # Текущий узел
                    next_city = None  # Следующий узел
                    min_dist = float('inf')  # Минимальное расстояние

                    # Ищем ближайший непосещённый узел
                    for city in unvisited:
                        if self.distance_matrix[current, city] < min_dist:
                            min_dist = self.distance_matrix[current, city]
                            next_city = city

                    # Если следующий узел не найден, прерываем
                    if next_city is None:
                        break
                    # Добавляем узел в маршрут и убираем из непосещённых
                    route.append(next_city)
                    unvisited.remove(next_city)

                # Проверяем, что маршрут полный (все узлы посещены)
                if len(unvisited) == 0 and len(set(route)) == self.num_cities:
                    route_distance = len(route)  # Длина маршрута
                    # Если маршрут короче лучшего, обновляем лучший
                    if route_distance < best_distance:
                        best_distance = route_distance
                        best_route = route

        # Если маршрут найден, возвращаем результат
        if best_route:
            # Преобразуем индексы узлов в их значения из графа
            path = [self.graph.nodes[i] for i in best_route]
            return PathResult(path=path, total_distance=float(best_distance))
        else:
            return None  # Если путь не найден, возвращаем None