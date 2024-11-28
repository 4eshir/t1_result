import plotly.graph_objects as go
import networkx as nx
import numpy as np
from scipy.spatial import ConvexHull
import random

class GraphVisual:

    # Адаптер наших вершин к вершинам Plotly
    @staticmethod
    def vertex_adapter(vertices):
        result = []
        for vertex in vertices:
            result.append(vertex.name)

        return result

    # Адаптер наших ребер к ребрам Plotly
    @staticmethod
    def edge_adapter(edges):
        result = []
        for edge in edges:
            result.append((edge.vertex1.name, edge.vertex2.name, edge.weight))

        return result

    # Адаптер наших гиперребер к прокси-гиперребрам Plotly
    @staticmethod
    def hyperedge_adapter(hyperedges):
        result = []
        for edge in hyperedges:
            edgeVertices = []
            for vertex in edge.vertices:
                edgeVertices.append(vertex.name)
            result.append(edgeVertices)

        return result

    # Основная функция отрисовки графа
    @staticmethod
    def graph_output(vertices, edges, hyperedges):
        # Создаем граф
        G = nx.Graph()

        # Добавляем узлы
        G.add_nodes_from(vertices)

        # Добавляем рёбра с весами
        for edge in edges:
            G.add_edge(edge[0], edge[1], weight=edge[2])

        # Получаем позиции узлов для визуализации
        pos = nx.spring_layout(G)

        # Создаем фигуру
        fig = go.Figure()

        # Извлекаем координаты для рёбер
        x_edges = []
        y_edges = []
        for edge in G.edges(data=True):
            x_edges.append(pos[edge[0]][0])
            x_edges.append(pos[edge[1]][0])
            x_edges.append(None)  # Разрывы между рёбрами
            y_edges.append(pos[edge[0]][1])
            y_edges.append(pos[edge[1]][1])
            y_edges.append(None)  # Разрывы между рёбрами

        # Добавляем области (гиперребра)
        for edge in hyperedges:
            points = np.array([pos[v] for v in edge])

            # Нахождение выпуклой оболочки
            if len(points) > 2:  # Для выпуклой оболочки нужно минимум 3 точки
                hull = ConvexHull(points)
                x0 = points[hull.vertices, 0]
                y0 = points[hull.vertices, 1]

                # Замыкание обхода
                x0 = np.append(x0, x0[0])
                y0 = np.append(y0, y0[0])

                # Добавляем гиперребро
                fig.add_trace(go.Scatter(
                    x=x0,
                    y=y0,
                    mode='lines+text',
                    fill='toself',
                    name='Гиперребро',
                    line=dict(color='lightblue', width=2),
                    fillcolor=f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.5)',
                    hoverinfo='text',
                    hovertext='Гиперребро'  # Текст для отображения при наведении
                ))

        # Извлекаем координаты узлов
        x_nodes = [pos[node][0] for node in G.nodes()]
        y_nodes = [pos[node][1] for node in G.nodes()]

        # Добавляем рёбра
        fig.add_trace(go.Scatter(
            x=x_edges,
            y=y_edges,
            mode='lines',
            line=dict(width=2, color='rgba(90, 34, 139, 0.5)'),
            hoverinfo='none'
        ))

        # Добавляем узлы
        fig.add_trace(go.Scatter(
            x=x_nodes,
            y=y_nodes,
            mode='markers',
            marker=dict(size=35, color='purple', line=dict(color='rgba(255, 255, 255, 1)', width=6)),
            hoverinfo='none'
        ))

        # Добавляем черные подложки под текст меток узлов
        for i, node in enumerate(G.nodes()):
            fig.add_trace(go.Scatter(
                x=[pos[node][0]],  # Позиция узла
                y=[pos[node][1]],  # Чуть ниже узла
                mode='markers+text',
                marker=dict(size=25, color='black', opacity=0),  # Черная подложка
                text=[str(node)],
                textposition="middle center",
                textfont=dict(color='white', size=16, family='Trebuchet MS', weight='bold')
            ))

        # Настраиваем оси и фон
        fig.update_layout(
            title='Визуализация гиперграфа с гиперребрами',
            title_font=dict(size=20, color='darkblue'),
            plot_bgcolor='rgba(255, 255, 255, 0.5)',
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )

        # Показываем граф
        fig.show()