import time


def timeit(is_measured: bool = False):
    """Time record decorator

    Args:
        is_measured (bool, optional): Add a attribute to the class which can be measured. Defaults to False.
    """

    def decorator(func):
        def wrapper(*args, **kwargs) -> float:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            if is_measured:
                setattr(wrapper, "_execution_time", execution_time)
            return result

        return wrapper

    return decorator
