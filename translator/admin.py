from django.contrib import admin
from .models import TranslationCache, AutoTranslatedContent


@admin.register(TranslationCache)
class TranslationCacheAdmin(admin.ModelAdmin):
    list_display = ['id', 'source_language', 'target_language', 'short_source_text', 'created_at']
    list_filter = ['source_language', 'target_language', 'created_at']
    search_fields = ['source_text', 'translated_text']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def short_source_text(self, obj):
        """Сокращенный исходный текст для отображения в списке"""
        if len(obj.source_text) > 50:
            return obj.source_text[:50] + '...'
        return obj.source_text
    
    short_source_text.short_description = 'Исходный текст'


@admin.register(AutoTranslatedContent)
class AutoTranslatedContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_type', 'object_id', 'field_name', 'source_language', 'last_updated']
    list_filter = ['content_type', 'source_language', 'last_updated']
    search_fields = ['content_type', 'object_id', 'field_name']
    readonly_fields = ['last_updated']
    date_hierarchy = 'last_updated'
