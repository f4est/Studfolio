#!/usr/bin/env python
"""Django's command-line utility для административных задач с поддержкой Waitress."""
import os
import sys
import logging
from waitress import serve
from studfolio.wsgi import application

# Настройка базового логирования
logging.basicConfig(
    stream=sys.stdout, # Принудительно выводим в stdout
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s'
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # Убедимся, что root logger на DEBUG

# Логгеры spezifичные для waitress и django (уже должны наследоваться, но для ясности)
logging.getLogger('waitress').setLevel(logging.DEBUG)
logging.getLogger('django').setLevel(logging.DEBUG)

# Хост и порт
host = '127.0.0.1'
port = 8080

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')

    logger.info(f"Попытка запуска сервера Waitress на http://{host}:{port}...")
    logger.debug("Объект WSGI приложения: %s", application)
    
    try:
        serve(
            application, 
            host=host, 
            port=port, 
            threads=4, 
            channel_timeout=120, # Увеличим таймаут канала
            clear_untrusted_proxy_headers=True # Для безопасности
        )
    except SystemExit as e:
        logger.info(f"Сервер остановлен с SystemExit: {e}")
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем (KeyboardInterrupt).")
    except Exception as e:
        logger.critical("КРИТИЧЕСКАЯ ОШИБКА при запуске или работе сервера Waitress:", exc_info=True)
        # exc_info=True добавит полный traceback в лог
        sys.exit(1)
    logger.info("Сервер Waitress остановлен.") 