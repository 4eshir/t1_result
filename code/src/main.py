import time
import pandas as pd
from LoadAdapter import *
import json

from MultiGraph import *
from CleanData import *


def new_test():
    vertex_list = parse_csv_to_vertices('first100.csv')
    vertex_list = parse_json_to_vertices(vertex_list, 'comp.json')

    for vertex in vertex_list:
        print(f'ID: {vertex.id}, Completeness Coefficient: {vertex.completeness_coef}')

    return

    input_file_path = input("Введите путь к исходному файлу (например, 'in.csv'): ")
    output_file_path = input("Введите путь к итоговому файлу (например, 'out.csv'): ")

    start_time = time.time()
    vertices = parse_csv_to_vertices(input_file_path)
    end_time = time.time()
    print(f'Время парсинга файла: {end_time - start_time}с.')

    start_time = time.time()
    graph = MultiGraph(vertices)
    edges = LoadWizard.create_edges_and_hyperedges(graph, e_count, he_count)
    end_time = time.time()
    print(
        f'Время создания {v_count} вершин, генерации {edges} ребер и {round(v_count / he_count)} гиперребер: {end_time - start_time}с.')

    count = 800000
    input("Нажмите Enter, чтобы начать тестовое слияние")
    start_time = time.time()
    #graph.fake_merges(count)
    graph.collapse_hyperedges()
    end_time = time.time()
    print(f'Время тестового мерджа {count} вершин: {end_time - start_time}с.')



def test_similar():
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    # Читаем CSV файл
    df = pd.read_csv('dataset.csv')  # Замените 'your_file.csv' на имя вашего файла

    # Фильтруем строки, где contact_email не соответствует формату
    invalid_emails = df[~df['contact_email'].str.match(email_pattern, na=False)]
    pd.set_option('display.max_rows', None)
    # Выводим строки с неверными адресами электронной почты
    print(invalid_emails[['contact_email']])

def parse_json_to_vertices(vertices, json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Обновление completeness_coef для каждой вершины
    for vertex in vertices:
        if vertex.id in data:
            completeness = data[vertex.id].get('Полнота', None)
            if completeness is not None:
                try:
                    # Приведение к float, если значение существует
                    vertex.completeness_coef = float(completeness)
                except ValueError:
                    print(f'Warning: Ignored invalid completeness value for vertex {vertex.id}: {completeness}')

    return vertices

def parse_csv_to_vertices(file_path):
    # Читаем CSV файл с помощью pandas
    df = pd.read_csv(file_path)

    # Создаем список для хранения объектов Vertex
    vertices = []

    # Проходим по каждой строке DataFrame
    for index, row in df.iterrows():
        client_id = row['client_id']  # Предполагаем, что у вас есть столбец client_id
        properties_set = set()

        # Обходим все остальные столбцы, которые будут использоваться как свойства
        for col in df.columns:
            if col != 'client_id':  # Игнорируем столбец client_id
                property_name = col
                property_value = row[col]
                properties_set.add(Property(name=property_name, value=property_value))

        # Создаем объект Vertex и добавляем его в список
        vertex = Vertex(id=client_id, properties=properties_set)
        vertices.append(vertex)

    return vertices

if __name__ == '__main__':
    new_test()
    '''
    # Чтение данных из CSV файла
    df = pd.read_csv('dataset.csv')

    # Установка опций для отображения
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)

    # Очистка данных
    start_time = time.time()
    df = CleanData.clean_df(df)
    end_time = time.time()

    # Вывод
    print(f'Время выполнения: {end_time - start_time} с.')
    print(df[df['addr_str'].notna()][['addr_str', 'addr_str_code']])
    df.to_csv('output.csv')
    '''