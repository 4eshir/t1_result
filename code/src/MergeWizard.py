import random

import Graph
from datetime import datetime
from History import *

class MergeWizard:
    @staticmethod
    def merge_pair_vertices(vertex1: Vertex, vertex2: Vertex, graph: CombinedGraph):
        # Объединение свойств
        new_properties = vertex1.properties | vertex2.properties

        # Создание новой вершины
        new_vertex = Vertex(vertex1.name + '_' + vertex2.name, new_properties)
        for edge in vertex1.edges:
            new_vertex.add_edge(edge)
        for edge in vertex2.edges:
            new_vertex.add_edge(edge)

        # Добавление новой вершины в граф
        graph.vertices.append(new_vertex)

        # Удаление старых вершин из графа
        graph.vertices.remove(vertex1)
        graph.vertices.remove(vertex2)

        # Поиск рёбер, связанных с vertex1 и vertex2
        edges_to_update = sorted(list(vertex1.edges | vertex2.edges), key=lambda edge: edge.id)

        prev_edges = []
        # Удаление старых рёбер, связанных с vertex1 или vertex2
        for edge in edges_to_update:
            prev_edges.append(edge)
            if edge in graph.edges:
                #vertex1_instance = next((v for v in graph.vertices if v.name == edge.vertex1.name), None)
                #vertex2_instance = next((v for v in graph.vertices if v.name == edge.vertex2.name), None)
                #if vertex1_instance:
                #    vertex1_instance.remove_edge(edge)
                #if vertex2_instance:
                #    vertex2_instance.remove_edge(edge)
                graph.edges.remove(edge)

        new_edges = []
        # Создание новых рёбер
        for edge in edges_to_update:
            old_weight = edge.weight
            print(f'Base_edge: {edge}')

            # Определяем другую вершину
            if (edge.vertex1.name, edge.vertex2.name) not in {(vertex1.name, vertex2.name),
                                                                (vertex2.name, vertex1.name)}:
                if edge.vertex1.name == vertex1.name or edge.vertex1.name == vertex2.name:
                    other_vertex = edge.vertex2
                else:
                    other_vertex = edge.vertex1
            else:
                continue

            edges_vertex1 = new_vertex.edges
            edges_vertex2 = other_vertex.edges

            print('EV1')
            print(', '.join(edge.vertex1.name + '-' + edge.vertex2.name for edge in edges_vertex1))
            print('EV2')
            print(', '.join(edge.vertex1.name + '-' + edge.vertex2.name for edge in edges_vertex2))

            # Ищем пересечение рёбер, чтобы найти существующее
            existing_edge = next((e for e in edges_vertex1 if e in edges_vertex2), None)
            print(f'Existing_edge: {existing_edge}')

            if existing_edge:
                existing_edge.weight = (existing_edge.weight + old_weight) / 2
            elif other_vertex.name != vertex1.name and other_vertex.name != vertex2.name:
                new_edge = Edge()
                new_edge.vertex1 = new_vertex
                new_edge.vertex2 = other_vertex
                new_edge.weight = old_weight
                new_edges.append(new_edge)
                vertex1_instance = next((v for v in graph.vertices if v.name == vertex1.name), None)
                vertex2_instance = next((v for v in graph.vertices if v.name == vertex2.name), None)
                print(f'v1: {vertex1.name}, v2: {vertex2.name}')
                if not (vertex1_instance is None):
                    vertex1_instance.add_edge(new_edge)
                if not (vertex2_instance is None):
                    vertex2_instance.add_edge(new_edge)
                graph.edges.append(new_edge)

        # Обновление гиперрёбер
        hyperedges_to_update = []
        target_hyperedge = None
        for hyperedge in graph.hyperedges:
            if vertex1 in hyperedge.vertices or vertex2 in hyperedge.vertices:
                hyperedges_to_update.append(hyperedge)
                target_hyperedge = hyperedge

        for hyperedge in hyperedges_to_update:
            hyperedge.delete_vertex(vertex1)
            hyperedge.delete_vertex(vertex2)
            hyperedge.add_vertex(new_vertex)

        # Логирование слияния
        LogManager.writeMerge(vertex1, vertex2, new_vertex, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        history_vertex = HistoryVertex(target_hyperedge, new_vertex, vertex1, vertex2, new_edges, prev_edges)
        return history_vertex

    @staticmethod
    def fake_merges(graph: CombinedGraph, merge_count):
        vertices_list = list(graph.vertices)

        for _ in range(merge_count):
            if len(vertices_list) < 2:  # Проверка, достаточно ли вершин для слияния
                print("Недостаточно вершин для слияния.")
                break

            # Выбираем случайную пару вершин для слияния
            vertex1, vertex2 = random.sample(vertices_list, 2)

            if vertex1 != vertex2:  # Проверка на одинаковые вершины
                # Выполняем слияние
                history_vertex = MergeWizard.merge_pair_vertices(vertex1, vertex2, graph)

                # Обновляем список вершин
                vertices_list = list(graph.vertices)
