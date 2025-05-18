"""
URL configuration for studfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.views.generic import TemplateView
from django.shortcuts import redirect

# URL-шаблоны, которые НЕ будут переводиться (только необходимые пути, которые должны быть без префикса)
urlpatterns = [
    # Перенаправление с корневого URL на версию с префиксом языка
    path('', lambda request: redirect('/' + request.LANGUAGE_CODE + '/'), name='root'),
]

# URL-шаблоны, которые БУДУТ переводиться
# Все пути внутри i18n_patterns будут иметь префикс языка (например, /en/users/, /ru/users/)
urlpatterns += i18n_patterns(
    # Административные пути
    path('admin/', admin.site.urls),
    
    # Пути для интернационализации
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Пути для языковых модулей
    path('translator/', include('translator.urls')),
    path('language/', include('language.urls')),
    
    # Интерфейс переводов Rosetta (только для админов)
    path('rosetta/', include('rosetta.urls')),
    
    # Основные пути
    path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
    path('support/', include('support.urls')),
    path('accounts/', include('allauth.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('', include('users.urls')),
    
    prefix_default_language=True  # Добавлять префикс языка по умолчанию тоже
)

# Добавляем URL для медиа-файлов и статики (без языкового префикса)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
