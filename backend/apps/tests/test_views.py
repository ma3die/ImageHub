from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from apps.models import Image
from PIL import Image as PILImage
import io


class ImageViewSetTests(TestCase):
    def setUp(self):
        # Настройка пользователя и клиента
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def generate_test_image(self):
        """Генерирует изображение в формате JPEG и возвращает его как файл."""
        image = PILImage.new("RGB", (100, 100), color="red")  # Создаем простое изображение 100x100
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.name = 'test_image.jpg'
        image_file.seek(0)
        return image_file

    def test_upload_image(self):
        url = reverse('image-list')  # URL для загрузки изображения
        image_file = self.generate_test_image()
        data = {'file': image_file, 'name': 'test_image'}
        response = self.client.post(url, data, format='multipart')

        # Проверка успешности загрузки
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Image.objects.filter(name='test_image_500x500').exists())

    def test_transform_image(self):
        image = Image.objects.create(name='test_image', file_path='test_path', resolution='100x100', size=1024)
        self.assertEqual(image.name, 'test_image')
        self.assertEqual(image.resolution, '100x100')

    def test_delete_image(self):
        image = Image.objects.create(name='test_image', file_path='test_path', resolution='100x100', size=1024)
        url = reverse('image-detail', args=[image.id])
        response = self.client.delete(url)

        # Проверка успешного удаления
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Image.objects.filter(id=image.id).exists())
