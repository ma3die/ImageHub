from django.db import models

class Image(models.Model):
    """Модель изображений"""
    name = models.CharField(max_length=255, verbose_name="Название изображения")
    file_path = models.CharField(max_length=255, verbose_name="Путь к файлу")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    resolution = models.CharField(max_length=255, verbose_name="Разрешение")
    size = models.IntegerField(verbose_name="Размер файла")

    objects = models.Manager()

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
        ordering = ["-upload_date"]

    def __str__(self):
        return self.name


