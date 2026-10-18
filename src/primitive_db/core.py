SUPPORTED_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """Создаёт таблицу в метаданных"""

    table_name = table_name.lower()

    if table_name in metadata:
        print(f"Ошибка: таблица {table_name!r} уже существует")
        return None

    if not table_name:
        print(f"Некорректное название таблицы: {table_name!r}. Не может быть пустым")
        return None

    table_columns = []
    user_has_id = False

    for name, col_type in columns:
        name = name.lower()
        col_type = col_type.lower()

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

    table_columns.sort(key=lambda c: c[0] != "id")

    metadata[table_name] = [{"name": n, "type": t} for n, t in table_columns]
    print(f"Таблица {table_name!r} создана. Колонки: {table_columns}")
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу"""

    table_name = table_name.lower()
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


def insert(metadata, table_name, values, table_data):
    """Вставляет запись в таблицу"""

    table_name = table_name.lower()

    if table_name not in metadata:
        print(f"Ошибка: таблица {table_name!r} не найдена.")
        return None

    schema = metadata[table_name]
    data_columns = schema

    if len(values) != len(data_columns) - 1:
        print(
            f"Ошибка: ожидалось {len(data_columns) - 1} значений, "
            f"получено {len(values)}."
        )
        return None

    new_id = max((row.get("id", 0) for row in table_data), default=0) + 1
    values = [str(new_id)] + list(values)

    record = {}
    for col, value in zip(data_columns, values):
        col_name, col_type = col["name"], col["type"]
        try:
            if col_type == "int":
                record[col_name] = int(value)
            elif col_type == "bool":
                low_bool = value.lower()
                if low_bool not in ("true", "false"):
                    raise ValueError
                record[col_name] = low_bool == "true"
            else:
                record[col_name] = value
        except (ValueError, AttributeError):
            print(
                f"Ошибка: некорректное значение: {value!r} для столбца "
                f"{col_name!r} ({col_type})."
            )
            return None

    table_data.append(record)
    print(f"Запись добавлена: {record}")
    return table_data