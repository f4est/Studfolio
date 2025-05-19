# Context processors для заглушек изображений
# Автоматически сгенерирован скриптом apply_placeholders.py

from django.templatetags.static import static
from .placeholders import STATIC_PLACEHOLDER_PATH

def placeholder_images(request):
    """Добавляет пути к заглушкам изображений в контекст шаблонов"""
    return {
        'placeholder_images': {
            'avatar': static(STATIC_PLACEHOLDER_PATH + 'avatars/default.jpg'),
            'avatar_small': static(STATIC_PLACEHOLDER_PATH + 'avatars/small.jpg'),
            'avatar_large': static(STATIC_PLACEHOLDER_PATH + 'avatars/large.jpg'),
            'project': static(STATIC_PLACEHOLDER_PATH + 'projects/default.jpg'),
            'project_thumb': static(STATIC_PLACEHOLDER_PATH + 'projects/thumbnail.jpg'),
            'certificate': static(STATIC_PLACEHOLDER_PATH + 'certificates/default.jpg'),
            'certificate_thumb': static(STATIC_PLACEHOLDER_PATH + 'certificates/thumbnail.jpg'),
            'achievement': static(STATIC_PLACEHOLDER_PATH + 'achievements/default.jpg'),
            'achievement_small': static(STATIC_PLACEHOLDER_PATH + 'achievements/small.jpg'),
        }
    }
