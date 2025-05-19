from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Skill, PortfolioTheme, PortfolioSettings, SubscriptionCode, ProfileView

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Кастомная админ-панель для расширенной модели пользователя"""
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email',)
    ordering = ('username',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Админка для навыков"""
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name',)

@admin.register(PortfolioTheme)
class PortfolioThemeAdmin(admin.ModelAdmin):
    """Админка для тем портфолио"""
    list_display = ('name', 'description', 'is_premium')
    list_filter = ('is_premium',)
    search_fields = ('name', 'description')

@admin.register(PortfolioSettings)
class PortfolioSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек портфолио"""
    list_display = ('user', 'theme')
    list_filter = ('theme',)
    search_fields = ('user__username',)

@admin.register(SubscriptionCode)
class SubscriptionCodeAdmin(admin.ModelAdmin):
    """Админка для кодов подписки"""
    list_display = ('code', 'is_used', 'created_at', 'used_at')
    list_filter = ('is_used',)
    search_fields = ('code',)

@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    """Админка для просмотров профиля"""
    list_display = ('profile_user', 'viewer', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('profile_user__username', 'viewer__username')
