import os
import jwt
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from innotter.models import User


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header = request.headers.get('Authorization', None)
        if not header:
            request.user = AnonymousUser()
            return self.get_response(request)

        try:
            token = header.split(' ')[1]
            decoded_token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = User.objects.get(id=user_id)
            if not user:
                return JsonResponse({'error': 'User does not exist'}, status=404)
            request.user = user
        except jwt.exceptions.DecodeError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({'error': 'Token is expired'}, status=401)
        return self.get_response(request)



