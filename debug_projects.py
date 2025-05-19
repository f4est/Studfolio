#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

from portfolio.models import Project
from users.models import CustomUser

def debug_projects():
    try:
        # Получаем пользователя test_user_7
        user = CustomUser.objects.get(username='test_user_7')
        print(f"Найден пользователь ID: {user.id}, имя: {user.get_full_name()}")
        
        # Получаем проекты пользователя
        projects = Project.objects.filter(user=user).order_by('-created_at')
        
        print(f"Всего проектов у пользователя: {projects.count()}")
        
        if not projects:
            print("У пользователя нет проектов")
            return
        
        # Выводим информацию о каждом проекте
        for idx, project in enumerate(projects, 1):
            print(f"\nПроект #{idx}:")
            print(f"ID: {project.id}")
            print(f"Название: {project.title}")
            print(f"Описание: {project.description[:50]}...")
            print(f"Технологии: {project.technologies}")
            print(f"Изображение: {bool(project.image)}")
            print(f"Дата создания: {project.created_at}")
        
        # Проверяем, правильно ли работает related_name
        user_projects = user.projects.all()
        print(f"\nПолучено через related_name: {user_projects.count()} проектов")
        
    except CustomUser.DoesNotExist:
        print(f"Пользователь test_user_7 не найден")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    debug_projects() 