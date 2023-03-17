import os
from datetime import datetime, timedelta

import jwt
from django.contrib.auth import authenticate
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from innotter.models import Page, User
from innotter.serializers import PageSerializer, UserSerializer, AdminOrModeratorPageSerializer, OwnerPageSerializer
from innotter.services.permissions.permissions import IsOwnerOrModeratorCanEdit


class PageViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [IsOwnerOrModeratorCanEdit, IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token = jwt.encode(
                payload={
                    'user_id': user.id,
                    'exp': (datetime.now() + timedelta(seconds=int(os.getenv('WT_EXPIRATION_DELTA')))).timestamp()
                },
                key=os.getenv('SECRET_KEY'),
                algorithm='HS256'
            )
            return Response({'token': token})
        else:
            return Response({'error': 'Invalid username/password'}, status=400)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def account(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)




