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

