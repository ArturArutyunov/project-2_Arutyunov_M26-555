SUPPORTED_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """Создаёт таблицу в метаданных"""

    if table_name in metadata:
        print(f"Ошибка: таблица '{table_name!r}' уже существует")
        return None

    if not table_name:
        print(f"Некорректное название таблицы: {table_name!r}. Не может быть пустым")
        return None

    table_columns = []
    user_has_id = False

    for name, col_type in columns:
        if not name:
            print(f"Ошибка: некорректное значение: {name!r}")
            return None
        if col_type not in SUPPORTED_TYPES:
            print(f"Ошибка: неподдерживаемый тип {col_type!r} у поля {name!r}")
            return None
        if name == "id":
            if col_type != "int":
                print(f"Ошибка: некорректный тип id: {col_type!r}. Замените на 'int'")
                return None
            user_has_id = True
        if any(existing_name == name for existing_name, _ in table_columns):
            print(f"Ошибка: поле {name!r} уже существует")
            return None
        table_columns.append((name, col_type))

    if not user_has_id:
        table_columns.insert(0, ("id", "int"))

    metadata[table_name] = [{"name": n, "type": t} for n, t in table_columns]
    print(f"Таблица '{table_name!r}' создана. Колонки: {table_columns}")
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f"Ошибка: таблица {table_name!r} не найдена.")
        return None

    del metadata[table_name]
    print(f"Таблица {table_name!r} удалена.")
    return metadata


def list_tables(metadata):
    """Выводит список всех таблиц"""
    if not metadata:
        print("Таблиц пока нет")
        return
    print("Таблицы:")
    for table_name, columns in metadata.items():
        cols = ", ".join(f"{c['name']}:{c['type']}" for c in columns)
        print(f"  {table_name} ({cols})")