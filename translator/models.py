from django.db import models
from django.conf import settings


class TranslationCache(models.Model):
    """
    Кэш переводов для избежания повторных запросов к API перевода
    """
    source_text = models.TextField(verbose_name="Исходный текст")
    source_language = models.CharField(max_length=10, verbose_name="Исходный язык")
    target_language = models.CharField(max_length=10, verbose_name="Целевой язык")
    translated_text = models.TextField(verbose_name="Переведенный текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Кэш перевода"
        verbose_name_plural = "Кэш переводов"
        unique_together = [['source_text', 'source_language', 'target_language']]
        indexes = [
            models.Index(fields=['source_language', 'target_language']),
        ]
    
    def __str__(self):
        return f"{self.source_language} → {self.target_language}: {self.source_text[:50]}..."


class AutoTranslatedContent(models.Model):
    """
    Модель для хранения автоматически переведенного контента
    """
    content_type = models.CharField(max_length=100, verbose_name="Тип контента")
    object_id = models.PositiveIntegerField(verbose_name="ID объекта")
    field_name = models.CharField(max_length=100, verbose_name="Название поля")
    source_language = models.CharField(max_length=10, verbose_name="Исходный язык")
    translations = models.JSONField(verbose_name="Переводы", default=dict)
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
    
    class Meta:
        verbose_name = "Автоматический перевод"
        verbose_name_plural = "Автоматические переводы"
        unique_together = [['content_type', 'object_id', 'field_name', 'source_language']]
    
    def __str__(self):
        return f"{self.content_type} #{self.object_id}.{self.field_name}"
