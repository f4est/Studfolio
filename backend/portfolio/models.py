from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Portfolio(models.Model):
    """Модель портфолио студента"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio',
        verbose_name='Пользователь'
    )
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    is_public = models.BooleanField(default=True, verbose_name='Публичное портфолио')
    theme = models.CharField(max_length=50, default='default', verbose_name='Тема оформления')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Портфолио'
        verbose_name_plural = 'Портфолио'
        ordering = ['-updated_at']

    def __str__(self):
        return f'Портфолио {self.user.username}'


class AboutSection(models.Model):
    """Раздел 'Обо мне' в портфолио"""
    portfolio = models.OneToOneField(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='about',
        verbose_name='Портфолио'
    )
    content = models.TextField(verbose_name='Содержание')
    photo = models.ImageField(
        upload_to='portfolio/about/',
        null=True,
        blank=True,
        verbose_name='Фотография'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Раздел "Обо мне"'
        verbose_name_plural = 'Разделы "Обо мне"'

    def __str__(self):
        return f'Обо мне - {self.portfolio.user.username}'


class Education(models.Model):
    """Модель образования в портфолио"""
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='educations',
        verbose_name='Портфолио'
    )
    institution = models.CharField(max_length=255, verbose_name='Учебное заведение')
    degree = models.CharField(max_length=255, verbose_name='Степень/Специальность')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_current = models.BooleanField(default=False, verbose_name='Текущее место учебы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образование'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.institution} - {self.portfolio.user.username}'


class Skill(models.Model):
    """Модель навыка в портфолио"""
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name='Портфолио'
    )
    name = models.CharField(max_length=100, verbose_name='Название')
    level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Уровень (1-5)'
    )
    category = models.CharField(max_length=100, blank=True, verbose_name='Категория')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['-level', 'name']
        unique_together = ['portfolio', 'name']

    def __str__(self):
        return f'{self.name} ({self.level}) - {self.portfolio.user.username}'


class Project(models.Model):
    """Модель проекта в портфолио"""
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Портфолио'
    )
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='portfolio/projects/',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    url = models.URLField(blank=True, verbose_name='URL проекта')
    github_url = models.URLField(blank=True, verbose_name='GitHub URL')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    is_ongoing = models.BooleanField(default=False, verbose_name='В процессе')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-start_date', 'title']

    def __str__(self):
        return f'{self.title} - {self.portfolio.user.username}'


class Certificate(models.Model):
    """Модель сертификата в портфолио"""
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name='Портфолио'
    )
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    issuer = models.CharField(max_length=255, verbose_name='Выдан')
    issue_date = models.DateField(verbose_name='Дата выдачи')
    expiration_date = models.DateField(null=True, blank=True, verbose_name='Дата истечения')
    description = models.TextField(blank=True, verbose_name='Описание')
    credential_id = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='ID сертификата'
    )
    credential_url = models.URLField(blank=True, verbose_name='URL сертификата')
    file = models.FileField(
        upload_to='portfolio/certificates/',
        null=True,
        blank=True,
        verbose_name='Файл сертификата'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'
        ordering = ['-issue_date']

    def __str__(self):
        return f'{self.title} - {self.portfolio.user.username}'


class PortfolioComment(models.Model):
    """Модель комментария к портфолио"""
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Портфолио'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_comments',
        verbose_name='Автор'
    )
    section = models.CharField(max_length=50, verbose_name='Раздел портфолио')
    text = models.TextField(verbose_name='Текст комментария')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name='Оценка (1-5)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Комментарий к портфолио'
        verbose_name_plural = 'Комментарии к портфолио'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий от {self.author.username} к {self.portfolio.user.username}' 