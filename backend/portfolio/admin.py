from django.contrib import admin
from .models import (
    Portfolio, 
    AboutSection, 
    Education, 
    Skill, 
    Project, 
    Certificate, 
    PortfolioComment
)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_public', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    list_filter = ('is_public', 'created_at')


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'updated_at')
    search_fields = ('portfolio__user__username', 'content')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'institution', 'degree', 'start_date', 'end_date', 'is_current')
    search_fields = ('portfolio__user__username', 'institution', 'degree')
    list_filter = ('is_current', 'start_date')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'name', 'level', 'category')
    search_fields = ('portfolio__user__username', 'name', 'category')
    list_filter = ('level', 'category')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'title', 'start_date', 'end_date', 'is_ongoing')
    search_fields = ('portfolio__user__username', 'title', 'description')
    list_filter = ('is_ongoing', 'start_date')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'title', 'issuer', 'issue_date', 'expiration_date')
    search_fields = ('portfolio__user__username', 'title', 'issuer', 'credential_id')
    list_filter = ('issue_date', 'issuer')


@admin.register(PortfolioComment)
class PortfolioCommentAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'author', 'section', 'rating', 'created_at')
    search_fields = ('portfolio__user__username', 'author__username', 'text')
    list_filter = ('section', 'rating', 'created_at') 