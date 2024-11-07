import os
from pathlib import Path
from typing import Optional

from celery import shared_task
from PIL import Image as PILImage, UnidentifiedImageError
from django.conf import settings
from loguru import logger

from .models import Image

SIZES = [(100, 100), (500, 500)]


def save_resized_image(
        original_image: PILImage, size: tuple[int, int], name: str, base_dir: Path
) -> Optional[tuple[Path, tuple[int, int], int]]:
    """Сохраняет изображение заданного размера и возвращает информацию о нем."""
    try:
        resized_img = original_image.resize(size).convert("L")
        resized_path = base_dir / f"{name}_{size[0]}x{size[1]}.jpg"
        resized_img.save(resized_path, format="JPEG")
        file_size = os.path.getsize(resized_path)
        logger.info(f"Сохранено измененное изображение по адресу {resized_path} с размером {file_size} байт")
        return resized_path, resized_img.size, file_size
    except Exception as e:
        logger.error(f"Ошибка сохранения измененного изображения {size}: {e}")
        return None


@shared_task
def process_image(file_path: str | bytes, name: str) -> None:
    """Задача обработки изображения: изменение размера и сохранение в БД."""
    base_dir = Path(settings.MEDIA_ROOT) / 'images' / name
    base_dir.mkdir(parents=True, exist_ok=True)
    processed_files = []
    try:
        with PILImage.open(file_path) as img:
            for size in SIZES:
                result = save_resized_image(img, size, name, base_dir)
                if result:
                    processed_files.append(result)
                else:
                    logger.warning(f"Не удалось обработать размер изображения {size} для {file_path}")

            for path, res, size in processed_files:
                Image.objects.create(
                    name=f"{path.stem}",
                    file_path=str(path),
                    resolution=f"{res[0]}x{res[1]}",
                    size=size
                )
                logger.info(f"Изображение сохранено в базе данных: {path.stem} ({res[0]}x{res[1]}, {size} байт)")
    except UnidentifiedImageError as e:
        logger.error(f"Не удалось открыть изображение {file_path}: {e}")
    except Exception as e:
        logger.error(f"Произошла ошибка в process_image: {e}")


@shared_task()
def del_file(file_name: str | bytes) -> None:
    """Удаляет файл и обрабатывает исключения."""
    try:
        os.remove(file_name)
        logger.info(f"Удаляет файл: {file_name}")
    except FileNotFoundError:
        logger.warning(f"Файл не найден для удаления: {file_name}")
    except OSError as e:
        logger.error(f"Ошибка удаления файла {file_name}: {e}")

