from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Cho phép mọi người xem (phương thức GET) mà không cần quyền truy cập.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Cho phép chỉ admin thực hiện phương thức POST.
        return request.user and (request.user.is_staff or request.user.groups.filter(name='admin').exists())
    
class IsAdminOrAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        # Cần admin hoặc là tác giả mới được phép thực hiện phương thức 
        return request.user and (request.user.is_staff or request.user.groups.filter(name='admin').exists())
