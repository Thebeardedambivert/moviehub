from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import BasePermission, DjangoModelPermissions

#Create a permission that allows us to block users. 
#Since this is a permission that would be a custom one and is an object related permission,
#we would need to extend the base permission class.


class BlockUserPermission(BasePermission):
    blocked_users_id = []

    def has_permission(self, request, view):
        #Getting the current user
        user = request.user
        if request.user.has_perm('hub.block_user'):
            return request.user.has_perm('hub.block_user')
        elif user.is_authenticated and user.id in self.blocked_users_id:
            return False
    

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.is_staff)
    

class ViewCustomerHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('hub.view_history')