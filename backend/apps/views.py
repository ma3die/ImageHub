import os
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage, FileSystemStorage
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from loguru import logger

from .models import Image
from .serializers import ImageSerializer, RegisterSerializer, UserSerializer
from .tasks import process_image, del_file
from .permissions import IsUserProfile
from .services.rabbitmq.rabbitmq_service import send_rabbitmq_message


class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User successfully created."
        })


class ProfileViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsUserProfile]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ['get', 'patch', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response({
            "user": UserSerializer(request.user, context=self.get_serializer_context()).data,
        })

    # def perform_destroy(self, instance):
    #     instance.delete()


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

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
        # TODO передавать файл или сохранять у себя, а потом удалять
        process_image(file_path, name)
        del_file(file_path)

        # send_rabbitmq_message(f"Image uploaded: {name}")

        return Response({'status': 'image upload started'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Логика обновления изображения
        response = super().update(request, *args, **kwargs)

        # Отправка сообщения об обновлении изображения
        image = self.get_object()
        # send_rabbitmq_message(f"Image updated: {image.name}")
        return Response(response)

    def destroy(self, request, *args, **kwargs):
        # Логика удаления изображения
        image = self.get_object()
        # send_rabbitmq_message(f"Image deleted: {image.name}")
        try:
            super().destroy(request, *args, **kwargs)
            return Response(data={'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
