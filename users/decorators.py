"""
Декораторы для проверки доступа к premium-функциям.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

from .premium_features import can_use_feature, check_limit_exceeded

def require_premium(feature_name, redirect_url='users:subscription'):
    """
    Декоратор для проверки доступа к премиум-функциям.
    
    Args:
        feature_name: Название функции из premium_features
        redirect_url: URL для перенаправления при отсутствии доступа
        
    Returns:
        Декоратор функции
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Проверяем, может ли пользователь использовать функцию
            if not request.user.is_authenticated:
                return redirect('account_login')
            
            if can_use_feature(request.user, feature_name):
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(
                    request, 
                    _('Эта функция доступна только для пользователей с премиум-подпиской. '
                      'Перейдите на премиум, чтобы получить доступ.')
                )
                return redirect(redirect_url)
        return _wrapped_view
    return decorator

def check_resource_limit(limit_name, count_function, error_message=None):
    """
    Декоратор для проверки лимитов ресурсов (количество проектов, сертификатов и т.д.).
    
    Args:
        limit_name: Название лимита из premium_features
        count_function: Функция, которая возвращает текущее количество ресурсов для пользователя
        error_message: Сообщение об ошибке (опционально)
        
    Returns:
        Декоратор функции
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')
            
            # Получаем текущее количество ресурсов
            current_count = count_function(request.user)
            
            # Проверяем, не превышен ли лимит
            if check_limit_exceeded(request.user, limit_name, current_count):
                message = error_message or _(
                    'Вы достигли лимита для этого ресурса. '
                    'Перейдите на премиум-подписку, чтобы добавить больше.'
                )
                messages.warning(request, message)
                return redirect('users:subscription')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def premium_feature_context(feature_list):
    """
    Декоратор для добавления информации о доступности премиум-функций в контекст шаблона.
    
    Args:
        feature_list: Список названий функций для проверки
        
    Returns:
        Декоратор функции
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Проверяем, является ли ответ TemplateResponse
            if hasattr(response, 'context_data'):
                premium_features = {}
                if request.user.is_authenticated:
                    for feature in feature_list:
                        premium_features[feature] = can_use_feature(request.user, feature)
                
                response.context_data['premium_features'] = premium_features
                response.context_data['has_premium'] = request.user.is_authenticated and request.user.has_active_subscription()
            
            return response
        return _wrapped_view
    return decorator 