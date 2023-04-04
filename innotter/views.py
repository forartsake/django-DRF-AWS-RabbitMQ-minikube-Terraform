from django.db.models import Q

from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets, status, generics
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.exceptions import PermissionDenied

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework.viewsets import GenericViewSet, ViewSetMixin

from innotter.models import Page, User, Post
from innotter.serializers import PageSerializer, UserSerializer, PostSerializer, FollowerSerializer, \
    CreatePostSerializer, PageCreateSerializer, PostContentSerializer, UserSearchSerializer, PageSearchSerializer, \
    CreateTagSerializer

from innotter.services.permissions.permissions import IsOwnerOrReadOnly, \
    IsOwnerOrAuthorityCanEdit, IsAdminOrReadOnly, OwnerCanEditOrAdminCanBlockUser
from innotter.services.services import PageService, PostService, UserService, AuthService

from rest_framework import filters
from django_filters import rest_framework as django_filters


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminOrReadOnly]
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.permission_classes = [OwnerCanEditOrAdminCanBlockUser]
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminOrReadOnly]
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()
            new_user.set_password(serializer.validated_data['password'])
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        token = AuthService.create_token(username, password)
        if token:
            return Response({'username': username, 'token': token})
        else:
            return Response({'error': 'Invalid username/password'}, status=400)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def account(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def user_liked_posts(self, request, pk=None):
        user = request.user
        liked_posts = UserService.get_liked_posts_by_user(user.id)
        serializer = PostContentSerializer(liked_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def news(self, request):
        user = request.user
        news_posts = UserService.get_news_posts(user)
        serializer = PostContentSerializer(news_posts, many=True)
        return Response(serializer.data)


class PageViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):

    queryset = Page.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PageCreateSerializer
        return PageSerializer

    def update(self, request, *args, **kwargs):
        self.permission_classes = [IsOwnerOrAuthorityCanEdit]
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminOrReadOnly]
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [IsOwnerOrReadOnly]
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'delete'], serializer_class=CreateTagSerializer)
    def modify_tag(self, request, pk=None):
        page = self.get_object()
        if page.owner != request.user:
            return Response({'status': 'You do not have permission to perform this action.'},
                            status=403)
        tag_names = [tag_data['name'] for tag_data in request.data]
        if request.method == 'POST':
            PageService.add_tag_to_page(page, tag_names)
            return Response({'status': 'Tags have been added successfully.'})
        elif request.method == 'DELETE':
            print("I am here in DELETE method")
            PageService.remove_tags_from_page(page, tag_names)
            return Response({'status': 'Tags have been removed successfully.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe_or_unsubscribe(self, request, pk=None):
        page = self.get_object()
        user_id = request.data.get('user_id')
        flag = request.data.get('flag')

        success, message = PageService.follow_or_unfollow(user_id, page.id, flag)
        if success:
            return Response({'status': message})
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
        serializer = CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            post = PostService().create_post(user=request.user, page_id=pk, data=serializer.validated_data)
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    post_service = PostService()

    def perform_create(self, serializer):
        page_id = self.kwargs['page_id']
        page = get_object_or_404(Page, pk=page_id)
        if page.owner != self.request.user:
            raise PermissionDenied("You don't have permission to create posts for this page.")
        post = self.post_service.create_post(user=self.request.user, page_id=page_id, data=serializer.validated_data)
        return Response(PostSerializer(post).data, status=201)

    def perform_update(self, serializer):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        if post.page.owner != self.request.user:
            raise PermissionDenied("You don't have permission to update this post.")
        post = self.post_service.update_post(user=self.request.user, post_id=post_id, data=serializer.validated_data)
        return Response(PostSerializer(post).data, status=200)

    def perform_destroy(self, instance):
        post_id = instance.id
        post = get_object_or_404(Post, pk=post_id)
        self.post_service.delete_post(user=self.request.user, post_id=post_id)
        print("I am in perform_destroy")
        return Response({'message': 'Post has been deleted successfully.'}, status=200)

    def like(self, request, page_id, post_id):
        self.post_service.like_post(user=self.request.user, post_id=post_id)
        return Response({'message': 'Post has been liked successfully.'}, status=200)

    def unlike(self, request, page_id, post_id):
        self.post_service.unlike_post(user=self.request.user, post_id=post_id)
        return Response({'message': 'Post has been unliked successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):

        post = self.get_object()
        page_id = request.data.get('page_id')
        if not page_id:
            return Response({'page_id': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        page = get_object_or_404(Page, pk=page_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(page=page, reply_to=post)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SearchViewList(generics.ListAPIView):
    serializer_class = None
    queryset = None
    filter_backends = [filters.SearchFilter]
    search_fields = []

    def get_serializer_class(self):
        print(f"I am in get_serializer")
        if self.request.query_params.get('type') == 'user':
            print(f" self.request.query_params.get('type') == 'user' {self.request.query_params.get('type') == 'user'}")
            return UserSearchSerializer
        elif self.request.query_params.get('type') == 'page':
            print(f"self.request.query_params.get('type') == 'page' {self.request.query_params.get('type') == 'page'}")
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
