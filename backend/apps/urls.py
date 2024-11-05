from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, RegisterView, ProfileViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
    path('register/', RegisterView.as_view()),
    path('profile/', ProfileViewSet.as_view({'get': 'retrieve'}), name='profile'),
    path('profile/<int:pk>/', ProfileViewSet.as_view({'patch': 'partial_update'}), name='partial_update'),
    path('profile/delete/<int:pk>/', ProfileViewSet.as_view({'delete': 'destroy'}), name='destroy'),

]
