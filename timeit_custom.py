from functools import wraps
from time import sleep, time

DEBUG_ROUTE = sys.stderr


def timeit(func):
    """
    :param func: Decorated function
    :return: wrapped function
    A decorator  for exec-timing service components
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        print(
            f"{func.__name__} executed in {end - start:.4f} seconds",
            file=DEBUG_ROUTE
        )
        return result
    return wrapper
