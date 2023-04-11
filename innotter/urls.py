from rest_framework.routers import DefaultRouter

from django.urls import path, include
from django.contrib import admin
from .views import PageViewSet, UserViewSet, PostViewSet, SearchViewList

router = DefaultRouter()
router.register(r'pages', PageViewSet, basename='pages')
router.register(r'users', UserViewSet, basename='users')
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('pages/<int:page_pk>/posts/<int:pk>/',
         PostViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'}),
         name='post-detail'),
    path('pages/<int:page_id>/posts/<int:post_id>/like/', PostViewSet.as_view({'post': 'like'}),
         name='post_like'),
    path('pages/<int:page_id>/posts/<int:post_id>/unlike/', PostViewSet.as_view({'post': 'unlike'}),
         name='post_like'),
    path('search/', SearchViewList.as_view(), name='user_and_page_search'),

]
