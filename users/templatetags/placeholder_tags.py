# Template tags для заглушек изображений
# Автоматически сгенерирован скриптом apply_placeholders.py

from django import template
from django.templatetags.static import static
from django.conf import settings

register = template.Library()

@register.filter
def placeholder_or_image(image_field, placeholder_type):
    """
    Проверяет наличие изображения и возвращает URL изображения или заглушки
    Использование: {{ user.profile_image|placeholder_or_image:"avatar" }}
    """
    if image_field and hasattr(image_field, 'url'):
        return image_field.url
    
    placeholders = {
        'avatar': 'img/placeholders/avatars/default.jpg',
        'avatar_small': 'img/placeholders/avatars/small.jpg',
        'avatar_large': 'img/placeholders/avatars/large.jpg',
        'project': 'img/placeholders/projects/default.jpg',
        'project_thumb': 'img/placeholders/projects/thumbnail.jpg',
        'certificate': 'img/placeholders/certificates/default.jpg',
        'certificate_thumb': 'img/placeholders/certificates/thumbnail.jpg',
        'achievement': 'img/placeholders/achievements/default.jpg',
        'achievement_small': 'img/placeholders/achievements/small.jpg',
    }
    
    return static(placeholders.get(placeholder_type, placeholders['avatar']))

@register.filter
def random_placeholder(placeholder_type):
    """
    Возвращает случайную заглушку указанного типа
    Использование: {{ "project"|random_placeholder }}
    """
    import random
    
    placeholders = {
        'avatar': [f'img/placeholders/avatars/avatar{i}.jpg' for i in range(1, 6)],
        'project': [f'img/placeholders/projects/project{i}.jpg' for i in range(1, 6)],
        'certificate': [f'img/placeholders/certificates/certificate{i}.jpg' for i in range(1, 6)],
        'achievement': [f'img/placeholders/achievements/achievement{i}.jpg' for i in range(1, 6)],
    }
    
    if placeholder_type in placeholders:
        return static(random.choice(placeholders[placeholder_type]))
    
    # Возвращаем стандартную заглушку
    default_placeholders = {
        'avatar': 'img/placeholders/avatars/default.jpg',
        'project': 'img/placeholders/projects/default.jpg',
        'certificate': 'img/placeholders/certificates/default.jpg',
        'achievement': 'img/placeholders/achievements/default.jpg',
    }
    
    return static(default_placeholders.get(placeholder_type, default_placeholders['avatar']))
