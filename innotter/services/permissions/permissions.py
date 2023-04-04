from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from innotter.models import User



class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ('admin', 'moderator')



class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsOwnerOrAuthorityCanEdit(permissions.BasePermission):
    user_allowed_fields = {'name', 'description', 'image', 'is_private'}
    admin_allowed_fields = {'is_blocked', 'unblock_date'}

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_anonymous and request.method in permissions.SAFE_METHODS:
            return True

        if user.role in ('admin', 'moderator') and request.method in ['PUT', 'PATCH']:
                fields = set(request.data.keys())
                return fields.issubset(self.admin_allowed_fields)

        if user == obj.owner and request.method in ['PUT', 'PATCH']:
            fields = set(request.data.keys())
            return fields.issubset(self.user_allowed_fields)

        return False
class OwnerCanEditOrAdminCanBlockUser(IsOwnerOrAuthorityCanEdit):
    user_allowed_fields = {'username', 'email'}
    admin_allowed_fields = {'is_blocked'}

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_anonymous and request.method in permissions.SAFE_METHODS:
            return True

        if user.role in ('admin', 'moderator'):
            if request.method in ['PUT', 'PATCH']:
                fields = set(request.data.keys())
                return fields.issubset(self.admin_allowed_fields)

            return True

        if user.pk == obj.pk and request.method in ['PUT', 'PATCH']:
            fields = set(request.data.keys())
            return fields.issubset(self. user_allowed_fields)

        return False

class FollowersPermission(IsAuthenticated):
    pass


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS or request.user.is_authenticated)
