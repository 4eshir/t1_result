import csv
import random
from MultiGraph import *

class LoadWizard:
    @staticmethod
    def parse_csv(file_path, N = -1):
        vertices_list = []

        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader)  # Пропустить заголовок
            counter = 0
            for row in csv_reader:
                if counter >= N and N != -1:  # Проверка, достигли ли мы N записей
                    break
                counter += 1
                properties_list = set()
                for header, value in zip(headers, row):
                    # Создаем объект Property и добавляем его в список
                    properties_list.add(Property(name=header, value=value))
                vertices_list.append(Vertex(str(counter), properties_list))

        return vertices_list

    @staticmethod
    def create_edges_and_hyperedges(graph: MultiGraph, num_edges_per_vertex: list, vertices_per_hyperedge: int):
        vertices_list = list(graph.vertices)  # Преобразуем множество в список
        num_vertices = len(vertices_list)
        sum_edges = 0

        counter = 1
        # Генерация рёбер Edge
        '''
        for vertex in vertices_list:
            num_edges = random.randint(num_edges_per_vertex[0], num_edges_per_vertex[1])
            sum_edges += num_edges
            for _ in range(num_edges):
                # Выбираем случайную вершину, отличную от текущей
                vertex2 = random.choice([v for v in vertices_list if v != vertex])
                weight = random.randint(1, 10)  # Случайный вес
                edge = Edge(counter, weight, vertex, vertex2)
                graph.add_edge(edge)
                counter += 1
        '''

        # Генерация гиперрёбер Hyperedge
        all_vertices = list(vertices_list)
        random.shuffle(all_vertices)  # Перетасовываем все вершины

        # Создаем гиперрёбра
        for i in range(0, num_vertices, vertices_per_hyperedge):
            hyperedge_vertices = [vertex for vertex in all_vertices[i:i + vertices_per_hyperedge]]
            if len(hyperedge_vertices) < vertices_per_hyperedge:
                break  # Если недостаточно вершин для гиперребра, выходим

            agr_weight = random.randint(1, 10)  # Пример агрегатного веса
            hyperedge = Hyperedge((i + 1), agr_weight, [v for v in hyperedge_vertices])
            graph.add_hyperedge(hyperedge)

        return sum_edges or 0
