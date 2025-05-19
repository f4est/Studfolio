# Система заглушек изображений в Studfolio

## Обзор

Система заглушек изображений предоставляет автоматическую замену отсутствующих или недоступных изображений на визуально приятные заглушки.
Система работает как на сервере (через Django template tags), так и на клиенте (через JavaScript), обеспечивая бесшовный опыт пользователя.

## Компоненты системы

1. **Заглушки изображений** - находятся в директории `media/placeholders`
   - Аватары, проекты, сертификаты, достижения, баннеры, иконки и т.д.

2. **Серверные компоненты**:
   - `users/placeholders.py` - константы с путями к заглушкам
   - `users/context_processors.py` - контекст-процессор для доступа к заглушкам в шаблонах
   - `users/templatetags/placeholder_tags.py` - теги шаблонов для работы с заглушками

3. **Клиентские компоненты**:
   - `static/js/image-placeholder.js` - JS скрипт для обработки отсутствующих изображений
   - `static/css/image-placeholder.css` - стили для заглушек изображений

4. **Утилиты**:
   - `templates/includes/image_helpers.html` - макросы для шаблонов
   - `fix_missing_images.py` - скрипт для исправления отсутствующих изображений в БД

## Использование в шаблонах Django

### 1. Через template tags

```html
{% load placeholder_tags %}

<!-- Базовое использование -->
<img src="{{ user.profile_image|placeholder_or_image:'avatar' }}" alt="Аватар">

<!-- С указанием размера -->
<img src="{{ user.profile_image|placeholder_or_image:'avatar_small' }}" alt="Аватар">
<img src="{{ user.profile_image|placeholder_or_image:'avatar_large' }}" alt="Аватар">

<!-- Для различных типов контента -->
<img src="{{ project.image|placeholder_or_image:'project' }}" alt="Проект">
<img src="{{ certificate.image|placeholder_or_image:'certificate' }}" alt="Сертификат">
<img src="{{ achievement.image|placeholder_or_image:'achievement' }}" alt="Достижение">

<!-- Случайные заглушки -->
<img src="{{ 'project'|random_placeholder }}" alt="Случайный проект">
```

### 2. Через включаемые макросы

```html
{% include 'includes/image_helpers.html' with template='user_avatar' image=user.profile_image size='small' alt=user.username %}

{% include 'includes/image_helpers.html' with template='project_image' image=project.image type='thumbnail' alt=project.title %}

{% include 'includes/image_helpers.html' with template='certificate_image' image=certificate.image alt=certificate.title %}

{% include 'includes/image_helpers.html' with template='achievement_image' image=achievement.image type='small' alt=achievement.title %}

{% include 'includes/image_helpers.html' with template='random_placeholder' type='project' alt='Случайный проект' %}
```

## Использование в HTML с JavaScript

### Добавление атрибута data-placeholder

```html
<!-- Простое использование -->
<img src="/path/to/image.jpg" data-placeholder="avatar" alt="Аватар">

<!-- С указанием различных типов -->
<img src="/path/to/image.jpg" data-placeholder="project" alt="Проект">
<img src="/path/to/image.jpg" data-placeholder="certificate" alt="Сертификат">
<img src="/path/to/image.jpg" data-placeholder="achievement" alt="Достижение">
```

### Использование классов для автоматического определения типа заглушки

```html
<!-- Определение по классу -->
<img src="/path/to/image.jpg" class="avatar rounded-circle" alt="Аватар">
<img src="/path/to/image.jpg" class="project thumbnail" alt="Миниатюра проекта">
<img src="/path/to/image.jpg" class="certificate" alt="Сертификат">
<img src="/path/to/image.jpg" class="achievement small" alt="Достижение маленькое">
```

## Создание новых заглушек

Для создания новых заглушек используйте скрипт `create_realistic_placeholders.py`:

```bash
python create_realistic_placeholders.py
```

После создания новых заглушек, примените их к проекту:

```bash
python apply_placeholders.py
```

## Исправление отсутствующих изображений

Если вы заметили, что в проекте отсутствуют некоторые изображения, запустите:

```bash
python fix_missing_images.py
```

## Дополнительные стили

Заглушки изображений имеют дополнительные CSS стили и эффекты:

- Плавное появление
- Пульсация для индикации заглушки
- Тени при наведении
- Адаптация к тёмной теме

Класс `.using-placeholder` автоматически добавляется к изображениям, для которых была применена заглушка. 