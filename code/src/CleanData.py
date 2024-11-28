import pandas as pd
from datetime import datetime
import re
import numpy as np

class CleanData:
    @staticmethod
    def russian_alphabet_index(char):
        alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
        return alphabet.find(char.lower()) + 1

    @staticmethod
    def similar(s2):
        s1 = 'а' * 100
        s1 = s1[:len(s2)]
        differences = ""
        for c1, c2 in zip(s1, s2):
            index1 = CleanData.russian_alphabet_index(c1)
            index2 = CleanData.russian_alphabet_index(c2)

            if index1 == 0 or index2 == 0:
                differences += "0"
                continue

            difference = abs(index1 - index2)
            difference_base32 = format(difference, 'x')

            if difference < 32:
                differences += difference_base32
            else:
                chars = "0123456789abcdefghijklmnopqrstuvwxyz"
                base32_str = ''
                while difference:
                    difference, rem = divmod(difference, 32)
                    base32_str = chars[rem] + base32_str
                differences += base32_str

        return differences

    @staticmethod
    def clean_df(df):
        df = df.head(1000).copy()
        # Предварительно стандартизируем ФИО и создаем код 'fio'
        df[['client_fio_full', 'client_fio_full_code']] = df.apply(
            lambda row: (
                CleanData.standardize_fio(row),
                CleanData.similar(row['client_fio_full']) if isinstance(row['client_fio_full'], str) else ''
            ),
            axis=1,
            result_type='expand'
        )

        # Чекаем дату рождения на формат
        df['client_bday_code'] = CleanData.clean_date(df['client_bday'])

        # Обрезаем дробную часть (у снилса и инн ага)
        df['client_snils'] = df['client_snils'].astype(str).str[:-2]
        df['client_inn'] = df['client_inn'].astype(str).str[:-2]

        # Чекаем валидность снилс и инн
        df['client_snils_code'] = df['client_snils'].apply(
            lambda x: 1 if CleanData.is_valid_snils(x) else (0 if pd.notna(x) else -1)
        )
        df['client_inn_code'] = df['client_inn'].apply(
            lambda x: 1 if CleanData.is_valid_inn(x) else (0 if pd.notna(x) else -1)
        )

        # Простая проверка регуляркой
        df['contact_email_code'] = df['contact_email'].apply(CleanData.assign_email_code)

        # ПЕРЕЗАПИСЫВАЕМ в в стандартном формате
        df['contact_phone'] = df['contact_phone'].apply(CleanData.standardize_phone)

        # Проверяем, соответствует ли строка адреса ее сборной версии из других столбцов.
        # ожно будет перезаписать наиболее полным вариантом
        df['addr_str_code'] = df.apply(CleanData.compare_addresses, axis=1)

        new_columns = [
            'client_id',
            'client_fio_full',
            'client_fio_full_code',
            'client_bday_code',
            'client_snils_code',
            'client_inn_code',
            'contact_email_code',
            'contact_phone',
            'addr_str_code'
        ]

        df = df[new_columns]

        return df

    @staticmethod
    def build_address_parts(row):
        return [
            str(row['addr_region']) if pd.notna(row['addr_region']) else '',
            str(row['addr_zip']) if pd.notna(row['addr_zip']) else '',
            str(row['addr_country']) if pd.notna(row['addr_country']) else '',
            str(row['addr_body']) if pd.notna(row['addr_body']) else '',
            str(row['addr_area']) if pd.notna(row['addr_area']) else '',
            str(row['addr_loc']) if pd.notna(row['addr_loc']) else '',
            str(row['addr_reg_dt']) if pd.notna(row['addr_reg_dt']) else '',
            str(row['addr_city']) if pd.notna(row['addr_city']) else '',
            str(row['addr_street']) if pd.notna(row['addr_street']) else '',
            str(row['addr_house']) if pd.notna(row['addr_house']) else '',
            str(row['addr_flat']) if pd.notna(row['addr_flat']) else ''
        ]

    @staticmethod
    def compare_addresses(row):
        # Собираем адресные части
        constructed_parts = CleanData.build_address_parts(row)
        constructed_address = ', '.join(part for part in constructed_parts if part)

        # Проверяем, что addr_str - это строка
        addr_str = row['addr_str'] if isinstance(row['addr_str'], str) else ''

        # Разделяем адрес как строки для сравнения
        constructed_parts_set = {part.strip() for part in constructed_address.split(',')}
        addr_parts_set = {part.strip() for part in addr_str.split(',')}

        # Проверяем, все ли составные части constructed_addr содержатся в addr_str
        return constructed_parts_set.issubset(addr_parts_set)

    @staticmethod
    def standardize_phone(phone):
        # Удаляем все символы, кроме цифр
        cleaned_phone = ''.join(filter(str.isdigit, phone))

        # Проверяем длину и стандартизируем
        if len(cleaned_phone) == 10:
            return '8' + cleaned_phone  # Добавляем 8, если 10 цифр
        elif len(cleaned_phone) == 11:
            if cleaned_phone.startswith('7'):
                return '8' + cleaned_phone[1:]  # Заменяем 7 на 8
            return cleaned_phone  # Возвращаем как есть, если первая цифра не 7
        else:
            return np.nan  # Если длина не подходит, можно вернуть NaN

    @staticmethod
    def assign_email_code(email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if pd.isna(email):
            return 0  # Если значение NaN, возвращаем 0
        elif re.match(email_regex, email):
            return 1  # Совпадение с регуляркой, возвращаем 1
        else:
            return CleanData.similar(email)

    @staticmethod
    def is_valid_inn(inn):
        if not isinstance(inn, str) or not inn.isdigit():
            return False
        return len(inn) in [10, 12]

    @staticmethod
    def is_valid_snils(snils):
        snils = snils.replace(' ', '').replace('-', '')
        if len(snils) != 11 or not snils.isdigit():
            return False
        return True

    @staticmethod
    def clean_date(birth_dates):
        current_year = datetime.now().year
        standardized_codes = []

        for date_str in birth_dates:
            try:
                # Попытка преобразовать строку в дату
                birth_date = pd.to_datetime(date_str)
                age = current_year - birth_date.year

                if age > 130:
                    # Подозрительная дата (человек более 130 лет)
                    standardized_codes.append(0)
                else:
                    # Реалистичная дата
                    standardized_codes.append(1)
            except ValueError:
                # Формат не соответствует дате
                standardized_codes.append(-1)

        return standardized_codes

    @staticmethod
    def standardize_fio(row):
        # Если все три поля заполнены, создаем FIO
        if pd.notnull(row['client_first_name']) and pd.notnull(row['client_middle_name']) and pd.notnull(
                row['client_last_name']):
            # Генерируем полное ФИО
            row['client_fio_full'] = f"{row['client_first_name']} {row['client_middle_name']} {row['client_last_name']}"
        # Если полное ФИО заполнено и какое-то поле из ФИО отсутствует
        elif pd.notnull(row.get('client_fio_full')):  # Используем .get для безопасного доступа
            # Разделяем полное ФИО на части
            fio_parts = row['client_fio_full'].split()
            if len(fio_parts) >= 3:
                row['client_first_name'] = fio_parts[0]
                row['client_middle_name'] = fio_parts[1]
                row['client_last_name'] = fio_parts[2]
            elif len(fio_parts) == 2:  # Если только 2 части, например, имя и фамилия
                row['client_first_name'] = fio_parts[0]
                row['client_last_name'] = fio_parts[1]

        # Возвращаем обновленную строку
        return row