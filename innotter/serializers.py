from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from innotter.models import Page, User, Post, Tag


# USERS SERIALIZERS
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(validators=[validate_password], write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'image_s3_path', 'role', 'title', 'is_blocked')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PageCreateSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(read_only=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(), required=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Page
        fields = ['name', 'description', 'tags', 'uuid', 'owner']


class TagSerializer(serializers.ModelSerializer):
    pages = PageCreateSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name')


class CreateTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'id')


class PageSerializer(serializers.ModelSerializer):
    tags = CreateTagSerializer(many=True)

    class Meta:
        model = Page
        fields = ['id', 'name', 'description', 'tags', 'uuid', 'owner', 'followers', 'follow_requests', 'is_private',
                  'is_blocked', 'unblock_date']


class PostSerializer(serializers.ModelSerializer):
    page = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all(), required=False)

    class Meta:
        model = Post
        fields = '__all__'


class CreatePostSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=180)

    class Meta:
        model = Post
        fields = ['content']


class FollowerSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ('username',)


class PostContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('content', 'created_at', 'page')


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name')


class PageSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'tags')
