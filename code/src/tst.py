import json
import time
from copy import deepcopy

import numpy as np
import pandas as pd

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

def jaro_metric(S1, S2):
    s1 = str(S1)
    s2 = str(S2)
    # Если одна из строк пустая, возвращаем 0
    if not s1 or not s2:
        return 0.0

    # Определение максимального расстояния для сравнения символов
    max_dist = max(len(s1), len(s2)) // 2 - 1

    # Списки для хранения индексов совпавших символов
    match_indices_s1 = [-1] * len(s1)
    match_indices_s2 = [-1] * len(s2)

    # Считаем количество совпадений
    matches = 0
    for i, char1 in enumerate(s1):
        start = max(0, i - max_dist)
        end = min(i + max_dist + 1, len(s2))
        for j in range(start, end):
            if s2[j] == char1 and match_indices_s2[j] == -1:
                matches += 1
                match_indices_s1[i] = j
                match_indices_s2[j] = i
                break

    # Рассчитываем количество транспозиций
    transpositions = sum(
        1 for k in range(matches) if match_indices_s1[k] != match_indices_s2[match_indices_s1[k]]
    )

    # Деление числа транспозиций пополам
    transpositions //= 2

    # Вычисляем итоговый коэффициент Джаро
    if matches == 0:
        return 0.0
    else:
        return (
                matches / len(s1) +
                matches / len(s2) +
                (matches - transpositions) / matches
        ) / 3.0

def extended_alphabet_index(char):
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz0123456789"
    return alphabet.find(char.lower()) + 1

def trans(s2):
    s1 = 'а' * len(s2)
    differences = ""

    for c1, c2 in zip(s1, s2):
        index1 = extended_alphabet_index(c1)
        index2 = extended_alphabet_index(c2)

        if index1 == 0 or index2 == 0:
            differences += "0"
            continue

        difference = abs(index1 - index2)

        if difference == 0:
            differences += "0"
            continue

        difference_base32 = format(difference, 'x')

        if difference < 32:
            differences += difference_base32
        else:
            # Новый набор символов для системы счисления Base64
            chars = "абвгдежзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz0123456789"
            base32_str = ''
            while difference:
                difference, rem = divmod(difference, len(chars))  # Изменено деление на длину нового набора символов
                base32_str = chars[rem] + base32_str
            differences += base32_str

    return differences

start_time = time.time()

df = pd.read_csv('ds_dirty_fin_202410041147.csv', index_col=None)
ddf = deepcopy(df)

# Получаем общее количество записей
total_records = len(df)

# Поиск первой строки и колонки с символом '@'
index, column_index = find_first_column_with_at(df)

numeric_columns = df.select_dtypes(include=np.number).columns

# Работа только с числовыми столбцами
numeric_df = df[numeric_columns]
#max_values = df.astype(str).map(len).max().max()
temp_df = numeric_df[1:]
max_values = max([len(str(x)) for x in temp_df.values.flatten() if x is not None])

# Процентное соотношение заполненности для каждой колонки
column_stats = {}
for column in df.columns[1:-3]:
    non_null_count = df[column].notna().sum()
    is_text = df[column].apply(lambda x: isinstance(x, str)).any()
    percentage_filled = round((non_null_count / total_records) * 100, 2)
    if percentage_filled < 0:#10
        df.drop(column, axis=1, inplace=True)
    else:
        if is_text and not df.columns.get_loc(column) == column_index:
            percentage_filled *= 0.8
        elif not is_text:
            non_null_values = df[column].dropna()
            if not non_null_values.empty:
                first_non_null_index = non_null_values.first_valid_index()
                first_non_null_len = len(str(non_null_values.loc[first_non_null_index]))
                percentage_filled *= np.interp(first_non_null_len, (1, max_values), (0.9, 1.1))
        '''if column != "JsonID" and column != 'CreationDate':
            column_stats[column] = f"{percentage_filled}"
        else: column_stats[column] = f"{0}"'''
        column_stats[column] = f"{percentage_filled}"

json_data = json.dumps(column_stats, indent=4)

with open('Y.json', 'w') as outfile:
    outfile.write(json_data)

columns_to_convert = df.columns[1:]

# Преобразуем указанные колонки в строки
df.loc[:, columns_to_convert] = df[columns_to_convert].astype(str)

for column in columns_to_convert:
    # Пропускаем пустые значения
    non_zero_indices = ~df[column].isna() & (df[column] != np.nan) & (df[column] != 0) & (df[column] != "0")
    subset = df.loc[non_zero_indices, column]

    # Находим максимальную длину строки в колонке среди ненулевых значений
    max_length_index = subset.str.len().argmax()
    longest_string = subset.iloc[max_length_index]

    df[column] = subset.apply(trans)
    df[column] = subset.apply(jaro_metric, args=(longest_string,))

sorted_columns = sorted(column_stats, key=lambda x: column_stats[x], reverse=True)

CC = sorted_columns[0]

index_groups = {}

for col in sorted_columns:
    df = df.sort_values(by=[*sorted_columns[:sorted_columns.index(col)], col], ascending=False)

for name, group in df.groupby(CC):
    index_groups[name] = group.index.tolist()

json_data = json.dumps(index_groups, indent=4)

print(len(index_groups))

# Запись данных в JSON-файл
with open('Clusters.json', 'w') as outfile:
    outfile.write(json_data)

indices = df['client_id']

df.to_csv('Jaro_Matrix.csv', index=True)

# Фильтруем строки df1, где значение в колонке 'A' совпадает с одним из индексов df2
filtered_df = ddf[ddf['client_id'].isin(indices)]

filtered_df.set_index('client_id', inplace=True)

filtered_df = filtered_df.loc[indices]

filtered_df['client_id'] = filtered_df.index

filtered_df.to_csv('test_with_full_fin_as_yadro.csv', index=True)

end_time = time.time()
elapsed_time = end_time - start_time

print(elapsed_time)