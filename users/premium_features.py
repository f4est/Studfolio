"""
Этот модуль определяет премиум-функции и ограничения для разных типов пользователей.
"""

# Ограничения для обычных пользователей (без подписки)
STANDARD_LIMITS = {
    'max_projects': 5,        # Максимальное количество проектов
    'max_certificates': 3,     # Максимальное количество сертификатов
    'max_achievements': 3,     # Максимальное количество достижений
    'max_skills': 10,          # Максимальное количество навыков
    'analytics_period': 30,    # Период аналитики в днях
    'theme_access': False,     # Доступ к премиум темам
    'subdomain_access': False, # Возможность использовать поддомен
    'custom_domain': False,    # Возможность использовать пользовательский домен
    'custom_css': False,       # Возможность использовать пользовательский CSS
    'api_access': False,       # Доступ к API
    'watermark': True,         # Наличие водяного знака
    'advanced_analytics': False, # Расширенная аналитика
    'email_notifications': False, # Уведомления по электронной почте
    'visibility_settings': False, # Расширенные настройки видимости
    'language_translation': False, # Перевод портфолио на другие языки
}

# Ограничения для премиум пользователей (с активной подпиской)
PREMIUM_LIMITS = {
    'max_projects': float('inf'),  # Неограниченное количество проектов
    'max_certificates': float('inf'), # Неограниченное количество сертификатов
    'max_achievements': float('inf'), # Неограниченное количество достижений
    'max_skills': float('inf'),      # Неограниченное количество навыков
    'analytics_period': 365,         # Расширенный период аналитики (1 год)
    'theme_access': True,           # Доступ к премиум темам
    'subdomain_access': True,      # Возможность использовать поддомен
    'custom_domain': True,         # Возможность использовать пользовательский домен
    'custom_css': True,            # Возможность использовать пользовательский CSS
    'api_access': True,            # Доступ к API
    'watermark': False,            # Отсутствие водяного знака
    'advanced_analytics': True,    # Расширенная аналитика
    'email_notifications': True,   # Уведомления по электронной почте
    'visibility_settings': True,   # Расширенные настройки видимости
    'language_translation': True,  # Перевод портфолио на другие языки
}

def get_user_limits(user):
    """
    Возвращает ограничения для конкретного пользователя в зависимости от наличия подписки.
    
    Args:
        user: Экземпляр пользователя (CustomUser)
        
    Returns:
        dict: Словарь с ограничениями
    """
    if user.has_active_subscription():
        return PREMIUM_LIMITS
    return STANDARD_LIMITS

def can_use_feature(user, feature_name):
    """
    Проверяет, может ли пользователь использовать определенную функцию.
    
    Args:
        user: Экземпляр пользователя (CustomUser)
        feature_name: Название функции (строка)
        
    Returns:
        bool: True, если пользователь может использовать функцию, иначе False
    """
    limits = get_user_limits(user)
    return limits.get(feature_name, False)

def get_limit_value(user, limit_name):
    """
    Возвращает числовое значение ограничения для пользователя.
    
    Args:
        user: Экземпляр пользователя (CustomUser)
        limit_name: Название ограничения (строка)
        
    Returns:
        int/float: Значение ограничения
    """
    limits = get_user_limits(user)
    return limits.get(limit_name, 0)

def check_limit_exceeded(user, limit_name, current_count):
    """
    Проверяет, превышено ли ограничение для пользователя.
    
    Args:
        user: Экземпляр пользователя (CustomUser)
        limit_name: Название ограничения (строка)
        current_count: Текущее количество (int)
        
    Returns:
        bool: True, если ограничение превышено, иначе False
    """
    limit = get_limit_value(user, limit_name)
    return current_count >= limit 