from rest_framework import permissions


class SafeOrAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorModeratorAdministratorOrReadOnly(
        permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and obj.author == request.user
            or request.user.is_authenticated and request.user.is_admin
            or request.user.is_authenticated and request.user.is_moderator
        )


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

