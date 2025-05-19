import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from pathlib import Path
import shutil
import math

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

# Цветовые схемы (основной цвет, дополнительный цвет, цвет текста)
COLOR_SCHEMES = [
    ((32, 101, 176), (88, 155, 220), (255, 255, 255)),  # Синий
    ((46, 153, 87), (119, 221, 156), (255, 255, 255)),  # Зеленый
    ((173, 48, 41), (225, 101, 94), (255, 255, 255)),   # Красный
    ((119, 73, 152), (168, 128, 199), (255, 255, 255)), # Фиолетовый
    ((213, 156, 34), (246, 199, 97), (68, 68, 68)),     # Желтый
    ((52, 73, 94), (108, 122, 137), (255, 255, 255)),   # Темно-синий
    ((23, 162, 184), (83, 204, 224), (255, 255, 255)),  # Бирюзовый
]

# Паттерны для фона
def create_gradient_background(width, height, color1, color2, vertical=True):
    """Создает градиентный фон"""
    base = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(base)
    
    steps = width if vertical else height
    for i in range(steps):
        r = int(color1[0] + (color2[0] - color1[0]) * i / steps)
        g = int(color1[1] + (color2[1] - color1[1]) * i / steps)
        b = int(color1[2] + (color2[2] - color1[2]) * i / steps)
        
        line_color = (r, g, b)
        if vertical:
            draw.line([(i, 0), (i, height)], fill=line_color)
        else:
            draw.line([(0, i), (width, i)], fill=line_color)
    
    return base

def create_pattern_background(width, height, color1, color2):
    """Создает фон с паттерном"""
    base = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(base)
    
    # Выбираем случайный паттерн
    pattern_type = random.choice(['dots', 'grid', 'lines', 'diagonal'])
    
    if pattern_type == 'dots':
        dot_spacing = random.randint(20, 40)
        dot_size = random.randint(2, 6)
        for x in range(0, width, dot_spacing):
            for y in range(0, height, dot_spacing):
                draw.ellipse([(x, y), (x + dot_size, y + dot_size)], fill=color2)
    
    elif pattern_type == 'grid':
        grid_spacing = random.randint(30, 60)
        line_width = random.randint(1, 3)
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=color2, width=line_width)
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=color2, width=line_width)
    
    elif pattern_type == 'lines':
        line_spacing = random.randint(20, 40)
        line_width = random.randint(1, 4)
        for y in range(0, height, line_spacing):
            draw.line([(0, y), (width, y)], fill=color2, width=line_width)
    
    elif pattern_type == 'diagonal':
        line_spacing = random.randint(20, 50)
        line_width = random.randint(1, 3)
        for i in range(-height, width + height, line_spacing):
            draw.line([(i, 0), (i + height, height)], fill=color2, width=line_width)
    
    return base

# Функция для создания реалистичной заглушки
def create_realistic_placeholder(path, width, height, text, theme=None):
    """Создает реалистичную заглушку изображения"""
    # Выбираем цветовую схему
    color_scheme = random.choice(COLOR_SCHEMES) if theme is None else COLOR_SCHEMES[theme % len(COLOR_SCHEMES)]
    main_color, secondary_color, text_color = color_scheme
    
    # Определяем тип фона: градиент или паттерн
    background_type = random.choice(['gradient', 'pattern'])
    
    if background_type == 'gradient':
        vertical = random.choice([True, False])
        img = create_gradient_background(width, height, main_color, secondary_color, vertical)
    else:
        img = create_pattern_background(width, height, main_color, secondary_color)
    
    # Добавляем небольшое размытие
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Добавляем текст
    draw = ImageDraw.Draw(img)
    
    # Настраиваем размер шрифта
    font_size = min(width, height) // 10
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
        small_font = ImageFont.truetype('arial.ttf', font_size // 2)
    except IOError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Рисуем основной текст (центрированный)
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Добавляем тень для текста (необязательно)
    shadow_offset = 2
    draw.text((position[0] + shadow_offset, position[1] + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
    draw.text(position, text, font=font, fill=text_color)
    
    # Добавляем размеры изображения внизу
    size_text = f"{width} × {height}"
    size_text_width, size_text_height = draw.textbbox((0, 0), size_text, font=small_font)[2:4]
    size_position = ((width - size_text_width) // 2, height - size_text_height - 10)
    draw.text(size_position, size_text, font=small_font, fill=text_color)
    
    # Добавляем рамку или декоративный элемент
    if random.choice([True, False]):
        frame_width = 4
        # Внешняя рамка
        draw.rectangle([0, 0, width-1, height-1], outline=secondary_color, width=frame_width)
        # Внутренняя рамка (меньше)
        inner_margin = 10
        draw.rectangle([inner_margin, inner_margin, width-inner_margin-1, height-inner_margin-1], 
                      outline=secondary_color, width=1)
    
    # Сохраняем изображение
    img.save(path)
    print(f"Создана реалистичная заглушка: {path}")
    return True

# Функция для создания иконки или логотипа
def create_icon_placeholder(path, size, text, is_round=False):
    """Создает заглушку для иконки или логотипа"""
    # Выбираем цветовую схему
    color_scheme = random.choice(COLOR_SCHEMES)
    main_color, secondary_color, text_color = color_scheme
    
    # Создаем квадратное изображение
    img = Image.new('RGBA', (size, size), main_color)
    draw = ImageDraw.Draw(img)
    
    # Определяем тип иконки
    icon_type = random.choice(['letter', 'shape', 'simple'])
    
    if icon_type == 'letter':
        # Иконка с буквой
        letter = text[0].upper() if text else 'S'
        try:
            font = ImageFont.truetype('arial.ttf', size // 2)
        except IOError:
            font = ImageFont.load_default()
        
        # Центрируем букву
        letter_width, letter_height = draw.textbbox((0, 0), letter, font=font)[2:4]
        position = ((size - letter_width) // 2, (size - letter_height) // 2)
        draw.text(position, letter, font=font, fill=text_color)
    
    elif icon_type == 'shape':
        # Иконка с геометрической фигурой
        shape = random.choice(['circle', 'triangle', 'square'])
        padding = size // 5
        
        if shape == 'circle':
            draw.ellipse([(padding, padding), (size-padding, size-padding)], fill=secondary_color)
        elif shape == 'triangle':
            draw.polygon([(size//2, padding), (padding, size-padding), (size-padding, size-padding)], fill=secondary_color)
        elif shape == 'square':
            draw.rectangle([(padding, padding), (size-padding, size-padding)], fill=secondary_color)
            
    elif icon_type == 'simple':
        # Простая иконка с градиентом и линией
        for i in range(size):
            r = int(main_color[0] + (secondary_color[0] - main_color[0]) * i / size)
            g = int(main_color[1] + (secondary_color[1] - main_color[1]) * i / size)
            b = int(main_color[2] + (secondary_color[2] - main_color[2]) * i / size)
            draw.line([(0, i), (size, i)], fill=(r, g, b))
        
        # Добавляем линию
        line_width = max(1, size // 20)
        draw.line([(size//4, size//2), (3*size//4, size//2)], fill=text_color, width=line_width)
    
    # Если нужно создать круглую иконку
    if is_round:
        # Создаем маску круга
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)
        
        # Применяем маску
        img_rgba = img.convert("RGBA")
        img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        img.paste(img_rgba, (0, 0), mask)
    
    # Сохраняем как PNG для прозрачности
    img.save(path, format='PNG')
    print(f"Создана заглушка иконки: {path}")
    return True

# Функция для создания заглушки аватара
def create_avatar_placeholder(path, size, text=None):
    """Создает заглушку для аватара"""
    # Случайная цветовая схема
    color_scheme = random.choice(COLOR_SCHEMES)
    main_color, secondary_color, text_color = color_scheme
    
    # Создаем базовое изображение
    img = Image.new('RGB', (size, size), main_color)
    draw = ImageDraw.Draw(img)
    
    # Выбираем тип аватара
    avatar_type = random.choice(['initials', 'silhouette', 'abstract'])
    
    if avatar_type == 'initials':
        # Аватар с инициалами
        initials = "U" if not text else text[0].upper()
        try:
            font = ImageFont.truetype('arial.ttf', size // 2)
        except IOError:
            font = ImageFont.load_default()
        
        # Центрируем инициалы
        text_width, text_height = draw.textbbox((0, 0), initials, font=font)[2:4]
        position = ((size - text_width) // 2, (size - text_height) // 2)
        draw.text(position, initials, font=font, fill=text_color)
    
    elif avatar_type == 'silhouette':
        # Аватар с силуэтом
        # Рисуем круг для головы
        head_size = size // 2
        head_pos = (size // 2, size // 3)
        draw.ellipse([
            (head_pos[0] - head_size//2, head_pos[1] - head_size//2),
            (head_pos[0] + head_size//2, head_pos[1] + head_size//2)
        ], fill=secondary_color)
        
        # Рисуем тело
        body_top = head_pos[1] + head_size//2
        draw.ellipse([
            (size//4, body_top),
            (3*size//4, size)
        ], fill=secondary_color)
    
    elif avatar_type == 'abstract':
        # Абстрактный аватар с геометрическими фигурами
        for i in range(random.randint(3, 6)):
            shape = random.choice(['circle', 'rectangle', 'triangle'])
            shape_color = (
                random.randint(max(0, main_color[0]-50), min(255, main_color[0]+50)),
                random.randint(max(0, main_color[1]-50), min(255, main_color[1]+50)),
                random.randint(max(0, main_color[2]-50), min(255, main_color[2]+50))
            )
            
            # Случайное расположение и размер
            x = random.randint(0, size)
            y = random.randint(0, size)
            w = random.randint(size//5, size//2)
            h = random.randint(size//5, size//2)
            
            if shape == 'circle':
                draw.ellipse([(x, y), (x+w, y+h)], fill=shape_color)
            elif shape == 'rectangle':
                draw.rectangle([(x, y), (x+w, y+h)], fill=shape_color)
            elif shape == 'triangle':
                draw.polygon([(x, y+h), (x+w//2, y), (x+w, y+h)], fill=shape_color)
    
    # Добавляем небольшое размытие
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Делаем круглую аватарку
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size, size), fill=255)
    
    # Обрезаем до круга
    result = Image.new('RGB', (size, size), (255, 255, 255, 0))
    result.paste(img, (0, 0), mask)
    
    # Сохраняем изображение
    result.save(path)
    print(f"Создана заглушка аватара: {path}")
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
    
    # Создаем заглушки аватаров
    avatar_placeholders = [
        (placeholders_dir / 'avatars' / 'default.jpg', 200, 'User'),
        (placeholders_dir / 'avatars' / 'large.jpg', 300, 'User'),
        (placeholders_dir / 'avatars' / 'small.jpg', 100, 'User'),
        # Дополнительные аватары с разными именами
        (placeholders_dir / 'avatars' / 'avatar1.jpg', 200, 'Alex'),
        (placeholders_dir / 'avatars' / 'avatar2.jpg', 200, 'Maria'),
        (placeholders_dir / 'avatars' / 'avatar3.jpg', 200, 'Ivan'),
        (placeholders_dir / 'avatars' / 'avatar4.jpg', 200, 'Elena'),
        (placeholders_dir / 'avatars' / 'avatar5.jpg', 200, 'Dmitry'),
    ]
    
    for path, size, text in avatar_placeholders:
        create_avatar_placeholder(path, size, text)
    
    # Создаем заглушки проектов
    project_names = [
        "Веб-разработка", "Мобильное приложение", "Дизайн интерфейса", 
        "Исследовательская работа", "Программная система"
    ]
    
    project_placeholders = [
        (placeholders_dir / 'projects' / 'default.jpg', 800, 500, "Проект"),
        (placeholders_dir / 'projects' / 'thumbnail.jpg', 400, 250, "Миниатюра"),
        (placeholders_dir / 'projects' / 'banner.jpg', 1200, 400, "Баннер проекта"),
    ]
    
    for i, name in enumerate(project_names):
        project_placeholders.append(
            (placeholders_dir / 'projects' / f'project{i+1}.jpg', 800, 500, name)
        )
        project_placeholders.append(
            (placeholders_dir / 'projects' / f'project{i+1}_thumb.jpg', 400, 250, name)
        )
    
    # Создаем заглушки проектов разных цветов
    for i in range(1, 6):
        project_placeholders.append(
            (placeholders_dir / 'projects' / f'colored_{i}.jpg', 800, 500, f"Проект {i}", i-1)
        )
    
    for path, width, height, text, *args in project_placeholders:
        theme = args[0] if args else None
        create_realistic_placeholder(path, width, height, text, theme)
    
    # Создаем заглушки сертификатов
    certificate_names = [
        "Сертификат Web-разработчика", "Курс Python", "Основы Data Science", 
        "Front-end разработка", "DevOps практики"
    ]
    
    certificate_placeholders = [
        (placeholders_dir / 'certificates' / 'default.jpg', 1000, 700, "Сертификат"),
        (placeholders_dir / 'certificates' / 'thumbnail.jpg', 500, 350, "Сертификат"),
    ]
    
    for i, name in enumerate(certificate_names):
        certificate_placeholders.append(
            (placeholders_dir / 'certificates' / f'certificate{i+1}.jpg', 1000, 700, name)
        )
        certificate_placeholders.append(
            (placeholders_dir / 'certificates' / f'certificate{i+1}_thumb.jpg', 500, 350, name)
        )
    
    for path, width, height, text in certificate_placeholders:
        create_realistic_placeholder(path, width, height, text)
    
    # Создаем заглушки достижений
    achievement_names = [
        "Победитель хакатона", "Лучший студенческий проект", "Научная публикация", 
        "Стипендия за достижения", "Участие в конференции"
    ]
    
    achievement_placeholders = [
        (placeholders_dir / 'achievements' / 'default.jpg', 600, 600, "Достижение"),
        (placeholders_dir / 'achievements' / 'small.jpg', 300, 300, "Достижение"),
    ]
    
    for i, name in enumerate(achievement_names):
        achievement_placeholders.append(
            (placeholders_dir / 'achievements' / f'achievement{i+1}.jpg', 600, 600, name)
        )
        achievement_placeholders.append(
            (placeholders_dir / 'achievements' / f'achievement{i+1}_small.jpg', 300, 300, name)
        )
    
    for path, width, height, text in achievement_placeholders:
        create_realistic_placeholder(path, width, height, text)
    
    # Создаем заглушки баннеров
    banner_placeholders = [
        (placeholders_dir / 'banners' / 'large.jpg', 1920, 600, "Баннер"),
        (placeholders_dir / 'banners' / 'medium.jpg', 1400, 400, "Баннер"),
        (placeholders_dir / 'banners' / 'small.jpg', 800, 300, "Баннер"),
    ]
    
    for path, width, height, text in banner_placeholders:
        create_realistic_placeholder(path, width, height, text)
    
    # Создаем заглушки логотипов и иконок
    logo_placeholders = [
        (placeholders_dir / 'logos' / 'default.png', 200, "Лого"),
        (placeholders_dir / 'logos' / 'small.png', 100, "Лого"),
    ]
    
    icon_placeholders = [
        (placeholders_dir / 'icons' / 'default.png', 64, "Иконка"),
        (placeholders_dir / 'icons' / 'small.png', 32, "Иконка"),
        (placeholders_dir / 'icons' / 'large.png', 128, "Иконка"),
    ]
    
    for path, size, text in logo_placeholders:
        create_icon_placeholder(path, size, text, is_round=False)
    
    for path, size, text in icon_placeholders:
        create_icon_placeholder(path, size, text, is_round=True)
    
    print("\nВсе заглушки успешно созданы!")
    print(f"Основная директория: {placeholders_dir}")
    print(f"Всего создано заглушек: {len(avatar_placeholders) + len(project_placeholders) + len(certificate_placeholders) + len(achievement_placeholders) + len(banner_placeholders) + len(logo_placeholders) + len(icon_placeholders)}")

if __name__ == "__main__":
    main() 