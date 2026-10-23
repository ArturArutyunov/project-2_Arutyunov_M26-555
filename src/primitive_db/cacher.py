def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result