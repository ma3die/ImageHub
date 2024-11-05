import os
from pathlib import Path

from celery import shared_task
from PIL import Image as PILImage
from django.core.files.base import ContentFile
from django.conf import settings
from loguru import logger

from .models import Image

SIZES = [(100, 100), (500, 500)]


def save_resized_image(original_image: PILImage, size: tuple[int, int], name: str, base_dir: Path) -> tuple | None:
    try:
        resized_img = original_image.resize(size).convert("L")
        resized_path = base_dir / f"{name}_{size[0]}x{size[1]}.jpg"
        logger.info(f"resized_path {resized_path}")
        resized_img.save(resized_path, format="JPEG")
        return resized_path, resized_img.size, os.path.getsize(resized_path)
    except Exception:
        return None


# @shared_task
def process_image(file_path: str, name: str) -> None:
    try:
        with PILImage.open(file_path) as img:
            base_dir = Path(settings.MEDIA_ROOT) / 'images' / name
            base_dir.mkdir(parents=True, exist_ok=True)

            processed_files = []

            for size in SIZES:
                result = save_resized_image(img, size, name, base_dir)
                if result:
                    processed_files.append(result)

            for path, res, size in processed_files:
                logger.info(f"path.stem {path.stem}")
                logger.info(f"name {name}")
                Image.objects.create(
                    name=f"{name}_{path.stem}",
                    file_path=str(path),
                    resolution=f"{res[0]}x{res[1]}",
                    size=size
                )
    except Exception as e:
        logger.error(f"Achtung!!! {e}")

def del_file(file_name: str) -> None:
    os.remove(file_name)
    # logger.info(f"path del {Path(settings.MEDIA_ROOT)}")
    # folder = Path(settings.MEDIA_ROOT)
    # logger.info(file_name)
    # for item in folder.iterdir():
    #     if item.is_file() and item == file_name:
    #         item.unlink()
    #     elif item.is_dir():
    #         continue

# celery -A backend worker -l info
