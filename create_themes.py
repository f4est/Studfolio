import os
import django

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

from users.models import PortfolioTheme

# Создаем базовые темы портфолио
themes = [
    {
        'name': 'Классическая светлая',
        'type': 'light',
        'primary_color': '#007bff',
        'secondary_color': '#6c757d',
        'background_color': '#ffffff',
        'text_color': '#212529',
        'is_premium': False
    },
    {
        'name': 'Классическая темная',
        'type': 'dark',
        'primary_color': '#375a7f',
        'secondary_color': '#444444',
        'background_color': '#222222',
        'text_color': '#ffffff',
        'is_premium': False
    },
    {
        'name': 'Минималистичная',
        'type': 'minimalist',
        'primary_color': '#000000',
        'secondary_color': '#555555',
        'background_color': '#ffffff',
        'text_color': '#000000',
        'is_premium': False
    },
    {
        'name': 'Креативная цветная',
        'type': 'colorful',
        'primary_color': '#ff4081',
        'secondary_color': '#7c4dff',
        'background_color': '#f5f5f5',
        'text_color': '#424242',
        'is_premium': False
    },
    {
        'name': 'Профессиональная синяя',
        'type': 'professional',
        'primary_color': '#1565c0',
        'secondary_color': '#0d47a1',
        'background_color': '#f5f7fa',
        'text_color': '#333333',
        'is_premium': False
    },
    # Премиум темы
    {
        'name': 'Премиум градиент',
        'type': 'colorful',
        'primary_color': '#8e24aa',
        'secondary_color': '#5e35b1',
        'background_color': '#ffffff',
        'text_color': '#333333',
        'is_premium': True
    },
    {
        'name': 'Премиум темная',
        'type': 'dark',
        'primary_color': '#1db954',
        'secondary_color': '#191414',
        'background_color': '#121212',
        'text_color': '#ffffff',
        'is_premium': True
    },
    {
        'name': 'Премиум корпоративная',
        'type': 'professional',
        'primary_color': '#00838f',
        'secondary_color': '#006064',
        'background_color': '#f0f7fa',
        'text_color': '#263238',
        'is_premium': True
    }
]

# Добавляем темы в базу данных
for theme_data in themes:
    # Проверяем, существует ли уже тема с таким названием
    if not PortfolioTheme.objects.filter(name=theme_data['name']).exists():
        PortfolioTheme.objects.create(**theme_data)
        print(f"Создана тема: {theme_data['name']}")
    else:
        print(f"Тема {theme_data['name']} уже существует")

print("\nВсего создано тем:", PortfolioTheme.objects.count()) 