import time
from functools import wraps

def retry(times=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == times:
                        raise
                    time.sleep(delay)
                    print(f"Retrying {func.__name__} due to {e}. Attempt {attempt}/{times}")
        return wrapper
    return decorator