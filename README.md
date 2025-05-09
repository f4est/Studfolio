# Портфолио студентов

Веб-приложение для формирования, хранения и демонстрации портфолио студентов.

## Возможности

- Аутентификация и разделение ролей (Студент, Преподаватель, Администратор)
- Создание и редактирование портфолио
- Загрузка файлов (PDF, изображения, видео)
- Комментирование и оценка портфолио преподавателями
- Экспорт портфолио в PDF

## Технический стек

- **Backend API**: Django 4.x + Django REST Framework
- **Frontend**: Vue.js 3
- **База данных**: SQLite
- **Аутентификация**: JWT + refresh-токены

## Установка и запуск

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
``` 