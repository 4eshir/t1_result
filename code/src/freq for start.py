import numpy as np
import pandas as pd
import json

df = pd.read_csv('ds_dirty_fin_202410041147.csv', index_col=None)

# Получаем общее количество записей
total_records = len(df)

# Функция для поиска первой строки с включением символа '@'
def find_first_column_with_at(df):
    found = False
    index = None
    column_index = None

    for i, row in df.iterrows():
        for j, cell in enumerate(row):
            if isinstance(cell, str) and '@' in cell:
                found = True
                index = i
                column_index = j
                break
        if found:
            break

    return index, column_index

# Поиск первой строки и колонки с символом '@'
index, column_index = find_first_column_with_at(df)

numeric_columns = df.select_dtypes(include=np.number).columns

# Работа только с числовыми столбцами
numeric_df = df[numeric_columns]
temp_df = numeric_df[3:]
max_values = max([len(str(x)) for x in temp_df.values.flatten() if x is not None])

# Процентное соотношение заполненности для каждой колонки
column_stats = {}
for column in df.columns[3:]:
    non_null_count = df[column].notna().sum()
    is_text = df[column].apply(lambda x: isinstance(x, str)).any()
    percentage_filled = round((non_null_count / total_records) * 100, 2)
    if is_text and not df.columns.get_loc(column) == column_index:
        percentage_filled *= 0.8
    elif not is_text:
        non_null_values = df[column].dropna()
        if not non_null_values.empty:
            first_non_null_index = non_null_values.first_valid_index()
            first_non_null_len = len(str(non_null_values.loc[first_non_null_index]))
            percentage_filled *= np.interp(first_non_null_len, (1, max_values), (0.9, 1.1))
    if column != "JsonID" and column != 'CreationDate':
        column_stats[column] = f"{percentage_filled}"
    else: column_stats[column] = f"{0}"

json_data = json.dumps(column_stats, indent=4)

with open('freq.json', 'w') as outfile:
    outfile.write(json_data)

non_null_counts = df.notna().sum(axis=1)

# Считаем отношение количества ненулевых значений к общему числу столбцов
fullness_ratio = non_null_counts / len(df.columns)

df.set_index('client_id', inplace=True)

# Создаем новый датафрейм с индексами и значением полноты
index_and_fullness_df = pd.DataFrame({
    'Индекс': df.index,
    'Полнота': fullness_ratio
})

# Преобразуем новый датафрейм в JSON
json_data = index_and_fullness_df.to_json(force_ascii=False, orient='records')

# Сохраняем результат в файл
with open('comp.json', 'w', encoding='utf-8') as f:
    f.write(json_data)