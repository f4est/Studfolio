from rest_framework import permissions


class IsAdminOrTeacherOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на чтение всем пользователям,
    а полный доступ только администраторам и преподавателям.
    """
    
    def has_permission(self, request, view):
        # Разрешить GET, HEAD или OPTIONS запросы всем
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешить запись администраторам и преподавателям
        return request.user.is_authenticated and (
            request.user.is_admin() or request.user.is_teacher()
        )


class IsUserOrAdmin(permissions.BasePermission):
    """
    Разрешает действия только владельцу объекта или администратору.
    """
    
    def has_object_permission(self, request, view, obj):
        # Проверить, является ли пользователь владельцем объекта или администратором
        return request.user.is_authenticated and (
            obj.id == request.user.id or request.user.is_admin()
        )


class IsOwnerOrTeacherOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ владельцу, преподавателю или администратору.
    """
    
    def has_object_permission(self, request, view, obj):
        # Разрешить GET, HEAD или OPTIONS запросы всем
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True
        
        # Проверить, является ли пользователь владельцем, преподавателем или администратором
        return request.user.is_authenticated and (
            obj.user.id == request.user.id or  # Владелец
            request.user.is_teacher() or  # Преподаватель
            request.user.is_admin()  # Администратор
        ) 