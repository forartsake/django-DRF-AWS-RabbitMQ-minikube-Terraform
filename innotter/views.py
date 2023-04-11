from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status, generics
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSetMixin
from innotter.models import Page, User, Post
from innotter.serializers import PageSerializer, UserSerializer, PostSerializer, FollowerSerializer, \
    CreatePostSerializer, PageCreateSerializer, PostContentSerializer, UserSearchSerializer, PageSearchSerializer, \
    CreateTagSerializer
from innotter.services.permissions.permissions import IsOwnerOrReadOnly, \
    IsOwnerOrAuthorityCanEdit, IsAdminOrReadOnly, OwnerCanEditOrAdminCanBlockUser, IsOwnerOnly, \
    IsOwnerCanEditPostOrReadOnly
from innotter.services.services import PageService, PostService, UserService, AuthService
from rest_framework import filters


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()
            new_user.set_password(serializer.validated_data['password'])
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        token = AuthService.create_token(username, password)
        if token:
            return Response({'username': username, 'token': token}, status=200)
        else:
            return Response({'error': 'Invalid username/password'}, status=400)

    @action(detail=True, methods=['get'])
    def user_liked_posts(self, request, pk=None):
        """
        Returns all posts that have been liked by a particular user
        """
        user = request.user
        if int(pk) == user.pk:
            liked_posts = UserService.get_liked_posts_by_user(user.id)
            serializer = PostContentSerializer(liked_posts, many=True)
            return Response(serializer.data)
        else:
            return Response({'status': 'You do not have permission to perform this action.'},
                            status=403)

    @action(detail=True, methods=['get'])
    def news(self, request, pk=None):
        """
        Returns news feed to a particular user, consisting of both his own posts and those of his followers
        """
        user = request.user
        if int(pk) == user.pk:
            news_posts = UserService.get_news_posts(user)
            return Response({'news_posts': news_posts})
        else:
            return Response({'status': 'You do not have permission to perform this action.'},
                            status=403)

    def get_permissions(self):
        if self.action in ('login', 'register'):
            return [AllowAny()]
        elif self.request.method in ('PUT', 'PATCH'):
            return [OwnerCanEditOrAdminCanBlockUser()]
        else:
            return [IsAuthenticated()]


class PageViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = Page.objects.all()

    @action(detail=True, methods=['post', 'delete'], serializer_class=CreateTagSerializer, name='modify_tag')
    def modify_tag(self, request, pk=None):
        page = self.get_object()
        if page.owner != request.user:
            return Response({'status': 'You do not have permission to perform this action.'},
                            status=403)
        tag_names = [tag_data['name'] for tag_data in request.data]
        if request.method == 'POST':
            PageService.add_tag_to_page(page, tag_names)
            return Response({'status': 'Tags have been added successfully.'}, status=200)
        elif request.method == 'DELETE':
            PageService.remove_tags_from_page(page, tag_names)
            return Response({'status': 'Tags have been removed successfully.'}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe_or_unsubscribe(self, request, pk=None):
        page = self.get_object()
        user_id = request.data.get('user_id')

        flag = request.data.get('flag')

        success, message = PageService.follow_or_unfollow(user_id, page.id, flag)
        if success:
            return Response({'status': message}, status=200)
        else:
            return Response({'error': message}, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    def accept_or_reject_subscription(self, request, pk=None):
        page = self.get_object()
        user = User.objects.get(id=request.user.pk)
        request_user_ids = request.data.get('user_ids')
        flag = request.data.get('flag')

        success, message = PageService.accept_or_reject_follow_request(page, user, request_user_ids, flag)

        if success:
            return Response({'status': message})
        else:
            return Response({'error': message}, status=400)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def followers_list(self, request, pk=None):
        user = request.user
        page = self.get_object()
        if user.is_authenticated:
            followers = page.followers.all()
            serializer = FollowerSerializer(followers, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsOwnerOrReadOnly])
    def follow_requests_list(self, request, pk=None):
        user = request.user
        page = self.get_object()
        if user != page.owner:
            return Response({'Access has been denied'}, status=403)

        follow_requests = page.follow_requests.all()
        serializer = FollowerSerializer(follow_requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    def create_post(self, request, pk=None):
        page = get_object_or_404(Page, id=pk)
        post = PostService.create_post(page, request.user, request.data)

        serializer = PostSerializer(post)
        return Response(serializer.data, status=201)

    def get_serializer_class(self):
        if self.action == 'create':
            return PageCreateSerializer
        return PageSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        elif self.request.method in ('PUT', 'PATCH'):
            return [IsOwnerOrAuthorityCanEdit()]
        elif self.request.method == 'DELETE':
            return [IsOwnerOnly()]
        else:
            return [IsAuthenticated()]


class PostViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def like(self, request, post_id, page_id):
        success, message = PostService.like_post(user=request.user, post_id=post_id)
        if success:
            return Response({'message': message}, status=200)
        else:
            return Response({'message': message}, status=403)

    def unlike(self, request, page_id, post_id):
        success, message = PostService.unlike_post(user=request.user, post_id=post_id)
        if success:
            return Response({'message': 'Post has been unliked successfully.'}, status=200)
        else:
            return Response({'message': message}, status=400)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):

        post = self.get_object()
        page_id = request.data.get('page_id')
        if not page_id:
            return Response({'page_id': ['This field is required.']}, status=400)

        page = get_object_or_404(Page, pk=page_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(page=page, reply_to=post)

        return Response(serializer.data, status=200)

    def get_permissions(self):
        if self.action in ('like', 'unlike', 'reply'):
            return [IsAuthenticated()]
        else:
            return [IsOwnerCanEditPostOrReadOnly()]


class SearchViewList(generics.ListAPIView):
    serializer_class = None
    queryset = None
    filter_backends = [filters.SearchFilter]
    search_fields = []

    def get_serializer_class(self):
        if self.request.query_params.get('type') == 'user':
            return UserSearchSerializer
        elif self.request.query_params.get('type') == 'page':
            return PageSearchSerializer
        else:
            return None

    def get_queryset(self):
        search = self.request.query_params.get('search', False).lower()
        type_ = self.request.query_params.get('type', False).lower()

        if type_ == 'user':
            return User.objects.filter(
                Q(username__icontains=search) |
                Q(last_name__icontains=search) |
                Q(first_name__icontains=search)
            ).distinct()
        elif type_ == 'page':
            return Page.objects.filter(
                Q(name__icontains=search) |
                Q(uuid__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        return super().get_queryset()
