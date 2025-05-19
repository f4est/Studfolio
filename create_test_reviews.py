#!/usr/bin/env python
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

from users.models import CustomUser
from portfolio.models import Review, Project

def create_test_reviews():
    print("Начинаем создание тестовых отзывов...")
    
    # Получаем нужных пользователей
    try:
        student = CustomUser.objects.get(username='test_user_7')
        print(f"Найден студент: {student.username}")
        
        teachers = CustomUser.objects.filter(user_type='teacher')
        if not teachers:
            print("Не найдено преподавателей, создаём тестового преподавателя")
            teacher = CustomUser.objects.create_user(
                username='test_teacher',
                password='testpass123',
                email='test_teacher@example.com',
                first_name='Тестовый',
                last_name='Преподаватель',
                user_type='teacher',
                is_public=True
            )
            teachers = [teacher]
        
        # Получаем проекты студента
        projects = Project.objects.filter(user=student)
        if not projects:
            print("У студента нет проектов, создаём тестовый проект")
            project = Project.objects.create(
                user=student,
                title="Тестовый проект",
                description="Описание тестового проекта",
                technologies="Python, Django",
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now(),
                is_featured=True
            )
            projects = [project]
        
        # Удаляем существующие отзывы для этого студента
        existing_reviews = Review.objects.filter(student=student)
        if existing_reviews:
            count = existing_reviews.count()
            existing_reviews.delete()
            print(f"Удалено {count} существующих отзывов")
        
        # Создаём новые отзывы
        reviews_texts = [
            "Отличная работа! Студент проявил инициативу и творческий подход.",
            "Хороший проект, но есть некоторые недоработки в дизайне.",
            "Проект выполнен на высоком уровне, все требования учтены.",
            "Интересное решение, но нужно доработать документацию.",
            "Превосходная работа с использованием современных технологий."
        ]
        
        review_count = 0
        # Создаём по 2 отзыва от каждого преподавателя
        for teacher in teachers:
            # Один отзыв без проекта (общий)
            review = Review.objects.create(
                student=student,
                reviewer=teacher,
                project=None,
                text=random.choice(reviews_texts) + " Общий отзыв.",
                rating=random.randint(3, 5),
                is_approved=True
            )
            review_count += 1
            
            # Один отзыв к конкретному проекту
            if projects:
                review = Review.objects.create(
                    student=student,
                    reviewer=teacher,
                    project=random.choice(projects),
                    text=random.choice(reviews_texts) + " Отзыв к проекту.",
                    rating=random.randint(3, 5),
                    is_approved=True
                )
                review_count += 1
        
        print(f"Создано {review_count} новых отзывов для студента {student.username}")
        
    except CustomUser.DoesNotExist:
        print("Пользователь test_user_7 не найден!")
    except Exception as e:
        print(f"Ошибка при создании отзывов: {e}")

if __name__ == "__main__":
    create_test_reviews() 