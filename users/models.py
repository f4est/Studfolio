from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, email_confirmed

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    """Логируем успешный вход в систему"""
    print(f"\n{'='*50}")
    print(f"User logged in: {user.username} (Email: {user.email})")
    print(f"{'='*50}\n")

@receiver(email_confirmed)
def email_confirmed_callback(sender, request, email_address, **kwargs):
    """Логируем подтверждение email"""
    print(f"\n{'='*50}")
    print(f"Email confirmed: {email_address.email}")
    print(f"{'='*50}\n")

class CustomUser(AbstractUser):
    """Расширенная модель пользователя"""
    USER_TYPE_CHOICES = (
        ('student', _('Студент')),
        ('teacher', _('Преподаватель')),
        ('employer', _('Работодатель')),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    university = models.CharField(max_length=100, blank=True, null=True)
    faculty = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    enable_2fa = models.BooleanField(default=False, verbose_name=_('Включить двухфакторную аутентификацию'), 
                                      help_text=_('При включенной опции вам потребуется вводить код подтверждения при входе.'))
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name=_('Фото профиля'))
    
    def has_active_subscription(self):
        """Проверяет, есть ли у пользователя активная подписка"""
        if not self.subscription_end_date:
            return False
        return self.subscription_end_date > timezone.now()
    
    def get_subscription_days_left(self):
        """Возвращает количество оставшихся дней подписки"""
        if not self.subscription_end_date:
            return 0
        days_left = (self.subscription_end_date - timezone.now()).days
        return max(0, days_left)

class Skill(models.Model):
    """Модель навыков пользователя"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'name')
        ordering = ['name']

class Project(models.Model):
    """Модель проектов пользователя"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=200, blank=True)
    link = models.URLField(blank=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

class Certificate(models.Model):
    """Модель сертификатов пользователя"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_certificates')
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    issue_date = models.DateField()
    link = models.URLField(blank=True)
    image = models.ImageField(upload_to='certificates/', blank=True, null=True)
    
    class Meta:
        ordering = ['-issue_date']

class Achievement(models.Model):
    """Модель достижений пользователя"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_achievements')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organizer = models.CharField(max_length=200)
    date = models.DateField()
    place = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    
    class Meta:
        ordering = ['-date']

class Review(models.Model):
    """Модель отзывов о пользователе"""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    text = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

class ProfileView(models.Model):
    """Модель для отслеживания просмотров профиля"""
    profile_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='profile_views')
    viewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='viewed_profiles')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']

class ProjectView(models.Model):
    """Модель для отслеживания просмотров проектов"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_viewed_projects')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']

class PortfolioTheme(models.Model):
    """Модель тем для портфолио"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_premium = models.BooleanField(default=False)
    preview_image = models.ImageField(upload_to='themes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']

class PortfolioSettings(models.Model):
    """Модель настроек портфолио пользователя"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='portfolio_settings')
    theme = models.ForeignKey(PortfolioTheme, on_delete=models.SET_NULL, null=True, blank=True)
    show_skills = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_certificates = models.BooleanField(default=True)
    show_achievements = models.BooleanField(default=True)
    show_reviews = models.BooleanField(default=True)
    custom_css = models.TextField(blank=True)
    custom_js = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Настройки портфолио')
        verbose_name_plural = _('Настройки портфолио')

class SubscriptionCode(models.Model):
    """Модель кодов активации подписки"""
    code = models.CharField(max_length=20, unique=True)
    duration_days = models.IntegerField(default=30)
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def activate(self, user):
        """Активирует код подписки для пользователя"""
        if self.is_used:
            return False
        
        self.is_used = True
        self.used_by = user
        self.used_at = timezone.now()
        self.save()
        
        # Обновляем дату окончания подписки пользователя
        if user.subscription_end_date and user.subscription_end_date > timezone.now():
            # Если подписка еще активна, добавляем дни к текущей дате окончания
            user.subscription_end_date += timezone.timedelta(days=self.duration_days)
        else:
            # Если подписка неактивна, устанавливаем новую дату окончания
            user.subscription_end_date = timezone.now() + timezone.timedelta(days=self.duration_days)
        
        user.save()
        return True
