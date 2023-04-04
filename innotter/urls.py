from rest_framework.routers import DefaultRouter

from django.urls import path, include
from django.contrib import admin
from .views import PageViewSet, UserViewSet, PostViewSet, SearchViewList

router = DefaultRouter()
router.register(r'pages', PageViewSet)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('pages/<int:page_pk>/posts/<int:pk>/',
         PostViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='post-detail'),
    path('pages/<int:page_id>/posts/<int:post_id>/like/', PostViewSet.as_view({
        'post': 'like',
        'delete': 'unlike'
    }), name='post_like'),
    path('users/account/liked_posts/', UserViewSet.as_view({'get': 'liked_posts'}), name='user-liked-posts'),
    path('users/account/news/', UserViewSet.as_view({'get': 'news'}), name='user-news'),
    path('search/', SearchViewList.as_view(), name='user_and_page_search'),

]
