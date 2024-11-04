from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls))
    path("api/token/", TokenObtainPairView.as_view(), name="token"),
    path("api/refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
]
