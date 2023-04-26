def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):  # type : ignore[no-untyped-def]
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
