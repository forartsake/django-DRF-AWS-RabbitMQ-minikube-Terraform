from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from innotter.models import Page, User


class PageSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault)

    class Meta:
        model = Page
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'image_s3_path', 'role', 'title', 'is_blocked')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            title=validated_data['title']
        )
        return user
