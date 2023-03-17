import os
import jwt
from django.http import JsonResponse
from innotter.models import User
from rest_framework import authentication



class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get('Authorization', None)
        if not header:
            return None
        token = header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        except jwt.exceptions.DecodeError:
            return JsonResponse({'DRF_error ': 'Invalid token'}, status=401)
        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'DRF_error': 'Token has expired'}, status=401)

        user = User.objects.get(id=decoded_token['user_id'])
        if not user:
            return JsonResponse({'DRF_error': 'User does not exist'}, status=404)
        return (user, decoded_token)

    # import jwt
    # from rest_framework.authentication import BaseAuthentication
    # from rest_framework.exceptions import AuthenticationFailed
    # from innotter.models import User
    #
    # class JWTAuthentication(BaseAuthentication):
    #     def authenticate(self, request):
    #         # Получаем токен из заголовка авторизации
    #         auth_header = request.headers.get('Authorization')
    #         if not auth_header:
    #             return None
    #         auth_token = auth_header.split(' ')[1]
    #
    #         try:
    #             # Декодируем токен
    #             payload = jwt.decode(auth_token, 'SECRET_KEY', algorithms=['HS256'])
    #         except jwt.exceptions.DecodeError:
    #             raise AuthenticationFailed('Invalid token')
    #         except jwt.exceptions.ExpiredSignatureError:
    #             raise AuthenticationFailed('Token has expired')
    #
    #         # Получаем пользователя по ID из токена
    #         try:
    #             user = User.objects.get(id=payload['user_id'])
    #         except User.DoesNotExist:
    #             raise AuthenticationFailed('User not found')
    #
    #         # Возвращаем кортеж (user, token), который будет установлен в request.user и request.auth соответственно
    #         return (user, auth_token)
    #
    #     def authenticate_header(self, request):
    #         # Возвращаем значение заголовка, которое будет отправлено в ответ на 401 Unauthorized
    #         return 'Bearer realm="api"'
