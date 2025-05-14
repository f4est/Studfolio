# Инструкции по развертыванию Studfolio

В этом документе приведены разные способы развертывания Django-приложения Studfolio в производственной среде.

## 1. Django + SSL Server (Для разработки на Windows и Linux)

Самый простой вариант для тестирования через HTTPS:

### Установка

```bash
pip install django-sslserver
```

### Добавьте в settings.py

```python
INSTALLED_APPS = [
    # ... другие приложения
    'sslserver',
]
```

### Запуск

```bash
python manage.py runsslserver
```

По умолчанию сервер запустится на https://127.0.0.1:8000/

## 2. Gunicorn + Nginx (для Linux)

### Установка необходимых пакетов

```bash
pip install gunicorn
sudo apt-get install nginx
```

### Настройка Gunicorn

Создайте файл сервиса systemd `/etc/systemd/system/studfolio.service`:

```ini
[Unit]
Description=Studfolio Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/путь/к/проекту
ExecStart=/путь/к/venv/bin/gunicorn --workers 3 --bind unix:/tmp/studfolio.sock studfolio.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Настройка Nginx

Создайте файл конфигурации Nginx `/etc/nginx/sites-available/studfolio`:

```nginx
server {
    listen 80;
    server_name ваш_домен.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /путь/к/проекту;
    }

    location /media/ {
        root /путь/к/проекту;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/tmp/studfolio.sock;
    }
}
```

Создайте символическую ссылку и перезапустите Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/studfolio /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

### Запуск службы Gunicorn

```bash
sudo systemctl start studfolio
sudo systemctl enable studfolio
```

## 3. Django + Daphne + Nginx для ASGI (Linux)

### Установка необходимых пакетов

```bash
pip install daphne
sudo apt-get install nginx
```

### Настройка проекта для ASGI

Создайте файл `studfolio/asgi.py` (если его нет):

```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
application = get_asgi_application()
```

### Настройка сервиса Daphne

Создайте файл сервиса systemd `/etc/systemd/system/daphne.service`:

```ini
[Unit]
Description=Studfolio Daphne Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/путь/к/проекту
ExecStart=/путь/к/venv/bin/daphne -u /tmp/daphne.sock studfolio.asgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Настройка Nginx для ASGI

Создайте файл конфигурации Nginx `/etc/nginx/sites-available/studfolio`:

```nginx
server {
    listen 80;
    server_name ваш_домен.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /путь/к/проекту;
    }

    location /media/ {
        root /путь/к/проекту;
    }

    location / {
        proxy_pass http://unix:/tmp/daphne.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Активация и запуск

```bash
sudo ln -s /etc/nginx/sites-available/studfolio /etc/nginx/sites-enabled
sudo systemctl restart nginx
sudo systemctl start daphne
sudo systemctl enable daphne
```

## 4. IIS + Django на Windows Server

### Установка

1. Установите Python на Windows Server
2. Установите Web Platform Installer
3. Через Web Platform Installer установите модуль "URL Rewrite" для IIS
4. Установите wfastcgi:

```bash
pip install wfastcgi
wfastcgi-enable
```

### Настройка IIS

1. Создайте новый сайт в IIS Manager
2. Укажите физический путь к папке проекта
3. Добавьте обработчик для fastcgi:
   - Путь запроса: *.py
   - Executable: C:\путь\к\python.exe|C:\путь\к\wfastcgi.py
   - Имя: Python_FastCGI

4. Создайте web.config файл в корне проекта:

```xml
<configuration>
  <system.webServer>
    <handlers>
      <add name="Python_FastCGI" 
           path="*.py" 
           verb="*" 
           modules="FastCgiModule" 
           scriptProcessor="C:\путь\к\python.exe|C:\путь\к\wfastcgi.py" 
           resourceType="Unspecified" />
    </handlers>
    <rewrite>
      <rules>
        <rule name="Static Files" stopProcessing="true">
          <match url="^(static|media)/(.*)" />
          <action type="Rewrite" url="{R:1}/{R:2}" />
        </rule>
        <rule name="Django URLs" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
          </conditions>
          <action type="Rewrite" url="studfolio/wsgi.py" />
        </rule>
      </rules>
    </rewrite>
    <appSettings>
      <add key="WSGI_HANDLER" value="django.core.wsgi.get_wsgi_application()" />
      <add key="PYTHONPATH" value="C:\путь\к\проекту" />
      <add key="DJANGO_SETTINGS_MODULE" value="studfolio.settings" />
    </appSettings>
  </system.webServer>
</configuration>
```

### Подготовка статических файлов

```bash
python manage.py collectstatic
```

## 5. Django + gunicorn + waitress (для Windows)

### Установка

```bash
pip install waitress gunicorn
```

### Пример запуска с помощью waitress

```bash
waitress-serve --port=8000 studfolio.wsgi:application
```

### Создание службы Windows

Используйте NSSM (Non-Sucking Service Manager):

1. Скачайте NSSM: https://nssm.cc/
2. Зарегистрируйте службу:

```bash
nssm install StudfolioService "C:\путь\к\venv\Scripts\waitress-serve.exe" "--port=8000 studfolio.wsgi:application"
nssm set StudfolioService AppDirectory "C:\путь\к\проекту"
nssm start StudfolioService
```

## 6. Деплой на платформе Render

Render - облачная платформа, которая предлагает бесплатный и платный хостинг для веб-приложений.

### Настройка проекта для Render

1. Создайте файл `requirements.txt` (если его еще нет):

```bash
pip freeze > requirements.txt
```

2. Создайте файл `build.sh` в корне проекта:

```bash
#!/usr/bin/env bash
# Выход при ошибке
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Сбор статических файлов
python manage.py collectstatic --no-input

# Применение миграций
python manage.py migrate
```

3. Создайте файл `render.yaml` для настройки деплоя:

```yaml
services:
  - type: web
    name: studfolio
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn studfolio.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: ".onrender.com"
      - key: DATABASE_URL
        fromDatabase:
          name: studfolio_db
          property: connectionString

databases:
  - name: studfolio_db
    plan: free
```

4. Обновите настройки в файле `settings.py`:

```python
import dj_database_url
import os
from pathlib import Path

# ... существующий код ...

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-REPLACE_WITH_YOUR_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = []
# Если определена переменная RENDER_EXTERNAL_HOSTNAME, добавляем ее в ALLOWED_HOSTS
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Добавляем значения из ALLOWED_HOSTS env var
ALLOWED_HOSTS += [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Заменяем конфигурацию БД, если определена переменная DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
```

### Деплой на Render

1. Зарегистрируйтесь на сайте [Render](https://render.com/)
2. Подключите свой репозиторий GitHub/GitLab/Bitbucket
3. Нажмите "New Web Service" и выберите свой репозиторий
4. Заполните данные:
   - **Name**: studfolio (или любое другое имя)
   - **Region**: выберите ближайший к вам регион
   - **Branch**: main (или другая ветка для деплоя)
   - **Runtime**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn studfolio.wsgi:application`
5. В разделе "Environment Variables" добавьте:
   - `SECRET_KEY`: <сгенерируйте случайный секретный ключ>
   - `DEBUG`: false
   - `ALLOWED_HOSTS`: .onrender.com,<ваш_домен_если_есть>
   - Другие необходимые переменные

6. Нажмите "Create Web Service"

### Установка дополнительных пакетов

Не забудьте добавить в `requirements.txt`:

```
dj-database-url==2.1.0
psycopg2-binary==2.9.9  # Для PostgreSQL
gunicorn==21.2.0
whitenoise==6.6.0  # Для статических файлов
```

И обновить `settings.py` для использования WhiteNoise:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Добавляем сразу после SecurityMiddleware
    # ... остальные middleware
]

# Настройка WhiteNoise для статических файлов
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Важные команды для Render

- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn studfolio.wsgi:application`

Если нужно настроить Gunicorn дополнительно:
- **Start Command**: `gunicorn studfolio.wsgi:application --workers 4 --threads 2 --timeout 60`

## Рекомендации по безопасности

1. Изменить SECRET_KEY в settings.py
2. Настроить HTTPS с помощью Let's Encrypt
3. Установить DEBUG = False в production
4. Настроить ALLOWED_HOSTS соответствующим образом
5. Регулярно обновлять зависимости

## Настройка SSL/TLS

Для всех вариантов рекомендуется настроить SSL/TLS сертификаты:

### Для Nginx (Linux):

```bash
# Установка Certbot
sudo apt-get install certbot python3-certbot-nginx

# Получение и настройка сертификата
sudo certbot --nginx -d ваш_домен.com
```

### Для IIS (Windows):

1. Используйте менеджер IIS для установки сертификата
2. Win-Acme можно использовать для автоматизации Let's Encrypt на Windows:
   https://www.win-acme.com/ 