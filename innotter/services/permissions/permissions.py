from rest_framework import permissions
from innotter.models import User


# Allows only administrators to execute methods; others - only read requests.
class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


# Only owner of the page may edit it
class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


# Allows moderators to make read, create, and edit requests, but does not allow removal of pages that are blocked.
class IsModeratorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated and request.user.role == User.Roles.MODERATOR:
            if view.action in ['list', 'retrieve', 'create']:
                return True
            elif view.action in ['update', 'partial_update']:
                return not obj.is_blocked
            elif view.action == 'destroy':
                return not obj.is_blocked
        return False


class IsOwnerOrModeratorCanEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_authenticated:
            if user.role in (User.Roles.ADMIN, User.Roles.MODERATOR):
                if request.method in ['PUT', 'PATCH']:
                    return 'is_blocked' in request.data or 'unblock_date' in request.data # allowed_fields = subset < requst...
                return True
            elif user == obj.owner:
                if request.method in ['PUT', 'PATCH']:
                    return 'name' in request.data or 'description' in request.data or 'image' in request.data # the same
                return True
        return False
