import os
import random
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import shutil

# Создаем корневую папку для заглушек если её нет
placeholders_dir = Path('media/placeholders')
os.makedirs(placeholders_dir, exist_ok=True)

# Удаляем все существующие файлы в директории placeholders
for item in placeholders_dir.glob('*.jpg'):
    if item.is_file():
        item.unlink()
for item in placeholders_dir.glob('*.png'):
    if item.is_file():
        item.unlink()

# Функция для создания заглушки определенного размера и текста
def create_placeholder(path, width, height, text, bg_color=None, text_color=(255, 255, 255)):
    # Если цвет фона не указан, выбираем случайный пастельный цвет
    if bg_color is None:
        # Генерируем пастельные цвета
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)
        bg_color = (r, g, b)
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Добавляем текст (размер текста зависит от размера изображения)
    font_size = min(width, height) // 10
    try:
        # Попытка использовать Arial, если доступен
        font = ImageFont.truetype('arial.ttf', font_size)
    except IOError:
        # Иначе используем стандартный шрифт
        font = ImageFont.load_default()
    
    # Вычисляем размеры текста
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    
    # Рисуем текст по центру
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, font=font, fill=text_color)
    
    # Рисуем рамку
    draw.rectangle([(0, 0), (width-1, height-1)], outline=text_color, width=2)
    
    # Добавляем размеры изображения как дополнительный текст
    size_text = f"{width}x{height}"
    size_text_width, size_text_height = draw.textbbox((0, 0), size_text, font=font)[2:4]
    draw.text(
        ((width - size_text_width) // 2, height - size_text_height - 10),
        size_text,
        font=font,
        fill=text_color
    )
    
    # Сохраняем изображение
    img.save(path)
    print(f"Создана заглушка: {path}")
    return True

def main():
    # Очищаем все существующие поддиректории
    subdirs = ['avatars', 'projects', 'certificates', 'achievements', 'banners', 'logos', 'icons']
    for subdir in subdirs:
        subdir_path = placeholders_dir / subdir
        if subdir_path.exists():
            for item in subdir_path.glob('*'):
                if item.is_file():
                    item.unlink()
        os.makedirs(subdir_path, exist_ok=True)
        print(f"Очищена и подготовлена директория: {subdir_path}")
    
    # Определяем типы заглушек и их параметры
    placeholders = [
        # Аватарки пользователей (квадратные)
        (placeholders_dir / 'profile-placeholder.jpg', 200, 200, 'Аватарка'),
        (placeholders_dir / 'profile-large.jpg', 300, 300, 'Аватарка'),
        (placeholders_dir / 'profile-small.jpg', 100, 100, 'Аватарка'),
        
        # Изображения проектов (прямоугольные)
        (placeholders_dir / 'project-placeholder.jpg', 800, 500, 'Проект'),
        (placeholders_dir / 'project-thumbnail.jpg', 400, 250, 'Миниатюра'),
        (placeholders_dir / 'project-banner.jpg', 1200, 400, 'Баннер проекта'),
        
        # Сертификаты (альбомная ориентация)
        (placeholders_dir / 'certificate-placeholder.jpg', 1000, 700, 'Сертификат'),
        (placeholders_dir / 'certificate-thumbnail.jpg', 500, 350, 'Сертификат'),
        
        # Достижения (квадратные или прямоугольные)
        (placeholders_dir / 'achievement-placeholder.jpg', 600, 600, 'Достижение'),
        (placeholders_dir / 'achievement-small.jpg', 300, 300, 'Достижение'),
        
        # Логотипы и значки
        (placeholders_dir / 'logo-placeholder.png', 200, 200, 'Логотип'),
        (placeholders_dir / 'icon-placeholder.png', 64, 64, 'Иконка'),
        
        # Баннеры для главной страницы
        (placeholders_dir / 'banner-large.jpg', 1920, 600, 'Баннер'),
        (placeholders_dir / 'banner-medium.jpg', 1400, 400, 'Баннер'),
        
        # Дополнительные заглушки по размерам
        (placeholders_dir / 'placeholder-xs.jpg', 100, 100, 'XS'),
        (placeholders_dir / 'placeholder-sm.jpg', 300, 200, 'SM'),
        (placeholders_dir / 'placeholder-md.jpg', 600, 400, 'MD'),
        (placeholders_dir / 'placeholder-lg.jpg', 900, 600, 'LG'),
        (placeholders_dir / 'placeholder-xl.jpg', 1200, 800, 'XL'),
    ]
    
    # Создаем заглушки непосредственно в подкаталогах
    avatar_placeholders = [
        (placeholders_dir / 'avatars' / 'default.jpg', 200, 200, 'Аватарка'),
        (placeholders_dir / 'avatars' / 'large.jpg', 300, 300, 'Аватарка'),
        (placeholders_dir / 'avatars' / 'small.jpg', 100, 100, 'Аватарка'),
    ]
    
    project_placeholders = [
        (placeholders_dir / 'projects' / 'default.jpg', 800, 500, 'Проект'),
        (placeholders_dir / 'projects' / 'thumbnail.jpg', 400, 250, 'Миниатюра'),
        (placeholders_dir / 'projects' / 'banner.jpg', 1200, 400, 'Баннер проекта'),
    ]
    
    certificate_placeholders = [
        (placeholders_dir / 'certificates' / 'default.jpg', 1000, 700, 'Сертификат'),
        (placeholders_dir / 'certificates' / 'thumbnail.jpg', 500, 350, 'Сертификат'),
    ]
    
    achievement_placeholders = [
        (placeholders_dir / 'achievements' / 'default.jpg', 600, 600, 'Достижение'),
        (placeholders_dir / 'achievements' / 'small.jpg', 300, 300, 'Достижение'),
    ]
    
    banner_placeholders = [
        (placeholders_dir / 'banners' / 'large.jpg', 1920, 600, 'Баннер'),
        (placeholders_dir / 'banners' / 'medium.jpg', 1400, 400, 'Баннер'),
        (placeholders_dir / 'banners' / 'small.jpg', 800, 300, 'Баннер'),
    ]
    
    logo_icon_placeholders = [
        (placeholders_dir / 'logos' / 'default.png', 200, 200, 'Логотип'),
        (placeholders_dir / 'icons' / 'default.png', 64, 64, 'Иконка'),
        (placeholders_dir / 'icons' / 'small.png', 32, 32, 'Иконка'),
        (placeholders_dir / 'icons' / 'large.png', 128, 128, 'Иконка'),
    ]
    
    # Создаем все заглушки
    all_placeholders = (
        placeholders + 
        avatar_placeholders + 
        project_placeholders + 
        certificate_placeholders + 
        achievement_placeholders + 
        banner_placeholders + 
        logo_icon_placeholders
    )
    
    for path, width, height, text in all_placeholders:
        create_placeholder(path, width, height, text)
    
    # Создаем дополнительные заглушки для проектов с разными цветами
    colors = [
        ((60, 120, 200), 'Синяя'),
        ((200, 60, 60), 'Красная'),
        ((60, 180, 60), 'Зеленая'),
        ((200, 180, 60), 'Желтая'),
        ((180, 60, 180), 'Фиолетовая'),
    ]
    
    for i, (color, name) in enumerate(colors, 1):
        path = placeholders_dir / 'projects' / f'colored_{i}.jpg'
        create_placeholder(path, 800, 500, f'Проект {name}', bg_color=color)
    
    print("\nВсе заглушки успешно созданы!")
    print(f"Основная директория: {placeholders_dir}")
    print(f"Всего создано заглушек: {len(all_placeholders) + len(colors)}")

if __name__ == "__main__":
    main() 