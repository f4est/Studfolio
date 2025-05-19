import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

# Импорт моделей после настройки Django
from users.models import PortfolioTheme

def create_themes():
    """Создает стандартные темы оформления портфолио"""
    
    # Удаляем существующие темы (опционально)
    existing_themes = PortfolioTheme.objects.all().count()
    if existing_themes > 0:
        print(f"Темы портфолио уже существуют ({existing_themes}). Очищаем и создаем новые...")
        PortfolioTheme.objects.all().delete()
    
    # Список тем для создания
    themes = [
        {
            'name': 'Классическая',
            'description': 'Стандартная светлая тема',
            'is_premium': False
        },
        {
            'name': 'Тёмная',
            'description': 'Тёмная тема с контрастными элементами',
            'is_premium': False
        },
        {
            'name': 'Минималистичная',
            'description': 'Простая и лаконичная тема',
            'is_premium': False
        },
        {
            'name': 'Синяя',
            'description': 'Яркая синяя тема',
            'is_premium': True
        },
        {
            'name': 'Премиум',
            'description': 'Эксклюзивная премиум-тема с расширенными возможностями',
            'is_premium': True
        }
    ]
    
    # Создаем темы
    created_themes = []
    for theme_data in themes:
        theme = PortfolioTheme.objects.create(**theme_data)
        created_themes.append(theme)
    
    print(f"Создано {len(created_themes)} тем портфолио")

if __name__ == '__main__':
    create_themes()
    print("Готово! Темы портфолио созданы.") 