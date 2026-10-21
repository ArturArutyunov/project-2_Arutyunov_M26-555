import shlex
import os

import prompt

from primitive_db.core import (
    create_table,
    drop_table,
    list_tables,
    insert,
    select,
    update,
    delete,
    info
)
from primitive_db.parser import parse_condition
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data
)

DB_FILE_NAME = os.path.join("data", "db_meta.json")

def show_help():
    """Выводит сообщение с инструкцией"""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nФункции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию") 
    print("<command> select from <имя_таблицы> - прочитать все записи") 
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись") 
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись") 
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 



def run():
    """Основная функция, запускающая интерактивный режим"""
    show_help()

    while True:
        metadata = load_metadata(DB_FILE_NAME)
        
        command = prompt.string("Введите команду: ").strip()
        if not command:
            continue

        try:
            parts = shlex.split(command, posix=False)
        except ValueError:
            print(f"Некорректное значение: {command!r}. Попробуйте снова.")
            continue

        if not parts:
            continue

        cmd, *args = parts
        cmd = cmd.lower()

        match cmd:
            case "exit":
                break

            case "help":
                show_help()

            case "create_table":
                if len(args) < 2:
                    print(
                        f"Некорректное значение: {command!r}. "
                        "Нужны название и колонки."
                    )
                    continue

                table_name = args[0]
                columns = []
                for arg in args[1:]:
                    if ":" not in arg:
                        print(f"Некорректное значение: {arg!r}. Попробуйте снова.")
                        break
                    name, col_type = arg.split(":", 1)
                    columns.append((name, col_type))
                else:
                    result = create_table(metadata, table_name, columns)
                    if result is not None:
                        save_metadata(DB_FILE_NAME, result)

            case "drop_table":
                if len(args) != 1:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                result = drop_table(metadata, args[0])
                if result is not None:
                    save_metadata(DB_FILE_NAME, result)

            case "list_tables":
                list_tables(metadata)

            case "info":
                if len(args) != 1:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                table_name = args[0].lower()
                table_data = load_table_data(table_name)
                info(metadata, table_name, table_data)

            case "insert":
                if len(args) < 4:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                if args[0].lower() != "into" or args[2].lower() != "values":
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                table_name = args[1].lower()
                raw_values = " ".join(args[3:]).strip()

                if not (raw_values.startswith("(") and raw_values.endswith(")")):
                        print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                        continue

                raw_values = raw_values[1:-1].strip()
                values = [v.strip() for v in raw_values.split(",")]

                table_data = load_table_data(table_name)
                result = insert(metadata, table_name, values, table_data)
                if result is not None:
                    save_table_data(table_name, result)

            case "select":
                if len(args) < 2 or args[0].lower() != "from":
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                table_name = args[1].lower()
                rest = args[2:]

                if not rest:
                    where_clause = None
                else:
                    if rest[0].lower() != "where":
                        print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                        continue

                    where_text = " ".join(rest[1:]).strip()
                    if not where_text:
                        print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                        continue

                    try:
                        where_clause = parse_condition(where_text)
                    except ValueError as e:
                        print(f"{e}. Попробуйте снова.")
                        continue
                table_data = load_table_data(table_name)
                select(table_data, where_clause)

            case "update":
                if len(args) < 9:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                table_name = args[0].lower()
                rest = args[1:]

                lower_rest = [a.lower() for a in rest]
                if "set" not in lower_rest or "where" not in lower_rest:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                set_idx = lower_rest.index("set")
                where_idx = lower_rest.index("where")

                if set_idx != 0:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                if where_idx - set_idx - 1 != 3:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                if len(rest) - where_idx - 1 != 3:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                set_text = " ".join(rest[set_idx + 1:where_idx]).strip()
                where_text = " ".join(rest[where_idx + 1:]).strip()

                try:
                    set_clause = parse_condition(set_text)
                    where_clause = parse_condition(where_text)
                except ValueError as e:
                    print(f"{e}. Попробуйте снова.")
                    continue

                table_data = load_table_data(table_name)
                result = update(table_data, set_clause, where_clause)
                save_table_data(table_name, result)

            case "delete":
                if len(args) != 6:
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                if args[0].lower() != "from" or args[2].lower() != "where":
                    print(f"Некорректное значение: {command!r}. Попробуйте снова.")
                    continue

                table_name = args[1].lower()
                where_text = " ".join(args[3:]).strip()

                try:
                    where_clause = parse_condition(where_text)
                except ValueError as e:
                    print(f"{e}. Попробуйте снова.")
                    continue

                table_data = load_table_data(table_name)
                result = delete(table_data, where_clause)
                save_table_data(table_name, result)

            case _:
                print(f"Функции {cmd} нет. Попробуйте снова.")