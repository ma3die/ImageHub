from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from loguru import logger

from .models import Image
from .serializers import ImageSerializer
from .tasks import process_image


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        file = request.FILES["file"]
        logger.info(f"file_type - {type(file)}")
        name = request.POST.get('name', 'Untitled')
        path = file.temporary_file_path()
        # process_image.delay(file.temporary_file_path(), name)
        #TODO передавать файл или сохранять у себя, а потом удалять
        process_image(file.temporary_file_path(), name)

        return Response({'status': 'image upload started'}, status=status.HTTP_201_CREATED)

