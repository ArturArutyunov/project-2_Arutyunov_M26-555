import json
import os

from prettytable import PrettyTable


def load_metadata(filepath):
    """Загружает данные из JSON-файла."""

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл"""

    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def table_path(table_name):
    """Возвращает путь к файлу данных таблицы: data/<table_name>.json"""

    return os.path.join("data", f"{table_name}.json")


def load_table_data(table_name):
    """Загружает данные таблицы"""

    data = load_metadata(table_path(table_name))
    return data if isinstance(data, list) else []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы"""

    save_metadata(table_path(table_name), data)


def join_conditions(condition_strings):
    """
    Склеивает тройки вида ['age', '=', '30', ... ,]
    в строки для парсинга ['age = 30', ... ,].
    """
    print(condition_strings)
    conditions = []
    current = []
    for str in condition_strings:
        current.append(str)
        if len(current) == 3:
            conditions.append(" ".join(current))
            current = []
    if current:
        raise ValueError(f"Некорректное условие: {' '.join(current)}")
    return conditions

def unquote(token):
    """Удаляет кавычки по краям строки"""

    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token

def print_table(result):
    """Выводит таблицу с результатами выборки"""

    if not result:
        print("Нет данных для отображения.")
        return

    table = PrettyTable()
    table.field_names = list(result[0].keys())
    for row in result:
        table.add_row([row.get(field) for field in table.field_names])
    print(table)