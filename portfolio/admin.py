from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Project, Certificate, Achievement, Review, ProjectPost, ProjectComment, ProjectView

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'technologies', 'start_date', 'end_date', 'is_featured')
    list_filter = ('is_featured', 'technologies')
    search_fields = ('title', 'description', 'technologies', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'issuer', 'issue_date', 'expiry_date')
    list_filter = ('issuer', 'issue_date')
    search_fields = ('title', 'description', 'issuer', 'user__username')
    date_hierarchy = 'issue_date'

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'organizer', 'date', 'place')
    list_filter = ('organizer', 'date')
    search_fields = ('title', 'description', 'organizer', 'user__username')
    date_hierarchy = 'date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'reviewer', 'project', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    search_fields = ('text', 'student__username', 'reviewer__username')
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _('Одобрено %(count)d отзывов.') % {'count': updated})
    approve_reviews.short_description = _('Одобрить выбранные отзывы')
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _('Отклонено %(count)d отзывов.') % {'count': updated})
    disapprove_reviews.short_description = _('Отклонить выбранные отзывы')

class ProjectViewAdmin(admin.ModelAdmin):
    """Админка для просмотров проектов"""
    list_display = ('project', 'viewer', 'ip_address', 'timestamp')
    list_filter = ('timestamp', 'project')
    search_fields = ('project__title', 'viewer__username', 'ip_address')
    date_hierarchy = 'timestamp'

admin.site.register(ProjectView, ProjectViewAdmin)
