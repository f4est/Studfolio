import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

from users.models import CustomUser, Project, Certificate, Achievement
from django.db import models
from pathlib import Path
from users.placeholders import (
    DEFAULT_PROFILE_IMAGE, DEFAULT_PROJECT_IMAGE, DEFAULT_PROJECT_THUMBNAIL,
    DEFAULT_CERTIFICATE_IMAGE, DEFAULT_CERTIFICATE_THUMBNAIL,
    DEFAULT_ACHIEVEMENT_IMAGE, DEFAULT_ACHIEVEMENT_SMALL
)

def update_profile_image_field():
    """Обновляет поле profile_image в модели CustomUser"""
    print("Обновление поля profile_image в модели CustomUser...")
    
    # Проверяем, есть ли уже значение по умолчанию
    field = CustomUser._meta.get_field('profile_image')
    
    if not field.has_default():
        # Добавляем значение по умолчанию для поля
        field.default = DEFAULT_PROFILE_IMAGE
        print(f"Добавлено значение по умолчанию: {DEFAULT_PROFILE_IMAGE}")
    else:
        print(f"Поле уже имеет значение по умолчанию: {field.default}")
    
    # Обновляем пользователей без аватарок
    users_without_avatar = CustomUser.objects.filter(profile_image='')
    count = users_without_avatar.count()
    
    if count > 0:
        print(f"Найдено {count} пользователей без аватарок. Обновляем...")
        for user in users_without_avatar:
            user.profile_image = DEFAULT_PROFILE_IMAGE
            user.save(update_fields=['profile_image'])
        print("Пользователи обновлены.")
    else:
        print("Нет пользователей без аватарок.")

def update_project_image_fields():
    """Обновляет поля изображений в модели Project"""
    print("\nОбновление полей изображений в модели Project...")
    
    # Проверяем, есть ли уже значения по умолчанию
    image_field = Project._meta.get_field('image')
    
    if not image_field.has_default():
        image_field.default = DEFAULT_PROJECT_IMAGE
        print(f"Добавлено значение по умолчанию для image: {DEFAULT_PROJECT_IMAGE}")
    else:
        print(f"Поле image уже имеет значение по умолчанию: {image_field.default}")
    
    # Обновляем проекты без изображений
    projects_without_image = Project.objects.filter(image='')
    count_image = projects_without_image.count()
    
    if count_image > 0:
        print(f"Найдено {count_image} проектов без изображений. Обновляем...")
        for project in projects_without_image:
            project.image = DEFAULT_PROJECT_IMAGE
            project.save(update_fields=['image'])
        print("Проекты обновлены.")
    else:
        print("Нет проектов без изображений.")

def update_certificate_image_fields():
    """Обновляет поля изображений в модели Certificate"""
    print("\nОбновление полей изображений в модели Certificate...")
    
    # Проверяем, есть ли уже значения по умолчанию
    image_field = Certificate._meta.get_field('image')
    
    if not image_field.has_default():
        image_field.default = DEFAULT_CERTIFICATE_IMAGE
        print(f"Добавлено значение по умолчанию для image: {DEFAULT_CERTIFICATE_IMAGE}")
    else:
        print(f"Поле image уже имеет значение по умолчанию: {image_field.default}")
    
    # Обновляем сертификаты без изображений
    certificates_without_image = Certificate.objects.filter(image='')
    count_image = certificates_without_image.count()
    
    if count_image > 0:
        print(f"Найдено {count_image} сертификатов без изображений. Обновляем...")
        for certificate in certificates_without_image:
            certificate.image = DEFAULT_CERTIFICATE_IMAGE
            certificate.save(update_fields=['image'])
        print("Сертификаты обновлены.")
    else:
        print("Нет сертификатов без изображений.")

def update_achievement_image_fields():
    """Обновляет поля изображений в модели Achievement"""
    print("\nОбновление полей изображений в модели Achievement...")
    
    # Проверяем, есть ли уже значения по умолчанию
    image_field = Achievement._meta.get_field('image')
    
    if not image_field.has_default():
        image_field.default = DEFAULT_ACHIEVEMENT_IMAGE
        print(f"Добавлено значение по умолчанию для image: {DEFAULT_ACHIEVEMENT_IMAGE}")
    else:
        print(f"Поле image уже имеет значение по умолчанию: {image_field.default}")
    
    # Обновляем достижения без изображений
    achievements_without_image = Achievement.objects.filter(image='')
    count_image = achievements_without_image.count()
    
    if count_image > 0:
        print(f"Найдено {count_image} достижений без изображений. Обновляем...")
        for achievement in achievements_without_image:
            achievement.image = DEFAULT_ACHIEVEMENT_IMAGE
            achievement.save(update_fields=['image'])
        print("Достижения обновлены.")
    else:
        print("Нет достижений без изображений.")

if __name__ == "__main__":
    print("Запуск обновления моделей для использования заглушек...")
    
    # Обновляем модели
    update_profile_image_field()
    update_project_image_fields()
    update_certificate_image_fields()
    update_achievement_image_fields()
    
    print("\nОбновление моделей завершено!") 