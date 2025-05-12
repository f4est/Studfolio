from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    """Расширенная модель пользователя с дополнительными полями"""
    
    USER_TYPE_CHOICES = (
        ('student', _('Студент')),
        ('teacher', _('Преподаватель')),
        ('admin', _('Администратор')),
    )
    
    email = models.EmailField(_('Email адрес'), unique=True)
    user_type = models.CharField(_('Тип пользователя'), max_length=10, choices=USER_TYPE_CHOICES, default='student')
    bio = models.TextField(_('Биография'), blank=True)
    profile_image = models.ImageField(_('Фото профиля'), upload_to='profile_images/', blank=True, null=True)
    date_of_birth = models.DateField(_('Дата рождения'), blank=True, null=True)
    phone_number = models.CharField(_('Номер телефона'), max_length=15, blank=True)

    # Дополнительные поля для студентов
    university = models.CharField(_('Учебное заведение'), max_length=100, blank=True)
    faculty = models.CharField(_('Факультет'), max_length=100, blank=True)
    specialization = models.CharField(_('Специализация'), max_length=100, blank=True)
    year_of_study = models.PositiveSmallIntegerField(_('Курс/Год обучения'), blank=True, null=True)
    
    # Публичный профиль
    is_public = models.BooleanField(_('Публичный профиль'), default=False)
    custom_url = models.SlugField(_('Уникальный URL'), max_length=50, blank=True, unique=True)
    
    # Для уведомлений
    notifications_enabled = models.BooleanField(_('Уведомления включены'), default=True)
    
    # Поля для подписки премиум
    subscription_end_date = models.DateTimeField(_('Дата окончания подписки'), blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    def has_active_subscription(self):
        """Проверяет, имеет ли пользователь активную подписку"""
        if not self.subscription_end_date:
            return False
        return self.subscription_end_date > timezone.now()

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')


class Skill(models.Model):
    """Модель для навыков пользователя"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(_('Название навыка'), max_length=50)
    level = models.PositiveSmallIntegerField(_('Уровень'), choices=[(i, i) for i in range(1, 6)], default=1)
    
    def __str__(self):
        return f"{self.name} ({self.level})"
    
    class Meta:
        verbose_name = _('Навык')
        verbose_name_plural = _('Навыки')
        unique_together = ('user', 'name')


class PortfolioTheme(models.Model):
    """Модель для тем оформления портфолио"""
    THEME_TYPE_CHOICES = (
        ('light', _('Светлая')),
        ('dark', _('Тёмная')),
        ('colorful', _('Цветная')),
        ('minimalist', _('Минималистичная')),
        ('professional', _('Профессиональная')),
        ('creative', _('Креативная')),
    )
    
    name = models.CharField(_('Название темы'), max_length=100)
    type = models.CharField(_('Тип темы'), max_length=20, choices=THEME_TYPE_CHOICES)
    primary_color = models.CharField(_('Основной цвет'), max_length=20, default='#007bff')
    secondary_color = models.CharField(_('Вторичный цвет'), max_length=20, default='#6c757d')
    background_color = models.CharField(_('Цвет фона'), max_length=20, default='#ffffff')
    text_color = models.CharField(_('Цвет текста'), max_length=20, default='#212529')
    css_file = models.FileField(_('CSS файл'), upload_to='portfolio_themes/', blank=True, null=True)
    is_premium = models.BooleanField(_('Премиум тема'), default=False)
    preview_image = models.ImageField(_('Изображение для предпросмотра'), upload_to='theme_previews/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Тема портфолио')
        verbose_name_plural = _('Темы портфолио')


class PortfolioSettings(models.Model):
    """Модель для хранения настроек портфолио пользователя"""
    LAYOUT_CHOICES = (
        ('standard', _('Стандартный')),
        ('modern', _('Современный')),
        ('classic', _('Классический')),
        ('creative', _('Креативный')),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='portfolio_settings')
    theme = models.ForeignKey(PortfolioTheme, on_delete=models.SET_NULL, blank=True, null=True, related_name='users')
    layout = models.CharField(_('Макет'), max_length=20, choices=LAYOUT_CHOICES, default='standard')
    show_skills = models.BooleanField(_('Показывать навыки'), default=True)
    show_education = models.BooleanField(_('Показывать образование'), default=True)
    show_certificates = models.BooleanField(_('Показывать сертификаты'), default=True)
    show_achievements = models.BooleanField(_('Показывать достижения'), default=True)
    show_contact_info = models.BooleanField(_('Показывать контактную информацию'), default=False)
    custom_css = models.TextField(_('Пользовательский CSS'), blank=True)
    custom_domain = models.CharField(_('Пользовательский домен'), max_length=100, blank=True)
    subdomain = models.SlugField(_('Субдомен'), max_length=50, blank=True, null=True, unique=True)
    use_subdomain = models.BooleanField(_('Использовать субдомен'), default=False)
    
    def __str__(self):
        return f"Настройки портфолио {self.user.username}"
    
    def get_full_domain(self):
        """Возвращает полный домен пользователя, включая субдомен"""
        if self.use_subdomain and self.subdomain:
            return f"{self.subdomain}.studfolio.com"
        elif self.custom_domain:
            return self.custom_domain
        return None
    
    def save(self, *args, **kwargs):
        """Автоматически создает субдомен на основе имени пользователя, если не указан"""
        if not self.subdomain and self.user:
            self.subdomain = self.user.username.lower()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Настройки портфолио')
        verbose_name_plural = _('Настройки портфолио')


class SubscriptionCode(models.Model):
    """Модель для кодов активации подписки"""
    code = models.CharField(_('Код активации'), max_length=16, unique=True)
    duration_days = models.PositiveIntegerField(_('Длительность подписки (дней)'), default=30)
    is_used = models.BooleanField(_('Использован'), default=False)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    used_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='subscription_codes')
    used_at = models.DateTimeField(_('Использован'), blank=True, null=True)
    
    def __str__(self):
        return f"Код: {self.code} ({self.duration_days} дней)"
    
    def activate(self, user):
        """Активирует подписку для пользователя"""
        if self.is_used:
            return False
        
        # Устанавливаем дату окончания подписки
        current_date = timezone.now()
        if user.subscription_end_date and user.subscription_end_date > current_date:
            # Если у пользователя уже есть активная подписка, добавляем дни
            user.subscription_end_date += timedelta(days=self.duration_days)
        else:
            # Иначе создаем новую подписку
            user.subscription_end_date = current_date + timedelta(days=self.duration_days)
        
        # Сохраняем информацию об использовании кода
        self.is_used = True
        self.used_by = user
        self.used_at = current_date
        self.save()
        
        # Сохраняем пользователя
        user.save()
        
        return True
    
    class Meta:
        verbose_name = _('Код подписки')
        verbose_name_plural = _('Коды подписки')


class ProfileView(models.Model):
    """Модель для отслеживания посещений профиля"""
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='viewed_profiles')
    ip_address = models.GenericIPAddressField(_('IP адрес'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    timestamp = models.DateTimeField(_('Время просмотра'), auto_now_add=True)
    referrer = models.URLField(_('Источник перехода'), max_length=500, blank=True)
    
    class Meta:
        verbose_name = _('Просмотр профиля')
        verbose_name_plural = _('Просмотры профиля')
        indexes = [
            models.Index(fields=['profile', 'timestamp']),
        ]
    
    def __str__(self):
        viewer_info = self.viewer.username if self.viewer else self.ip_address
        return f"{viewer_info} просмотрел {self.profile.username} в {self.timestamp}"
