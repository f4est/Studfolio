#!/usr/bin/env python
import os
import django

# Установка переменной окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

from users.models import ResumeTemplate, PortfolioTheme
from django.core.files.base import ContentFile
import random

# Проверяем импорт WeasyPrint и исправляем файл views.py
def fix_weasyprint_import():
    views_file_path = 'users/views.py'
    
    # Проверяем файл и вносим изменения
    with open(views_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Заменяем код импорта WeasyPrint
    fixed_content = content.replace(
        """# Импортируем WeasyPrint, но обрабатываем ошибку импорта
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False""",
        """# Импортируем WeasyPrint, но обрабатываем ошибку импорта
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML, CSS
    # Проверяем правильность загрузки библиотек с надежным обходом ошибок
    try:
        # Пустой HTML для тестирования
        test_html = HTML(string='<html><body>Test</body></html>')
        # Если дошли до этой точки без исключений, все работает
        WEASYPRINT_AVAILABLE = True
    except Exception as e:
        print(f"WeasyPrint доступен, но не может быть использован: {str(e)}")
        WEASYPRINT_AVAILABLE = False
except ImportError:
    print("WeasyPrint не установлен или не может быть импортирован")
    WEASYPRINT_AVAILABLE = False""")
    
    # Сохраняем изменения
    with open(views_file_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)
    
    print("Исправлен импорт WeasyPrint в файле users/views.py")
    

# Создаем базовые шаблоны резюме
def create_resume_templates():
    # Проверяем, существуют ли уже шаблоны
    if ResumeTemplate.objects.exists():
        print("Шаблоны резюме уже существуют. Очищаем и создаем новые...")
        ResumeTemplate.objects.all().delete()
    
    # Базовый шаблон (синий)
    basic_template = ResumeTemplate(
        name="Базовый шаблон",
        description="Простой и элегантный базовый шаблон для вашего резюме",
        template_type="basic",
        color_scheme="blue",
        primary_color="#3498db",
        secondary_color="#2c3e50",
        is_premium=False
    )
    basic_template.save()
    
    # Профессиональный шаблон (черно-белый)
    professional_template = ResumeTemplate(
        name="Профессиональный",
        description="Строгий профессиональный шаблон для бизнес-среды",
        template_type="professional",
        color_scheme="black",
        primary_color="#333333",
        secondary_color="#555555",
        is_premium=True
    )
    professional_template.save()
    
    # Креативный шаблон (зеленый)
    creative_template = ResumeTemplate(
        name="Креативный",
        description="Яркий и творческий шаблон для выделения вашего резюме",
        template_type="creative",
        color_scheme="green",
        primary_color="#27ae60",
        secondary_color="#2ecc71",
        is_premium=True
    )
    creative_template.save()
    
    # Академический шаблон (фиолетовый)
    academic_template = ResumeTemplate(
        name="Академический",
        description="Формальный шаблон для академической среды",
        template_type="academic",
        color_scheme="purple",
        primary_color="#8e44ad",
        secondary_color="#9b59b6",
        is_premium=True
    )
    academic_template.save()
    
    print(f"Создано {ResumeTemplate.objects.count()} шаблонов резюме")


# Создаем базовые темы портфолио
def create_portfolio_themes():
    # Проверяем, существуют ли уже темы
    if PortfolioTheme.objects.exists():
        print("Темы портфолио уже существуют. Очищаем и создаем новые...")
        PortfolioTheme.objects.all().delete()
    
    # Светлая тема
    light_theme = PortfolioTheme(
        name="Светлая",
        type="light",
        primary_color="#007bff",
        secondary_color="#6c757d",
        background_color="#ffffff",
        text_color="#333333",
        is_premium=False
    )
    light_theme.save()
    
    # Темная тема
    dark_theme = PortfolioTheme(
        name="Темная",
        type="dark",
        primary_color="#17a2b8",
        secondary_color="#343a40",
        background_color="#212529",
        text_color="#f8f9fa",
        is_premium=False
    )
    dark_theme.save()
    
    # Минималистичная тема
    minimal_theme = PortfolioTheme(
        name="Минималистичная",
        type="minimalist",
        primary_color="#495057",
        secondary_color="#adb5bd",
        background_color="#f8f9fa",
        text_color="#212529",
        is_premium=True
    )
    minimal_theme.save()
    
    # Креативная тема
    creative_theme = PortfolioTheme(
        name="Креативная",
        type="creative",
        primary_color="#e83e8c",
        secondary_color="#fd7e14",
        background_color="#ffffff",
        text_color="#212529",
        is_premium=True
    )
    creative_theme.save()
    
    # Профессиональная тема
    professional_theme = PortfolioTheme(
        name="Профессиональная",
        type="professional",
        primary_color="#28a745",
        secondary_color="#20c997",
        background_color="#f8f9fa",
        text_color="#343a40",
        is_premium=True
    )
    professional_theme.save()
    
    print(f"Создано {PortfolioTheme.objects.count()} тем портфолио")


if __name__ == "__main__":
    print("Начинаем исправление проблем с шаблонами и WeasyPrint...")
    
    # Исправляем импорт WeasyPrint
    fix_weasyprint_import()
    
    # Создаем шаблоны резюме
    create_resume_templates()
    
    # Создаем темы портфолио
    create_portfolio_themes()
    
    print("Готово! Проблемы исправлены, шаблоны и темы созданы.") 