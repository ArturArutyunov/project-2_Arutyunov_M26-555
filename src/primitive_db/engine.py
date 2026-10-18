import prompt


def show_help():
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

def welcome():
    print("***База данных***")
    show_help()

    while True:
        command = prompt.string("Введите команду: ").strip().lower()

        if command == "exit":
            break
        elif command == "help":
            show_help()