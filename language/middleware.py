from django.utils.translation import activate
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, Resolver404


class LanguageMiddleware(MiddlewareMixin):
    """
    Middleware для установки языка из URL префикса и сессии пользователя
    """
    def process_request(self, request):
        try:
            # Сначала пытаемся определить язык из URL (первый сегмент пути)
            path = request.path_info.lstrip('/')
            url_lang = path.split('/', 1)[0] if path else None
            
            # Проверяем, является ли первый сегмент пути кодом языка
            valid_langs = [code for code, name in settings.LANGUAGES]
            if url_lang in valid_langs:
                # Устанавливаем язык из URL
                language = url_lang
            else:
                # Если язык не в URL, пытаемся получить его из сессии
                language = request.session.get('django_language')
                
                # Если в сессии нет языка, пытаемся получить его из cookie
                if not language:
                    language = request.COOKIES.get('selected_language')
                
                # Если нигде не нашли язык, используем язык по умолчанию
                if not language or language not in valid_langs:
                    language = settings.LANGUAGE_CODE
            
            # Сохраняем язык в сессии для последующих запросов
            request.session['django_language'] = language
            
            # Активируем язык для текущего запроса
            activate(language)
            
            # Сохраняем язык непосредственно в объекте запроса
            request.LANGUAGE_CODE = language
            
        except Exception as e:
            # В случае ошибки используем язык по умолчанию
            activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
            # Можно добавить логирование ошибки
            print(f"Ошибка в LanguageMiddleware: {e}") 