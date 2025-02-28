from rest_framework import permissions


class IsPermission(permissions.BasePermission):
    def has_permission(self, request, view, obj=None):
        return request.user.is_staff or obj == request.user
