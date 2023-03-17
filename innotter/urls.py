from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import PageViewSet, UserViewSet

router = DefaultRouter()
router.register(r'pages', PageViewSet)
router.register(r'users', UserViewSet)
urlpatterns = [
    path('', include(router.urls)),

]
