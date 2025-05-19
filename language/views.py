from django.shortcuts import render, redirect
from django.utils.translation import activate
from django.urls import reverse
from django.conf import settings
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

# Create your views here.

def set_language(request):
    """
    Устанавливает выбранный язык в сессии пользователя и перенаправляет
    на предыдущую страницу с префиксом языка.
    """
    # Получаем выбранный язык или используем язык по умолчанию
    language = request.POST.get('language', settings.LANGUAGE_CODE)
    
    # Проверяем, что выбранный язык находится в списке доступных языков
    valid_langs = [code for code, name in settings.LANGUAGES]
    if language not in valid_langs:
        language = settings.LANGUAGE_CODE
    
    # Получаем URL для возврата (current или referer или home)
    next_url = request.POST.get('next', '')
    if not next_url:
        next_url = request.META.get('HTTP_REFERER', '/')
    
    # Очищаем URL от языкового префикса, чтобы избежать дублирования
    for lang_code in valid_langs:
        if next_url.startswith(f'/{lang_code}/'):
            next_url = next_url[len(lang_code)+1:]
            break
    
    # Убираем лишние слеши в начале пути
    while next_url.startswith('//'):
        next_url = next_url[1:]
    
    # Если URL не начинается со слеша, добавляем его
    if not next_url.startswith('/'):
        next_url = '/' + next_url
    
    # Добавляем префикс выбранного языка
    if not next_url.startswith(f'/{language}/'):
        if next_url == '/':
            next_url = f'/{language}/'
        else:
            next_url = f'/{language}{next_url}'
    
    # Устанавливаем язык в сессии
    request.session['django_language'] = language
    
    # Активируем язык для текущего запроса
    activate(language)
    
    # Сохраняем язык непосредственно в объекте запроса
    request.LANGUAGE_CODE = language
    
    # Создаем объект ответа
    response = HttpResponseRedirect(next_url)
    
    # Сохраняем выбранный язык в cookie для JavaScript и будущих запросов
    max_age = settings.LANGUAGE_COOKIE_AGE
    expires = None
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=max_age,
        expires=expires,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        path=settings.LANGUAGE_COOKIE_PATH,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE
    )
    
    return response


@user_passes_test(lambda u: u.is_superuser)
def translation_admin(request):
    """
    Перенаправляет на интерфейс Rosetta для управления переводами.
    Доступно только для администраторов.
    """
    return redirect('/admin/')  # Перенаправляем на стандартную админ-панель


def get_translations(request):
    """
    Возвращает переводы для динамического контента в формате JSON.
    Используется для AJAX-запросов.
    """
    # Получаем язык из URL, сессии или cookie
    language = request.LANGUAGE_CODE  # Берем из объекта запроса, установленный middleware
    
    # Активируем выбранный язык
    activate(language)
    
    # Здесь нужно будет получить переводы из базы данных или файла
    # Для примера возьмем простой словарь
    translations = {
        'en': {
            'welcome': 'Welcome',
            'profile': 'Profile',
            'settings': 'Settings',
            'projects': 'Projects',
            'certificates': 'Certificates',
            'achievements': 'Achievements',
            'portfolio': 'Portfolio',
            'resume': 'Resume',
            'skills': 'Skills',
            'edit': 'Edit',
            'delete': 'Delete',
            'add': 'Add',
            'save': 'Save',
            'cancel': 'Cancel',
            'my_profile': 'My Profile',
            'my_projects': 'My Projects',
            'project_feed': 'Project Feed',
            'search_portfolio': 'Search Portfolios',
            'support': 'Support',
            'edit_profile': 'Edit Profile',
            'portfolio_settings': 'Portfolio Settings',
            'subscription': 'Subscription',
            'analytics': 'Analytics',
            'logout': 'Logout',
            'login': 'Login',
            'register': 'Register',
            'create_project': 'Create Project',
            'add_certificate': 'Add Certificate',
            'add_achievement': 'Add Achievement',
            'contact_us': 'Contact Us',
            'privacy_policy': 'Privacy Policy',
            'terms_of_service': 'Terms of Service',
            
            # Тексты с главной страницы
            'project_management': 'Project Management',
            'create_manage_projects': 'Create and manage your academic and professional projects in one place.',
            'certificates_achievements': 'Certificates and Achievements',
            'save_show_certificates': 'Save and showcase your certificates, awards and achievements.',
            'teacher_reviews': 'Teacher Reviews',
            'get_feedback': 'Get constructive feedback from teachers on your work and projects.',
            'how_it_works': 'How it works',
            'home': 'Home',
            'my_certificates': 'My Certificates',
            'my_achievements': 'My Achievements'
        },
        'ru': {
            'welcome': 'Добро пожаловать',
            'profile': 'Профиль',
            'settings': 'Настройки',
            'projects': 'Проекты',
            'certificates': 'Сертификаты',
            'achievements': 'Достижения',
            'portfolio': 'Портфолио',
            'resume': 'Резюме',
            'skills': 'Навыки',
            'edit': 'Редактировать',
            'delete': 'Удалить',
            'add': 'Добавить',
            'save': 'Сохранить',
            'cancel': 'Отмена',
            'my_profile': 'Мой профиль',
            'my_projects': 'Мои проекты',
            'project_feed': 'Лента проектов',
            'search_portfolio': 'Поиск портфолио',
            'support': 'Поддержка',
            'edit_profile': 'Редактировать профиль',
            'portfolio_settings': 'Настройки портфолио',
            'subscription': 'Подписка',
            'analytics': 'Аналитика',
            'logout': 'Выйти',
            'login': 'Вход',
            'register': 'Регистрация',
            'create_project': 'Создать проект',
            'add_certificate': 'Добавить сертификат',
            'add_achievement': 'Добавить достижение',
            'contact_us': 'Связаться с нами',
            'privacy_policy': 'Политика конфиденциальности',
            'terms_of_service': 'Условия использования',
            
            # Тексты с главной страницы
            'project_management': 'Управление проектами',
            'create_manage_projects': 'Создавайте и управляйте вашими учебными и профессиональными проектами в одном месте.',
            'certificates_achievements': 'Сертификаты и достижения',
            'save_show_certificates': 'Сохраняйте и демонстрируйте ваши сертификаты, награды и достижения.',
            'teacher_reviews': 'Отзывы преподавателей',
            'get_feedback': 'Получайте конструктивную обратную связь от преподавателей по вашим работам и проектам.',
            'how_it_works': 'Как это работает',
            'home': 'Главная',
            'my_certificates': 'Мои сертификаты',
            'my_achievements': 'Мои достижения'
        },
        'kk': {
            'welcome': 'Қош келдіңіз',
            'profile': 'Профиль',
            'settings': 'Параметрлер',
            'projects': 'Жобалар',
            'certificates': 'Сертификаттар',
            'achievements': 'Жетістіктер',
            'portfolio': 'Портфолио',
            'resume': 'Түйіндеме',
            'skills': 'Дағдылар',
            'edit': 'Өңдеу',
            'delete': 'Жою',
            'add': 'Қосу',
            'save': 'Сақтау',
            'cancel': 'Болдырмау',
            'my_profile': 'Менің профилім',
            'my_projects': 'Менің жобаларым',
            'project_feed': 'Жобалар тізімі',
            'search_portfolio': 'Портфолио іздеу',
            'support': 'Қолдау',
            'edit_profile': 'Профильді өңдеу',
            'portfolio_settings': 'Портфолио параметрлері',
            'subscription': 'Жазылым',
            'analytics': 'Аналитика',
            'logout': 'Шығу',
            'login': 'Кіру',
            'register': 'Тіркелу',
            'create_project': 'Жоба құру',
            'add_certificate': 'Сертификат қосу',
            'add_achievement': 'Жетістік қосу',
            'contact_us': 'Бізбен байланыс',
            'privacy_policy': 'Құпиялылық саясаты',
            'terms_of_service': 'Қызмет көрсету шарттары',
            
            # Тексты с главной страницы
            'project_management': 'Жобаларды басқару',
            'create_manage_projects': 'Өзіңіздің оқу және кәсіби жобаларыңызды бір жерде жасаңыз және басқарыңыз.',
            'certificates_achievements': 'Сертификаттар мен жетістіктер',
            'save_show_certificates': 'Сертификаттарыңызды, марапаттарыңызды және жетістіктеріңізді сақтаңыз және көрсетіңіз.',
            'teacher_reviews': 'Оқытушылардың пікірлері',
            'get_feedback': 'Оқытушылардан өз жұмыстарыңыз бен жобаларыңыз туралы конструктивті кері байланыс алыңыз.',
            'how_it_works': 'Бұл қалай жұмыс істейді',
            'home': 'Басты бет',
            'my_certificates': 'Менің сертификаттарым',
            'my_achievements': 'Менің жетістіктерім'
        }
    }
    
    # Возвращаем переводы для выбранного языка
    return JsonResponse(translations.get(language, translations['en']))
