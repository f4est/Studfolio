#!/usr/bin/env python
"""
Скрипт для проверки и исправления проблем с отсутствующими изображениями
Анализирует базу данных и файловую систему, чтобы заменить отсутствующие изображения на заглушки
"""

import os
import sys
import django
from pathlib import Path

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import FileField, ImageField
from django.apps import apps
from users.models import CustomUser, Project, Certificate, Achievement
from users.placeholders import (
    DEFAULT_PROFILE_IMAGE, DEFAULT_PROJECT_IMAGE, DEFAULT_PROJECT_THUMBNAIL,
    DEFAULT_CERTIFICATE_IMAGE, DEFAULT_CERTIFICATE_THUMBNAIL,
    DEFAULT_ACHIEVEMENT_IMAGE, DEFAULT_ACHIEVEMENT_SMALL
)
import shutil

def is_image_exists(path):
    """Проверяет, существует ли изображение в файловой системе"""
    if not path:
        return False
    
    # Преобразуем относительный путь в абсолютный
    full_path = Path(settings.MEDIA_ROOT) / path
    return full_path.exists() and full_path.is_file()

def copy_placeholder(placeholder_path, destination_path):
    """Копирует заглушку в нужную директорию"""
    placeholder_full_path = Path(settings.MEDIA_ROOT) / placeholder_path
    destination_full_path = Path(settings.MEDIA_ROOT) / destination_path
    
    # Убедимся, что директория назначения существует
    destination_full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Копируем заглушку
    try:
        shutil.copy2(placeholder_full_path, destination_full_path)
        return True
    except Exception as e:
        print(f"Ошибка копирования заглушки: {e}")
        return False

def fix_user_profile_images():
    """Исправляет отсутствующие изображения профилей пользователей"""
    print("\n[Проверка изображений профилей пользователей]")
    
    users = CustomUser.objects.all()
    fixed_count = 0
    
    for user in users:
        if not user.profile_image or not is_image_exists(str(user.profile_image)):
            # Путь для новой заглушки
            profile_image_path = f"profile_images/{user.username}_default.jpg"
            
            # Копируем заглушку
            if copy_placeholder(DEFAULT_PROFILE_IMAGE, profile_image_path):
                # Обновляем объект пользователя
                user.profile_image = profile_image_path
                user.save(update_fields=['profile_image'])
                fixed_count += 1
                print(f"  ✓ Исправлено изображение профиля для пользователя {user.username}")
    
    print(f"Всего исправлено профилей пользователей: {fixed_count}/{users.count()}")

def fix_project_images():
    """Исправляет отсутствующие изображения проектов"""
    print("\n[Проверка изображений проектов]")
    
    projects = Project.objects.all()
    fixed_count = 0
    
    for project in projects:
        if not project.image or not is_image_exists(str(project.image)):
            # Путь для новой заглушки
            project_image_path = f"project_images/project_{project.id}_default.jpg"
            
            # Копируем заглушку
            if copy_placeholder(DEFAULT_PROJECT_IMAGE, project_image_path):
                # Обновляем объект проекта
                project.image = project_image_path
                project.save(update_fields=['image'])
                fixed_count += 1
                print(f"  ✓ Исправлено изображение для проекта {project.title}")
    
    print(f"Всего исправлено изображений проектов: {fixed_count}/{projects.count()}")

def fix_certificate_images():
    """Исправляет отсутствующие изображения сертификатов"""
    print("\n[Проверка изображений сертификатов]")
    
    certificates = Certificate.objects.all()
    fixed_count = 0
    
    for certificate in certificates:
        if not certificate.image or not is_image_exists(str(certificate.image)):
            # Путь для новой заглушки
            certificate_image_path = f"certificates/certificate_{certificate.id}_default.jpg"
            
            # Копируем заглушку
            if copy_placeholder(DEFAULT_CERTIFICATE_IMAGE, certificate_image_path):
                # Обновляем объект сертификата
                certificate.image = certificate_image_path
                certificate.save(update_fields=['image'])
                fixed_count += 1
                print(f"  ✓ Исправлено изображение для сертификата {certificate.title}")
    
    print(f"Всего исправлено изображений сертификатов: {fixed_count}/{certificates.count()}")

def fix_achievement_images():
    """Исправляет отсутствующие изображения достижений"""
    print("\n[Проверка изображений достижений]")
    
    achievements = Achievement.objects.all()
    fixed_count = 0
    
    for achievement in achievements:
        if not achievement.image or not is_image_exists(str(achievement.image)):
            # Путь для новой заглушки
            achievement_image_path = f"achievements/achievement_{achievement.id}_default.jpg"
            
            # Копируем заглушку
            if copy_placeholder(DEFAULT_ACHIEVEMENT_IMAGE, achievement_image_path):
                # Обновляем объект достижения
                achievement.image = achievement_image_path
                achievement.save(update_fields=['image'])
                fixed_count += 1
                print(f"  ✓ Исправлено изображение для достижения {achievement.title}")
    
    print(f"Всего исправлено изображений достижений: {fixed_count}/{achievements.count()}")

def fix_all_model_images():
    """Проверяет все модели проекта на наличие полей с изображениями и исправляет отсутствующие"""
    print("\n[Проверка всех моделей с изображениями]")
    
    # Счетчики
    total_models_checked = 0
    total_fields_checked = 0
    total_images_fixed = 0
    
    # Перебираем все модели в проекте
    for model in apps.get_models():
        # Пропускаем уже обработанные модели
        if model in [CustomUser, Project, Certificate, Achievement]:
            continue
        
        # Ищем поля типа ImageField и FileField
        image_fields = []
        for field in model._meta.fields:
            if isinstance(field, (ImageField, FileField)):
                image_fields.append(field.name)
        
        if not image_fields:
            continue
        
        total_models_checked += 1
        print(f"  Проверка модели {model.__name__}...")
        
        # Проверяем каждый объект модели
        objects = model.objects.all()
        for obj in objects:
            for field_name in image_fields:
                total_fields_checked += 1
                field_value = getattr(obj, field_name)
                
                if not field_value or not is_image_exists(str(field_value)):
                    # Определяем тип заглушки по имени поля
                    if 'avatar' in field_name or 'profile' in field_name or 'user_image' in field_name:
                        placeholder_path = DEFAULT_PROFILE_IMAGE
                    elif 'project' in field_name:
                        placeholder_path = DEFAULT_PROJECT_IMAGE
                    elif 'certificate' in field_name:
                        placeholder_path = DEFAULT_CERTIFICATE_IMAGE
                    elif 'achievement' in field_name:
                        placeholder_path = DEFAULT_ACHIEVEMENT_IMAGE
                    else:
                        placeholder_path = DEFAULT_PROJECT_IMAGE  # Универсальная заглушка
                    
                    # Создаем путь для заглушки
                    field_dir = model.__name__.lower()
                    new_path = f"{field_dir}/{field_name}_{obj.pk}_default.jpg"
                    
                    # Копируем заглушку
                    if copy_placeholder(placeholder_path, new_path):
                        setattr(obj, field_name, new_path)
                        obj.save(update_fields=[field_name])
                        total_images_fixed += 1
                        print(f"    ✓ Исправлено изображение {field_name} для {model.__name__} #{obj.pk}")
    
    print(f"Всего проверено моделей: {total_models_checked}")
    print(f"Всего проверено полей: {total_fields_checked}")
    print(f"Всего исправлено изображений: {total_images_fixed}")

def main():
    """Главная функция скрипта"""
    print("=" * 60)
    print("   ПРОВЕРКА И ИСПРАВЛЕНИЕ ОТСУТСТВУЮЩИХ ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    
    # Исправляем изображения для основных моделей
    fix_user_profile_images()
    fix_project_images()
    fix_certificate_images()
    fix_achievement_images()
    
    # Проверяем все остальные модели
    fix_all_model_images()
    
    print("\n" + "=" * 60)
    print("   ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 60)

if __name__ == "__main__":
    main() 