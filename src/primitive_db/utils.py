import json
import os


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
    """Путь к файлу данных таблицы: data/<table_name>.json"""

    return os.path.join("data", f"{table_name}.json")


def load_table_data(table_name):
    """Загружает данные таблицы"""

    data = load_metadata(table_path(table_name))
    return data if isinstance(data, list) else []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы"""

    save_metadata(table_path(table_name), data)