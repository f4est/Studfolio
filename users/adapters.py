from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Кастомный адаптер для allauth, который управляет функциональностью
    подтверждения кода в зависимости от настроек пользователя
    """
    
    def is_open_for_signup(self, request):
        """
        Открыта ли регистрация для новых пользователей.
        """
        return getattr(settings, 'ACCOUNT_ALLOW_SIGNUPS', True)
    
    def get_login_redirect_url(self, request):
        """
        Переопределение URL для перенаправления после входа.
        """
        return settings.LOGIN_REDIRECT_URL
    
    def login(self, request, user):
        """
        Переопределение метода входа в зависимости от настроек пользователя.
        """
        # Если у пользователя включена двухфакторная аутентификация
        if user.enable_2fa:
            # Вызываем стандартный метод, который направит на страницу с кодом
            return super().login(request, user)
        else:
            # Если двухфакторная отключена - входим и перенаправляем на главную
            super().login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    
    def pre_authenticate(self, request, **credentials):
        """
        Хук перед аутентификацией, используется для кастомной логики аутентификации.
        """
        return None  # Используем стандартную аутентификацию
        
    def is_email_verification_enabled(self, request):
        """
        Проверка необходимости верификации email в зависимости от настроек.
        """
        return getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', 'none') != 'none'
        
    def render_mail(self, template_prefix, email, context):
        """
        Переопределяем рендеринг письма для вывода кода в консоль.
        """
        mail = super().render_mail(template_prefix, email, context)
        
        # Если это письмо с кодом подтверждения, выводим код в консоль
        if template_prefix == 'account/email/email_confirmation':
            print("\n" + "="*50)
            print(f"CONFIRMATION CODE FOR {email}: {context.get('key', 'NO_KEY_FOUND')}")
            print("="*50 + "\n")
        
        return mail 