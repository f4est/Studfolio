from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Skill, PortfolioTheme, PortfolioSettings, SubscriptionCode, ProfileView, ResumeTemplate, UserResumeSettings

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


class SkillAdmin(admin.ModelAdmin):
    """Админка для навыков"""
    list_display = ('name', 'user', 'level')
    list_filter = ('level',)
    search_fields = ('name', 'user__username')


class CustomUserAdmin(UserAdmin):
    """Кастомная админ-панель для расширенной модели пользователя"""
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_public', 'has_active_subscription')
    list_filter = ('user_type', 'is_staff', 'is_active', 'is_public')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Персональная информация'), {'fields': (
            'first_name', 'last_name', 'email', 'bio', 'profile_image',
            'date_of_birth', 'phone_number'
        )}),
        (_('Информация об обучении'), {'fields': (
            'university', 'faculty', 'specialization', 'year_of_study'
        )}),
        (_('Настройки портфолио'), {'fields': (
            'is_public', 'custom_url', 'notifications_enabled'
        )}),
        (_('Подписка'), {'fields': (
            'subscription_end_date',
        )}),
        (_('Права доступа'), {'fields': (
            'user_type', 'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    inlines = [SkillInline]
    
    def has_active_subscription(self, obj):
        """Отображает статус подписки пользователя в админке"""
        return obj.has_active_subscription()
    has_active_subscription.boolean = True
    has_active_subscription.short_description = _('Активная подписка')


class PortfolioThemeAdmin(admin.ModelAdmin):
    """Админка для тем портфолио"""
    list_display = ('name', 'type', 'primary_color', 'is_premium')
    list_filter = ('type', 'is_premium')
    search_fields = ('name',)


class PortfolioSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек портфолио"""
    list_display = ('user', 'theme', 'layout')
    list_filter = ('layout', 'show_skills', 'show_certificates', 'show_achievements')
    search_fields = ('user__username', 'user__email')


class ResumeTemplateAdmin(admin.ModelAdmin):
    """Админка для шаблонов резюме"""
    list_display = ('name', 'template_type', 'color_scheme', 'is_premium', 'created_at')
    list_filter = ('template_type', 'color_scheme', 'is_premium')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'


class UserResumeSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек резюме пользователя"""
    list_display = ('user', 'template', 'show_skills', 'show_projects', 'show_certificates')
    list_filter = ('show_skills', 'show_projects', 'show_certificates', 'show_achievements')
    search_fields = ('user__username', 'user__email')


class SubscriptionCodeAdmin(admin.ModelAdmin):
    """Админка для кодов подписки"""
    list_display = ('code', 'duration_days', 'is_used', 'used_by', 'created_at', 'used_at')
    list_filter = ('is_used', 'duration_days')
    search_fields = ('code', 'used_by__username')
    readonly_fields = ('used_by', 'used_at')
    

class ProfileViewAdmin(admin.ModelAdmin):
    """Админка для просмотров профиля"""
    list_display = ('profile', 'viewer', 'ip_address', 'timestamp')
    list_filter = ('timestamp', 'profile')
    search_fields = ('profile__username', 'viewer__username', 'ip_address')
    date_hierarchy = 'timestamp'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(PortfolioTheme, PortfolioThemeAdmin)
admin.site.register(PortfolioSettings, PortfolioSettingsAdmin)
admin.site.register(SubscriptionCode, SubscriptionCodeAdmin)
admin.site.register(ProfileView, ProfileViewAdmin)
admin.site.register(ResumeTemplate, ResumeTemplateAdmin)
admin.site.register(UserResumeSettings, UserResumeSettingsAdmin)
