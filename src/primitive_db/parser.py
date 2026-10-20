def parse_condition(condition_str):
    """
    Парсит в словарь строку вида: 'age = 30' -> {'age': 30}
    """
    if "=" not in condition_str:
        raise ValueError(f"Некорректное условие: {condition_str}")

    key, value_str = condition_str.split("=", 1)
    key = key.strip().lower()
    value_str = value_str.strip()

    if not key or not value_str:
        raise ValueError(f"Некорректное условие: {condition_str}")

    if len(value_str) >= 2 and value_str[0] == value_str[-1] and value_str[0] in ("'", '"'):
        value = value_str[1:-1]
    elif value_str.lower() == "true":
        value = True
    elif value_str.lower() == "false":
        value = False
    else:
        try:
            value = int(value_str)
        except ValueError:
            raise ValueError(f"Строковые значения должны быть в кавычках: {value_str}")

    return {key: value}