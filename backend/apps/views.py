import os
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage, FileSystemStorage
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from loguru import logger

from .models import Image
from .serializers import ImageSerializer
from .tasks import process_image, del_file


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        file = request.FILES["file"]
        name = request.POST.get("name", "Untitled")
        fs = FileSystemStorage()
        file_name = fs.save(file.name, file)
        file_path = fs.url(file_name)
        logger.info(f"fs - {fs}")
        logger.info(f"file_name - {file_name}")
        logger.info(f"file_url - {file_path}")
        # file_name = default_storage.save(file.name, file)
        # file_name = file.name
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        logger.info(f"file_type - {type(file)}")
        logger.info(f"file_path - {type(file_path)}")
        # process_image.delay(file.temporary_file_path(), name)
        #TODO передавать файл или сохранять у себя, а потом удалять
        process_image(file_path, name)
        del_file(file_path)

        return Response({'status': 'image upload started'}, status=status.HTTP_201_CREATED)

