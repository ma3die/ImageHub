import time
from functools import wraps
from loguru import logger

import magic
def get_mime_type(file):
    """Функция для проверки типа фаула"""
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)
    file_type = mime_type.split('/')[0]
    return file_type

def retry(times=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info("Юзаем декоратор")
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