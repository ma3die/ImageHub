import os
from pathlib import Path
from django.conf import settings
from django.test import TestCase
from PIL import Image as PILImage
from apps.tasks import process_image

class ProcessImageTests(TestCase):
    def setUp(self):
        self.test_image_path = Path(settings.MEDIA_ROOT) / 'test_image.jpg'
        # Создаем тестовое изображение
        image = PILImage.new('RGB', (1024, 768), color='red')
        image.save(self.test_image_path)

    def tearDown(self):
        # Удаляем тестовые файлы после каждого теста
        if self.test_image_path.exists():
            self.test_image_path.unlink()
        for size in [(100, 100), (500, 500)]:
            resized_path = Path(settings.MEDIA_ROOT) / 'images' / 'test_image' / f"test_image_{size[0]}x{size[1]}.jpg"
            if resized_path.exists():
                resized_path.unlink()

    def test_process_image(self):
        # Тестируем основную функцию обработки изображения
        process_image(str(self.test_image_path), 'test_image')
        for size in [(100, 100), (500, 500)]:
            resized_path = Path(settings.MEDIA_ROOT) / 'images' / 'test_image' / f"test_image_{size[0]}x{size[1]}.jpg"
            self.assertTrue(resized_path.exists(), f"File {resized_path} does not exist")
