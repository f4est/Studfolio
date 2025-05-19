#!/usr/bin/env python
"""
Скрипт для создания тем портфолио из JSON файла.
Используйте этот скрипт для восстановления тем после сбоев.
"""

import os
import sys
import json
import django

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

from users.models import PortfolioTheme

def load_json_data(file_path):
    """Загружает данные из JSON файла"""
    encodings = ['utf-8', 'utf-16le', 'utf-16be', 'cp1251']
    
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return None
        
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Ошибка при чтении файла {file_path} с кодировкой {encoding}: {e}")
            continue
    
    # Если все кодировки не подошли, создаем новый файл
    try:
        print(f"Не удалось прочитать файл {file_path}. Создаем новый файл...")
        create_new_portfolio_themes_file()
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Не удалось создать новый файл: {e}")
        return None

def create_new_portfolio_themes_file():
    """Создает новый файл с темами портфолио"""
    themes_data = [
        {
            "model": "users.portfoliotheme",
            "pk": 1,
            "fields": {
                "name": "Светлая",
                "description": "Светлая тема с голубым акцентом",
                "is_premium": False,
                "preview_image": "",
                "created_at": "2023-01-01T00:00:00Z"
            }
        },
        {
            "model": "users.portfoliotheme",
            "pk": 2,
            "fields": {
                "name": "Темная",
                "description": "Темная тема для снижения нагрузки на глаза",
                "is_premium": False,
                "preview_image": "",
                "created_at": "2023-01-01T00:00:00Z"
            }
        },
        {
            "model": "users.portfoliotheme",
            "pk": 3,
            "fields": {
                "name": "Минималистичная",
                "description": "Минималистичная тема с акцентом на содержание",
                "is_premium": True,
                "preview_image": "",
                "created_at": "2023-01-01T00:00:00Z"
            }
        },
        {
            "model": "users.portfoliotheme",
            "pk": 4,
            "fields": {
                "name": "Креативная",
                "description": "Яркая креативная тема для творческих профессий",
                "is_premium": True,
                "preview_image": "",
                "created_at": "2023-01-01T00:00:00Z"
            }
        },
        {
            "model": "users.portfoliotheme",
            "pk": 5,
            "fields": {
                "name": "Профессиональная",
                "description": "Строгая профессиональная тема для делового использования",
                "is_premium": True,
                "preview_image": "",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
    ]
    
    with open('portfolio_themes.json', 'w', encoding='utf-8') as f:
        json.dump(themes_data, f, ensure_ascii=False, indent=2)

def create_portfolio_themes():
    """Создает темы портфолио из JSON файла"""
    data = load_json_data('portfolio_themes.json')
    if not data:
        return False
        
    # Проверяем, есть ли уже темы
    existing_count = PortfolioTheme.objects.count()
    if existing_count > 0:
        print("Темы портфолио уже существуют. Очищаем и создаем новые...")
        PortfolioTheme.objects.all().delete()
    
    # Создаем новые темы
    themes_created = 0
    for item in data:
        fields = item['fields']
        try:
            theme = PortfolioTheme(
                id=item['pk'],
                name=fields['name'],
                description=fields.get('description', ''),
                is_premium=fields.get('is_premium', False),
                preview_image=fields.get('preview_image', '')
            )
            theme.save()
            themes_created += 1
        except Exception as e:
            print(f"Ошибка при создании темы портфолио: {e}")
    
    print(f"Создано {themes_created} тем портфолио")
    return themes_created > 0

if __name__ == "__main__":
    success = True
    
    if not create_portfolio_themes():
        success = False
        print("Ошибка при создании тем портфолио")
    
    if success:
        print("Готово! Темы портфолио успешно созданы.")
    else:
        print("Возникли ошибки при создании тем.") 