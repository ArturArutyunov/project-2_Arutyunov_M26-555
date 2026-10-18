import shlex
import os

import prompt

from primitive_db.core import create_table, drop_table, insert, list_tables
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_FILE_NAME = os.path.join("data", "db_meta.json")

def show_help():
    """Выводит сообщение с инструкцией"""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
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
            parts = shlex.split(command)
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
            case _:
                print(f"Функции {cmd} нет. Попробуйте снова.")