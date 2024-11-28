# Свойство объекта
# name - название свойства
# value - значение свойства
# trusted_coefficient - уровень доверия свойства
import random
import MergeWizard


class Property:
    def __init__(self, name = '', value = '', trusted_coefficient = 0.9):
        self.name = name
        self.value = value
        self.trusted_coefficient = trusted_coefficient


# Вершина графа
# properties - набор свойств
class Vertex:
    def __init__(self, name = 'default', properties = None, hyperedge_id = None):
        if properties is None:
            self.properties = set()
        else:
            self.properties = set(properties)
        if hyperedge_id is None:
            self.hyperedge_id = -1
        else:
            self.hyperedge_id = hyperedge_id
        self.name = name
        self.edges = set()

    def fill(self, properties: set):
        self.properties = set(properties)

    def fill_edges(self, edges):
        self.edges = edges

    def add_edge(self, edge):
        self.edges.add(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def add_property(self, property: Property):
        self.properties.add(property)

    def __str__(self):
        return (f'Vertex: {self.name}')


# Гиперребро
# vertices - множество вершин, ассоцииарованных с ребром
# agr_weight - агрегатный вес ребра
# mark - отметка, обозначающая что-нибудь (например, текущий статус гиперребра)
class Hyperedge:
    def __init__(self, name, vertices, agr_weight = 0, mark = 0):
        self.name = name
        self.vertices = vertices
        self.agr_weight = agr_weight
        self.mark = mark

    def fill(self, vertices):
        self.vertices = vertices

    def add_vertex(self, vertex: Vertex):
        self.vertices.append(vertex)

    def delete_vertex(self, vertex: Vertex):
        for vertex in list(self.vertices):
            if vertex.name == vertex.name:
                self.vertices.remove(vertex)
                break


# Ребро
# vertex1, vertex2 - пара вершин графа
# weight - вес ребра
# mark - отметка, обозначающая что-нибудь (например, отметка о слиянии/разлитии)
class Edge:
    def __init__(self, id = -1, vertex1 = None, vertex2 = None, weight = 0, mark = 0):
        self.id = id
        if vertex1 is None:
            self.vertex1 = Vertex()
        else:
            self.vertex1 = vertex1
        if vertex2 is None:
            self.vertex2 = Vertex()
        else:
            self.vertex2 = vertex2
        self.weight = weight
        self.mark = mark

    def __str__(self):
        return (f'Edge: {self.vertex1.name} - {self.vertex2.name}, {self.weight}')


# Основной класс комбинированного графа, включающего в себя как традиционный взвешенный граф, так и гиперграф
# vertices - общий для обоих подграфов набор вершин
# hyperedges - массив гиперребер гиперграфа
# edges - массив ребер традиционного графа
class CombinedGraph:
    def __init__(self):
        self.vertices = []
        self.hyperedges = []
        self.edges = []

    def get_state(self):
        return {
            'hyperedges': self.hyperedges,
            'vertices': self.vertices,
            'edges': self.edges
        }

    def fill_edges(self, edges):
        self.edges = []
        self.edges.extend(edges)
        for edge in edges:
            if edge.vertex1 in self.vertices:
                self.vertices[self.vertices.index(edge.vertex1)].edges.add(edge)
            if edge.vertex2 in self.vertices:
                self.vertices[self.vertices.index(edge.vertex2)].edges.add(edge)


    def fill_hyperedges(self, hyperedges):
        self.hyperedges = []
        self.hyperedges.extend(hyperedges)

    def fill_vertices(self, vertices):
        self.vertices = vertices

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def remove_vertex(self, vertex_name):
        for vertex in list(self.vertices):
            if vertex.name == vertex_name:
                self.vertices.remove(vertex)
                break

    def remove_vertex_from_hyperedge(self, vertex_name, hyperedge: Hyperedge):
        vertex_to_remove = None
        for vertex in hyperedge.vertices:
            if vertex.name == vertex_name:
                vertex_to_remove = vertex
                break
        if vertex_to_remove:
            hyperedge.delete_vertex(vertex_to_remove)

    def add_vertex_to_hyperedge(self, vertex: Vertex, hyperedge: Hyperedge):
        hyperedge.add_vertex(vertex)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, other_edge):
        for edge in list(self.edges):
            if ((edge.vertex1.name == other_edge.vertex1.name and edge.vertex2.name == other_edge.vertex2.name) or
                (edge.vertex1.name == other_edge.vertex2.name and edge.vertex2.name == other_edge.vertex1.name)):
                self.edges.remove(edge)
                break

    def add_hyperedge(self, hyperedge: Hyperedge):
        if all(vertex in self.vertices for vertex in hyperedge):
            self.hyperedges.append(hyperedge)
        else:
            print("Ошибка: Все вершины гиперребра должны существовать в гиперграфе.")

    def get_edges_connected_to_vertices(self, vertices):
        # Получаем все ребра, которые соединяют указанные вершины
        return [edge for edge in self.edges if (edge.vertex1 in vertices and edge.vertex2 in vertices)]

    def check_hyperedge(self, hyperedge: Hyperedge):
        # Получаем все уникальные вершины в гиперребре
        vertices = hyperedge.vertices

        # Получаем все ребра, соединяющие вершины гиперребра
        connected_edges = self.get_edges_connected_to_vertices(vertices)

        # Определяем максимальный вес среди этих ребер
        max_weight = max((edge.weight for edge in connected_edges), default=0)

        # Проверяем каждое ребро гиперребра на аномалии
        for vertex in list(vertices):  # Преобразовываем в список для безопасного удаления
            anomaly_found = False

            # Проверяем вес гиперребра (которое нам нужно будет вычислить или предоставить)
            # Здесь предполагается, что у гиперребра есть определенный вес, можно добавить атрибут weight
            hyperedge_weight = hyperedge.agr_weight  # Предполагаем, что у гиперребра есть вес

            if (max_weight - hyperedge_weight) > N:
                anomaly_found = True

            if anomaly_found:
                hyperedge.delete_vertex(vertex)  # Удаляем вершину из гиперребра

    def calculate_all_hyperedge_weights(self):
        # Вычисляем агрегатные веса для всех гиперребер в графе
        for hyperedge in self.hyperedges:
            connected_edges = self.get_edges_connected_to_vertices(hyperedge.vertices)

            if connected_edges:
                total_weight = sum(edge.weight for edge in connected_edges)
                hyperedge.agr_weight = total_weight / len(connected_edges)
            else:
                hyperedge.agr_weight = 0  # Если нет соединяющих ребер, вес равен 0

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges

    def get_hyperedges(self):
        return self.hyperedges

    def __str__(self):
        output = "Вершины графа:\n"
        for v in self.get_vertices():
            output += str(v) + "\n"

        output += "\nРебра графа:\n"
        for e in self.get_edges():
            output += str(e) + "\n"

        output += "\nГиперребра графа:\n"
        for he in self.get_hyperedges():
            output += "["
            for v in he.vertices:
                output += str(v.name) + " "
            output += "]\n"

        return output.strip() + "\n----------\n"

    def get_subgraph_by_hyperedges(self):
        result = []
        for he in self.hyperedges:
            result.append(Vertex(he.name, random.choice(he.vertices).properties))

        return result

    def collapse_hyperedge(self, hyperedge):
        vertex1 = hyperedge.vertices[0]
        for vertex in hyperedge.vertices[1:]:
            vertex1 = MergeWizard.MergeWizard.merge_pair_vertices(vertex1, vertex, self).vertex