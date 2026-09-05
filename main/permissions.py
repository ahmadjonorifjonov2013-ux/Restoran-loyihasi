from rest_framework import permissions

def is_admin(user):
    return user and user.is_authenticated and (user.is_superuser or user.groups.filter(name='Administrator').exists())

def is_oshpaz(user):
    return user and user.is_authenticated and user.groups.filter(name='Oshpaz').exists()


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_admin(request.user)


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsOshpazOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user) or is_oshpaz(request.user)


class IsTelegramBotOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        bot_secret = request.headers.get('X-Telegram-Bot-Secret')
        if bot_secret and bot_secret == 'SUPER_SECRET_BOT_KEY': 
            return True
        return is_admin(request.user)