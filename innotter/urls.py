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

# GET /pages/ - получить список всех страниц
# POST /pages/ - создать новую страницу
# GET /pages/{id}/ - получить конкретную страницу по ID
# PUT /pages/{id}/ - полностью обновить конкретную страницу по ID
# PATCH /pages/{id}/ - частично обновить конкретную страницу по ID
# DELETE /pages/{id}/ - удалить конкретную страницу по ID
