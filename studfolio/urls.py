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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.views.generic import TemplateView

# URL-шаблоны, которые НЕ будут переводиться (например, админка, API)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('translator/', include('translator.urls')),
]

# URL-шаблоны, которые БУДУТ переводиться
# Все пути внутри i18n_patterns будут иметь префикс языка (например, /en/users/, /ru/users/)
urlpatterns += i18n_patterns(
    path('support/', include('support.urls')),
    path('accounts/', include('allauth.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('', include('users.urls')),
    path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
    prefix_default_language=True
)

# Главная страница (необходимо удалить или закомментировать)
# urlpatterns += [
#     path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
# ]

# Добавляем URL для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Обратите внимание, что явное добавление path('i18n/', include('django.conf.urls.i18n'))
# или path('set_language/', ...) не всегда требуется, если `LocaleMiddleware` активен
# и `USE_I18N = True`. Django и allauth могут обрабатывать `set_language`.
# Однако, чтобы быть уверенным, что Django точно знает о `set_language`,
# особенно если возникают проблемы, можно добавить его явно:

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]
