from rest_framework import permissions


class IsCreatorOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can read; only the creator can modify or delete."""

    message = "Only the user who created this record can modify or delete it."

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.created_by_id == request.user.id
