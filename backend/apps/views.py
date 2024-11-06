import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiExample, extend_schema
from loguru import logger

from .models import Image
from .serializers import ImageSerializer, RegisterSerializer, UserSerializer
from .tasks import process_image, del_file
from .permissions import IsUserProfile
from .services.rabbitmq.rabbitmq_service import send_rabbitmq_message
from .services.services import get_mime_type


class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        """Регистрация нового пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User successfully created."
        })


class ProfileViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):
    """Предоставляет доступ к профилю пользователя."""
    permission_classes = [IsUserProfile]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ['get', 'patch', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response({
            "user": UserSerializer(request.user, context=self.get_serializer_context()).data,
        })


class ImageViewSet(viewsets.ModelViewSet):
    """API для работы с изображениями."""
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    # @extend_schema(
    #     request=ImageSerializer,
    #     responses={201: ImageSerializer},
    #     examples=[
    #         OpenApiExample(
    #             'Example Create Image',
    #             value={
    #                 'name': 'test_image',
    #                 # 'file_path': '/images/test_image.jpg',
    #                 # 'resolution': '500x500',
    #                 # 'size': 1024
    #             }
    #         )
    #     ]
    # )
    def create(self, request, *args, **kwargs):
        """Создание изображения."""
        file = request.FILES["file"]
        file_type = get_mime_type(file)
        if file_type != "image":
            logger.info("Щас вернем 415")
            return Response(
                {"error": "Unsupported file type"},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )
        name = request.POST.get("name", "Untitled")
        fs = FileSystemStorage()
        file_name = fs.save(file.name, file)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        # process_image.delay(file.temporary_file_path(), name)
        try:
            process_image(file_path, name)

            send_rabbitmq_message(f"Image uploaded: {name}")
            return Response({'status': 'image upload started'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return Response(
                {"error": "Image processing failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            del_file(file_path)

    def update(self, request, *args, **kwargs):
        """Обновление информации об изображении."""
        try:
            response = super().update(request, *args, **kwargs)
            image = self.get_object()
            send_rabbitmq_message(f"Image updated: {image.name}")
            return response
        except Exception as e:
            logger.error(f"Error updating image: {e}")
            return Response(
                {"error": "Failed to update image"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """Удаление изображения."""
        image = self.get_object()

        try:
            super().destroy(request, *args, **kwargs)
            send_rabbitmq_message(f"Image deleted: {image.name}")
            return Response(data={'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
