import random
from typing import Optional, List
import copy
from datetime import datetime

class Property:
    def __init__(self, name = '', value = '', trusted_coefficient = 1):
        self.name = name
        self.value = value
        self.trusted_coefficient = trusted_coefficient

class Edge:
    def __init__(self, id, weight, v1_id, v2_id):
        self.id = id
        self.weight = weight
        self.v1_id = v1_id
        self.v2_id = v2_id

class Hyperedge:
    def __init__(self, id, agr_weight, v_ids: list = None):
        self.id = id
        self.agr_weight = agr_weight
        self.v_ids = v_ids or []

class Vertex:
    def __init__(self, id, properties: set = None, is_trusted = 0, completeness_coef = 0.0, last_update = '1900-01-01', edges: set = None, hyperedges: set = None):
        self.id = id
        self.properties = properties or set()
        self.completeness_coef = completeness_coef
        self.is_trusted = is_trusted
        self.last_update = last_update
        self.edges = edges or set()
        self.hyperedges = hyperedges or set()

    def add_edge(self, edge: Edge):
        self.edges.add(edge)


class MultiGraph:
    def __init__(self, vertices: list = None):
        self.vertices = {vertex.id: vertex for vertex in vertices} if vertices else {}
        self.edges = set()
        self.hyperedges = set()
        for vertex in self.vertices.values():
            self.edges.update(vertex.edges)
            self.hyperedges.update(vertex.hyperedges)

    def get_state(self):
        return {
            'vertices': self.vertices,
            'edges': self.edges,
            'hyperedges': self.hyperedges
        }

    def add_edge(self, edge: 'Edge'):
        self.vertices[edge.v1_id].edges.add(edge)
        self.vertices[edge.v2_id].edges.add(edge)
        self.edges.add(edge)

    def add_hyperedge(self, hyperedge: 'Hyperedge'):
        self.hyperedges.add(hyperedge)
        for vertex_id in hyperedge.v_ids:
            if vertex_id in self.vertices:
                self.vertices[vertex_id].hyperedges.add(hyperedge)

    def add_vertex(self, vertex: 'Vertex'):
        self.vertices[vertex.id] = vertex
        self.edges.update(vertex.edges)

    def remove_vertex(self, v_id):
        if v_id in self.vertices:
            del self.vertices[v_id]

    def remove_edge(self, edge: 'Edge'):
        self.vertices[edge.v1_id].edges.remove(edge)
        self.vertices[edge.v2_id].edges.remove(edge)

    def remove_hyperedge(self, hyperedge: 'Hyperedge'):
        for vertex in hyperedge.v_ids:
            self.vertices[vertex].hyperedges.remove(hyperedge)

    def get_same_vertex(self, edge1: 'Edge', edge2: 'Edge', v1: 'Vertex', v2: 'Vertex'):
        if (edge1.v1_id == edge2.v1_id or edge1.v1_id == edge2.v2_id) and not(edge1.v1_id == v1.id or edge1.v1_id == v2.id):
            return edge1.v1_id
        elif (edge1.v2_id == edge2.v1_id or edge1.v2_id == edge2.v2_id) and not(edge1.v2_id == v1.id or edge1.v2_id == v2.id):
            return edge1.v2_id
        else:
            return -1

    def get_different_vertex(self, edge, vertex):
        vertexes = vertex.id.split("_")
        for vertex in vertexes:
            if vertex == edge.v1_id:
                return edge.v2_id
            if vertex == edge.v2_id:
                return edge.v1_id

        return -1

    def merge_properties(self, v1: Vertex, v2: Vertex):
        new_properties = set()
        v1_properties = sorted(list(v1.properties), key=lambda x: x.name)
        v2_properties = sorted(list(v2.properties), key=lambda x: x.name)

        for prop1, prop2 in zip(v1_properties, v2_properties):
            if prop1.trusted_coefficient > prop2.trusted_coefficient:
                new_properties.add(prop1)
            elif prop1.trusted_coefficient < prop2.trusted_coefficient:
                new_properties.add(prop2)
            elif prop1.trusted_coefficient == 1 and prop2.trusted_coefficient == 1:
                if datetime.strptime(v1.last_update, '%Y-%m-%d') > datetime.strptime(v2.last_update, '%Y-%m-%d'):
                    new_properties.add(prop1)
                elif datetime.strptime(v1.last_update, '%Y-%m-%d') < datetime.strptime(v2.last_update, '%Y-%m-%d'):
                    new_properties.add(prop2)
                elif v1.completeness_coef > v2.completeness_coef:
                    new_properties.add(prop1)
                else:
                    new_properties.add(prop2)
            elif prop1.trusted_coefficient == -1 and prop2.trusted_coefficient == -1:
                new_properties.add(Property(prop1.name))
            elif prop1.trusted_coefficient == 0 and prop2.trusted_coefficient == 0:
                if v1.completeness_coef > v2.completeness_coef:
                    new_properties.add(prop1)
                else:
                    new_properties.add(prop2)
            else:
                new_properties.add(random.choice([prop1, prop2]))

        return new_properties

    def merge_vertex(self, v1: 'Vertex', v2: 'Vertex', debug = False):
        new_id = f"{v1.id}_{v2.id}"
        new_properties = self.merge_properties(v1, v2)

        new_vertex = Vertex(new_id, new_properties)
        self.add_vertex(new_vertex)

        remove_edges_1 = set()
        remove_edges_2 = set()
        solo_edges = set()
        add_edges = set()

        if debug:
            # ищем повторы а заодно сливаем одинаковые ребра со средним весом
            for edge1 in v1.edges:
                flag = -1
                sum = edge1.weight
                for edge2 in v2.edges:
                    edge2_instance = self.get_same_vertex(edge1, edge2, v1, v2)
                    if edge2_instance != -1:
                        sum += edge2.weight
                        flag = edge2_instance
                avg_weight = sum / 2
                if flag != -1:
                    new_edge = Edge(len(self.edges) + 1, avg_weight, new_id, flag)
                    self.add_edge(new_edge)
                    add_edges.add(new_edge)
                else:
                    solo_edges.add(edge1)

            # пройдемся в обратном порядке но без слияния, просто ищем одиночные ребра
            for edge1 in v2.edges:
                flag = -1
                for edge2 in v1.edges:
                    edge2_instance = self.get_same_vertex(edge1, edge2, v1, v2)
                    if edge2_instance != -1:
                        flag = edge2_instance
                if flag == -1:
                    solo_edges.add(edge1)

            for edge in solo_edges:
                old_vertex = self.get_different_vertex(edge, new_vertex)
                if old_vertex != -1:
                    self.add_edge(Edge(len(self.edges) + 1, edge.weight, new_id, old_vertex))

            for edge in list(v1.edges):
                remove_edges_1.add(edge)
                self.remove_edge(edge)

            for edge in list(v2.edges):
                remove_edges_2.add(edge)
                self.remove_edge(edge)

        history_vertex = HistoryVertex(new_vertex, v1, v2, add_edges, remove_edges_1, remove_edges_2)

        self.remove_vertex(v1.id)
        self.remove_vertex(v2.id)

        return history_vertex

    def __str__(self):
        result = "MultiGraph:\n"
        result += "Vertices:\n"
        for vertex in self.vertices.values():
            result += f"  ID: {vertex.id}, Edges: {[edge.weight for edge in vertex.edges]}, Hyperedges: {[hyperedge.id for hyperedge in vertex.hyperedges]}\n"

        result += "Edges:\n"
        edges = set()
        for vertex in self.vertices.values():
            for edge in vertex.edges:
                edges.add(edge)

        for edge in edges:
            result += f"  Edge: ({edge.v1_id} -- {edge.v2_id}) id: {edge.id} weight: {edge.weight} \n"

        result += "Hyperedges:\n"
        hyperedges = set()
        for vertex in self.vertices.values():
            for hyperedge in vertex.hyperedges:
                hyperedges.add(hyperedge)

        for hyperedge in hyperedges:
            result += f"  Hyperedge: {hyperedge.id}, Vertices: {hyperedge.v_ids}\n"

        return result

    def fake_merges(self, merge_count):
        vertices_list = list(self.vertices.values())  # Получаем список объектов Vertex

        for _ in range(merge_count):
            if len(vertices_list) < 2:  # Проверка, достаточно ли вершин для слияния
                print("Недостаточно вершин для слияния.")
                break

            # Выбираем случайную пару вершин для слияния
            vertex1, vertex2 = random.sample(vertices_list, 2)

            # Выполняем слияние
            history_vertex = self.merge_vertex(vertex1, vertex2, True)

            # Обновляем список вершин
            vertices_list = list(self.vertices.values())  # Обновляем список объектов Vertex

    def collapse_hyperedges(self):
        for hyperedge in self.hyperedges:
            new_vertex = self.vertices[hyperedge.v_ids[0]]
            for v_id in hyperedge.v_ids[1:]:
                new_vertex = self.merge_vertex(new_vertex, self.vertices[v_id]).vertex
            hyperedge.v_ids = [new_vertex.id]


class HistoryVertex:
    def __init__(self, vertex: Vertex, prev_vertex_1: Optional[Vertex] = None,
                 prev_vertex_2: Optional[Vertex] = None, add_edges: set = None,
                 prev_edges_1: set = None, prev_edges_2: set = None):
        self.vertex = vertex
        #self.vertex.edges.update(add_edges)
        self.prev_vertex_1 = prev_vertex_1
        self.prev_vertex_1.edges = prev_edges_1
        self.prev_vertex_2 = prev_vertex_2
        self.prev_vertex_2.edges = prev_edges_2

    def __str__(self):
        return f'V: {self.vertex.id} V1: {self.prev_vertex_1.id} V2: {self.prev_vertex_2.id}'


class HistoryManager:
    def __init__(self, graph: MultiGraph):
        self.graph = graph
        self.base_state = copy.deepcopy(graph.get_state())
        self.history: List[HistoryVertex] = []
        self.current_step = -1

    def return_to_base_state(self):
        base_state_data = self.base_state
        self.graph.vertices = {}
        self.graph.edges = set()
        for vertex in base_state_data['vertices'].values():
            self.graph.add_vertex(vertex)
        self.graph.edges.update(base_state_data['edges'])
        self.current_step = -1

    def write_step(self, vertex: HistoryVertex):
        self.history.append(vertex)
        self.current_step = len(self.history) - 1

    def next_step(self):
        if self.current_step >= len(self.history) - 1:
            return
        if self.current_step == -1:
            self.current_step = 0
        else:
            self.current_step += 1
        self.graph.add_vertex(self.history[self.current_step].vertex)
        self.graph.remove_vertex(self.history[self.current_step].prev_vertex_1.id)
        self.graph.remove_vertex(self.history[self.current_step].prev_vertex_2.id)

    def prev_step(self):
        if self.current_step < 0:
            return
        if self.current_step == 0:
            self.return_to_base_state()
            return
        print(f'Vertex {self.history[self.current_step].vertex.id} Edges {[edge for edge in self.history[self.current_step].vertex.edges]}')
        self.graph.remove_vertex(self.history[self.current_step].vertex.id)
        self.graph.add_vertex(self.history[self.current_step].prev_vertex_1)
        self.graph.add_vertex(self.history[self.current_step].prev_vertex_2)

        self.current_step -= 1