from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
