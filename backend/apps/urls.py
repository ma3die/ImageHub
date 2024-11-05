from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, RegisterView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
    path('register/', RegisterView.as_view()),
    path('profile/', ProfileView.as_view()),

]
