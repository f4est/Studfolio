from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from users.models import CustomUser

class SupportTicket(models.Model):
    """Модель для тикетов поддержки"""
    STATUS_CHOICES = (
        ('new', _('Новый')),
        ('in_progress', _('В обработке')),
        ('waiting', _('Ожидает ответа пользователя')),
        ('resolved', _('Решен')),
        ('closed', _('Закрыт')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
        ('urgent', _('Срочный')),
    )
    
    CATEGORY_CHOICES = (
        ('account', _('Аккаунт')),
        ('subscription', _('Подписка')),
        ('portfolio', _('Портфолио')),
        ('projects', _('Проекты')),
        ('certificates', _('Сертификаты')),
        ('achievements', _('Достижения')),
        ('technical', _('Технические вопросы')),
        ('other', _('Другое')),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(_('Тема'), max_length=255)
    category = models.CharField(_('Категория'), max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(_('Описание проблемы'))
    status = models.CharField(_('Статус'), max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(_('Приоритет'), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)
    assigned_to = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets',
        limit_choices_to={'user_type__in': ['admin', 'support']}
    )
    resolved_at = models.DateTimeField(_('Решен'), null=True, blank=True)
    is_closed = models.BooleanField(_('Закрыт'), default=False)
    
    def __str__(self):
        return f"Тикет #{self.id}: {self.subject}"
    
    def resolve(self):
        """Отмечает тикет как решенный"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    def close(self):
        """Закрывает тикет"""
        self.status = 'closed'
        self.is_closed = True
        if not self.resolved_at:
            self.resolved_at = timezone.now()
        self.save()
    
    def reopen(self):
        """Переоткрывает тикет"""
        self.status = 'in_progress'
        self.is_closed = False
        self.resolved_at = None
        self.save()
    
    class Meta:
        verbose_name = _('Тикет поддержки')
        verbose_name_plural = _('Тикеты поддержки')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['user', 'created_at']),
        ]


class TicketAttachment(models.Model):
    """Модель для вложений к тикетам"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(_('Файл'), upload_to='support_attachments/%Y/%m/')
    file_name = models.CharField(_('Имя файла'), max_length=255)
    uploaded_at = models.DateTimeField(_('Загружен'), auto_now_add=True)
    
    def __str__(self):
        return f"Вложение {self.file_name} к тикету #{self.ticket.id}"
    
    class Meta:
        verbose_name = _('Вложение к тикету')
        verbose_name_plural = _('Вложения к тикетам')


class TicketResponse(models.Model):
    """Модель для ответов на тикеты"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ticket_responses')
    content = models.TextField(_('Содержание'))
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    is_internal_note = models.BooleanField(_('Внутренняя заметка'), default=False, 
                                          help_text=_('Отметьте, если это внутренняя заметка, видимая только сотрудникам поддержки'))
    
    def __str__(self):
        return f"Ответ на тикет #{self.ticket.id} от {self.user.username}"
    
    class Meta:
        verbose_name = _('Ответ на тикет')
        verbose_name_plural = _('Ответы на тикеты')
        ordering = ['created_at']


class SupportCategory(models.Model):
    """Модель для категорий в базе знаний"""
    name = models.CharField(_('Название'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=120, unique=True)
    description = models.TextField(_('Описание'), blank=True)
    icon = models.CharField(_('Иконка FontAwesome'), max_length=50, blank=True, 
                           help_text=_('Например: fa-question-circle'))
    order = models.PositiveIntegerField(_('Порядок'), default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Категория поддержки')
        verbose_name_plural = _('Категории поддержки')
        ordering = ['order', 'name']


class KnowledgeBaseArticle(models.Model):
    """Модель для статей базы знаний"""
    title = models.CharField(_('Заголовок'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=280, unique=True)
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE, related_name='articles')
    content = models.TextField(_('Содержание'))
    is_published = models.BooleanField(_('Опубликовано'), default=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)
    views_count = models.PositiveIntegerField(_('Количество просмотров'), default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Статья базы знаний')
        verbose_name_plural = _('Статьи базы знаний')
        ordering = ['category', 'title']
