import os
import shutil
from pathlib import Path
import random

def ensure_dir(directory):
    """Убедиться, что директория существует"""
    os.makedirs(directory, exist_ok=True)
    return directory

def copy_with_message(src, dst):
    """Копировать файл с выводом сообщения"""
    if not Path(src).exists():
        print(f"Ошибка: Исходный файл {src} не найден")
        return False
    
    ensure_dir(Path(dst).parent)
    shutil.copy2(src, dst)
    print(f"Файл скопирован: {src} -> {dst}")
    return True

def main():
    # Основные директории
    placeholders_dir = Path('media/placeholders')
    
    # Директории для целевых файлов
    profile_images_dir = Path('media/profile_images')
    achievements_dir = Path('media/achievements')  
    certificates_dir = Path('media/certificates')
    project_images_dir = Path('media/project_images')
    static_dir = Path('static/img')
    
    # Убедитесь, что все директории существуют
    ensure_dir(profile_images_dir)
    ensure_dir(achievements_dir)
    ensure_dir(certificates_dir)
    ensure_dir(project_images_dir)
    ensure_dir(static_dir)
    
    # Копирование заглушек для аватарок в media/profile_images
    copy_with_message(
        placeholders_dir / 'avatars' / 'default.jpg',
        profile_images_dir / 'default.jpg'
    )
    copy_with_message(
        placeholders_dir / 'avatars' / 'large.jpg',
        profile_images_dir / 'default_large.jpg'
    )
    copy_with_message(
        placeholders_dir / 'avatars' / 'small.jpg',
        profile_images_dir / 'default_small.jpg'
    )
    
    # Копируем несколько аватарок с разными именами для тестирования
    for i in range(1, 6):
        copy_with_message(
            placeholders_dir / 'avatars' / f'avatar{i}.jpg',
            profile_images_dir / f'test_user{i}.jpg'
        )
    
    # Копирование заглушек для достижений
    copy_with_message(
        placeholders_dir / 'achievements' / 'default.jpg',
        achievements_dir / 'default.jpg'
    )
    copy_with_message(
        placeholders_dir / 'achievements' / 'small.jpg',
        achievements_dir / 'default_small.jpg'
    )
    
    # Копируем несколько достижений с разными именами
    for i in range(1, 6):
        copy_with_message(
            placeholders_dir / 'achievements' / f'achievement{i}.jpg',
            achievements_dir / f'achievement_example{i}.jpg'
        )
        copy_with_message(
            placeholders_dir / 'achievements' / f'achievement{i}_small.jpg',
            achievements_dir / f'achievement_example{i}_small.jpg'
        )
    
    # Копирование заглушек для сертификатов
    copy_with_message(
        placeholders_dir / 'certificates' / 'default.jpg',
        certificates_dir / 'default.jpg'
    )
    copy_with_message(
        placeholders_dir / 'certificates' / 'thumbnail.jpg',
        certificates_dir / 'default_thumbnail.jpg'
    )
    
    # Копируем несколько сертификатов с разными именами
    for i in range(1, 6):
        copy_with_message(
            placeholders_dir / 'certificates' / f'certificate{i}.jpg',
            certificates_dir / f'certificate_example{i}.jpg'
        )
        copy_with_message(
            placeholders_dir / 'certificates' / f'certificate{i}_thumb.jpg',
            certificates_dir / f'certificate_example{i}_thumb.jpg'
        )
    
    # Копирование заглушек для проектов
    copy_with_message(
        placeholders_dir / 'projects' / 'default.jpg',
        project_images_dir / 'default.jpg'
    )
    copy_with_message(
        placeholders_dir / 'projects' / 'thumbnail.jpg',
        project_images_dir / 'default_thumbnail.jpg'
    )
    copy_with_message(
        placeholders_dir / 'projects' / 'banner.jpg',
        project_images_dir / 'default_banner.jpg'
    )
    
    # Копируем несколько проектов с разными именами
    for i in range(1, 6):
        copy_with_message(
            placeholders_dir / 'projects' / f'project{i}.jpg',
            project_images_dir / f'project_example{i}.jpg'
        )
        copy_with_message(
            placeholders_dir / 'projects' / f'project{i}_thumb.jpg',
            project_images_dir / f'project_example{i}_thumb.jpg'
        )
    
    # Копирование заглушек с разными цветами для проектов
    for i in range(1, 6):
        copy_with_message(
            placeholders_dir / 'projects' / f'colored_{i}.jpg',
            project_images_dir / f'colored_{i}.jpg'
        )
    
    # Копируем баннеры и логотипы в статические файлы
    ensure_dir(static_dir / 'banners')
    ensure_dir(static_dir / 'logos')
    ensure_dir(static_dir / 'icons')
    ensure_dir(static_dir / 'placeholders')
    
    # Копирование баннеров
    for size in ['small', 'medium', 'large']:
        copy_with_message(
            placeholders_dir / 'banners' / f'{size}.jpg',
            static_dir / 'banners' / f'banner_{size}.jpg'
        )
    
    # Копирование логотипов
    copy_with_message(
        placeholders_dir / 'logos' / 'default.png',
        static_dir / 'logos' / 'logo.png'
    )
    copy_with_message(
        placeholders_dir / 'logos' / 'small.png',
        static_dir / 'logos' / 'logo_small.png'
    )
    
    # Копирование иконок
    for size in ['small', 'default', 'large']:
        copy_with_message(
            placeholders_dir / 'icons' / f'{size}.png',
            static_dir / 'icons' / f'icon_{size}.png'
        )
    
    # Создаем копии в директории placeholders для использования в шаблонах
    for cat in ['avatars', 'projects', 'certificates', 'achievements']:
        src_dir = placeholders_dir / cat
        dst_dir = static_dir / 'placeholders' / cat
        ensure_dir(dst_dir)
        
        for file in src_dir.glob('*.*'):
            copy_with_message(file, dst_dir / file.name)
    
    print("\nВсе заглушки успешно скопированы в соответствующие директории!")
    print("Теперь вы можете заменить их своими реальными изображениями.")
    
    # Создаем константы для Django
    create_django_placeholders_constants()

def create_django_placeholders_constants():
    """Создаем файл с константами для Django"""
    constants_file = Path('users/placeholders.py')
    
    content = """# Файл с константами для заглушек изображений
# Автоматически сгенерирован скриптом apply_placeholders.py

# Пути к заглушкам для профильных изображений
DEFAULT_PROFILE_IMAGE = 'profile_images/default.jpg'
DEFAULT_PROFILE_IMAGE_LARGE = 'profile_images/default_large.jpg'
DEFAULT_PROFILE_IMAGE_SMALL = 'profile_images/default_small.jpg'

# Пути к заглушкам для проектов
DEFAULT_PROJECT_IMAGE = 'project_images/default.jpg'
DEFAULT_PROJECT_THUMBNAIL = 'project_images/default_thumbnail.jpg'
DEFAULT_PROJECT_BANNER = 'project_images/default_banner.jpg'

# Пути к заглушкам для сертификатов
DEFAULT_CERTIFICATE_IMAGE = 'certificates/default.jpg'
DEFAULT_CERTIFICATE_THUMBNAIL = 'certificates/default_thumbnail.jpg'

# Пути к заглушкам для достижений
DEFAULT_ACHIEVEMENT_IMAGE = 'achievements/default.jpg'
DEFAULT_ACHIEVEMENT_SMALL = 'achievements/default_small.jpg'

# Статические пути для использования в шаблонах
STATIC_PLACEHOLDER_PATH = 'img/placeholders/'
"""
    
    with open(constants_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Создан файл с константами: {constants_file}")
    
    # Создадим файл context_processors.py для использования заглушек в шаблонах
    create_context_processors()

def create_context_processors():
    """Создаем файл context_processors.py для использования заглушек в шаблонах"""
    context_processors_file = Path('users/context_processors.py')
    
    content = '''# Context processors для заглушек изображений
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
'''
    
    with open(context_processors_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Создан файл context_processors: {context_processors_file}")
    
    # Создадим template tag для удобного использования заглушек
    create_templatetag()

def create_templatetag():
    """Создаем template tag для использования заглушек в шаблонах"""
    templatetags_dir = Path('users/templatetags')
    ensure_dir(templatetags_dir)
    
    init_file = templatetags_dir / '__init__.py'
    if not init_file.exists():
        with open(init_file, 'w') as f:
            f.write('# Init file for templatetags package')
    
    placeholder_tags_file = templatetags_dir / 'placeholder_tags.py'
    
    content = '''# Template tags для заглушек изображений
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
'''
    
    with open(placeholder_tags_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Создан файл template tags: {placeholder_tags_file}")

if __name__ == "__main__":
    main() 