from primitive_db.decorators import confirm_action, handle_db_errors, log_time

SUPPORTED_TYPES = {"int", "str", "bool"}

def normalize_clause(clause):
    """Приводит ключи к нижнему регистру"""
    return {k.lower(): v for k, v in clause.items()}

def matches(row, where_clause):
    """Проверяет что значения из записи совпадают со всеми условиями"""
    return all(row.get(k) == v for k, v in where_clause.items())


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу в метаданных"""

    table_name = table_name.lower()

    if table_name in metadata:
        raise ValueError(f"таблица {table_name!r} уже существует")

    if not table_name:
        raise ValueError(
            f"некорректное название таблицы: {table_name!r}. "
            "Не может быть пустым"
        )

    table_columns = []
    user_has_id = False

    for name, col_type in columns:
        name = name.lower()
        col_type = col_type.lower()

        if not name:
            raise ValueError(f"пустое имя столбца: {name!r}")
        if col_type not in SUPPORTED_TYPES:
            raise ValueError(f"неподдерживаемый тип {col_type!r} у поля {name!r}")
        if name == "id":
            if col_type != "int":
                raise ValueError(f"id должен быть int: {name}:{col_type}")
            user_has_id = True
        if any(existing_name == name for existing_name, _ in table_columns):
            raise ValueError(f"поле {name!r} уже существует")
        table_columns.append((name, col_type))

    if not user_has_id:
        table_columns.insert(0, ("id", "int"))

    table_columns.sort(key=lambda c: c[0] != "id")

    metadata[table_name] = [{"name": n, "type": t} for n, t in table_columns]
    print(f"Таблица {table_name!r} создана. Колонки: {table_columns}")
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу"""

    table_name = table_name.lower()
    if table_name not in metadata:
        raise KeyError(table_name)

    del metadata[table_name]
    print(f"Таблица {table_name!r} удалена.")
    return metadata


@handle_db_errors
def list_tables(metadata):
    """Выводит список всех таблиц"""

    if not metadata:
        print("Таблиц пока нет")
        return
    print("Таблицы:")
    for table_name, columns in metadata.items():
        cols = ", ".join(f"{c['name']}:{c['type']}" for c in columns)
        print(f"  {table_name} ({cols})")


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Вставляет запись в таблицу"""

    table_name = table_name.lower()

    if table_name not in metadata:
        raise KeyError(table_name)

    schema = metadata[table_name]
    data_columns = schema

    if len(values) != len(data_columns) - 1:
        raise ValueError(
            f"ожидалось {len(data_columns) - 1} значений, "
            f"получено {len(values)}"
        )

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
            raise ValueError(
                f"некорректное значение {value!r} "
                f"для столбца {col_name!r} ({col_type})"
            )

    table_data.append(record)
    print(f"Запись добавлена: {record}")
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает записи из таблицы согласно условию"""

    if where_clause:
        where_clause = normalize_clause(where_clause)
        return [row for row in table_data if matches(row, where_clause)]
    return table_data


@handle_db_errors
@log_time
def update(table_data, set_clause, where_clause):
    """Обновляет записи в таблице согласно условию"""

    set_clause = normalize_clause(set_clause)
    where_clause = normalize_clause(where_clause)

    updated = 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            row.update(set_clause)
            updated += 1
    print(f"Обновлено записей: {updated}")
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Удаляет записи из таблицы согласно условию"""

    where_clause = normalize_clause(where_clause)

    initial_count = len(table_data)
    result = [
        row for row in table_data
        if not all(row.get(k) == v for k, v in where_clause.items())
    ]
    print(f"Удалено записей: {initial_count - len(result)}")
    return result


@handle_db_errors
def info(metadata, table_name, table_data):
    """Возвращает информацию о таблице"""
    
    table_name = table_name.lower()

    if table_name not in metadata:
        raise KeyError(table_name)

    schema = metadata[table_name]
    cols = ", ".join(f"{c['name']}:{c['type']}" for c in schema)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols}")
    print(f"Количество записей: {len(table_data)}")