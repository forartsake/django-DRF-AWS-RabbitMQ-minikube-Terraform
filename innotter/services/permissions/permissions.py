from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        return request.user.role in ('admin', 'moderator')


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwnerCanEditPostOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.page.owner == request.user


class IsOwnerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'DELETE'

    def has_object_permission(self, request, view, obj):
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

        if user.is_anonymous:
            return False
        if all([
            user.role == 'user',
            user.pk != obj.pk,
            request.method in ['PUT', 'PATCH']
        ]):
            return False

        if user.is_anonymous and request.method in permissions.SAFE_METHODS:
            return True

        if user.role == 'admin' and request.method in ['PUT', 'PATCH']:
            fields = set(request.data.keys())
            if not fields.issubset(self.admin_allowed_fields):
                return False

        if user == obj.owner and request.method in ['PUT', 'PATCH']:
            fields = set(request.data.keys())
            if not fields.issubset(self.user_allowed_fields):
                return False

        return True


class OwnerCanEditOrAdminCanBlockUser(permissions.BasePermission):
    user_allowed_fields = {'username', 'email'}
    admin_allowed_fields = {'is_blocked'}

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_anonymous:
            return False
        if all([
            user.role == 'user',
            user.pk != obj.pk,
            request.method in ['PUT', 'PATCH']
        ]):
            return False
        if user.role in ('admin', 'moderator'):
            if request.method in ['PUT', 'PATCH']:
                fields = set(request.data.keys())
                if not fields.issubset(self.admin_allowed_fields):
                    return False

        if user.pk == obj.pk and request.method in ['PUT', 'PATCH']:
            fields = set(request.data.keys())
            if not fields.issubset(self.user_allowed_fields):
                return False
        return True
