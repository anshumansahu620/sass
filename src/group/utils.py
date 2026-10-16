from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner is not None and obj.owner.user == request.user
class IsGroupAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.group_admin==request.user
