from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser


class Project(models.Model):
    """Модель проекта в портфолио"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(_('Название'), max_length=100)
    description = models.TextField(_('Описание'))
    image = models.ImageField(_('Изображение'), upload_to='project_images/', blank=True, null=True)
    url = models.URLField(_('Ссылка на проект'), blank=True)
    github_url = models.URLField(_('Ссылка на GitHub'), blank=True)
    technologies = models.CharField(_('Используемые технологии'), max_length=200, blank=True)
    start_date = models.DateField(_('Дата начала'), blank=True, null=True)
    end_date = models.DateField(_('Дата завершения'), blank=True, null=True)
    is_featured = models.BooleanField(_('Избранный проект'), default=False)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')
        ordering = ['-created_at']


class Certificate(models.Model):
    """Модель сертификата в портфолио"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(_('Название'), max_length=100)
    issuer = models.CharField(_('Выдан'), max_length=100)
    description = models.TextField(_('Описание'), blank=True)
    certificate_id = models.CharField(_('Номер сертификата'), max_length=100, blank=True)
    issue_date = models.DateField(_('Дата выдачи'))
    expiry_date = models.DateField(_('Срок действия'), blank=True, null=True)
    certificate_file = models.FileField(_('Файл сертификата'), upload_to='certificates/', blank=True, null=True)
    certificate_url = models.URLField(_('Ссылка на сертификат'), blank=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    
    # Новые поля, используемые в шаблоне
    credential_id = models.CharField(_('ID сертификата'), max_length=100, blank=True)
    credential_url = models.URLField(_('URL для проверки'), blank=True)
    issuing_organization = models.CharField(_('Выдавшая организация'), max_length=100, blank=True)
    expiration_date = models.DateField(_('Дата окончания'), blank=True, null=True)
    image = models.ImageField(_('Изображение сертификата'), upload_to='certificates_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.issuer}"
    
    class Meta:
        verbose_name = _('Сертификат')
        verbose_name_plural = _('Сертификаты')
        ordering = ['-issue_date']


class Achievement(models.Model):
    """Модель достижения (участие в олимпиадах, конкурсах и т.д.)"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(_('Название'), max_length=100)
    organizer = models.CharField(_('Организатор'), max_length=100)
    description = models.TextField(_('Описание'), blank=True)
    date = models.DateField(_('Дата'))
    place = models.CharField(_('Занятое место'), max_length=50, blank=True)
    achievement_file = models.FileField(_('Подтверждающий документ'), upload_to='achievements/', blank=True, null=True)
    achievement_url = models.URLField(_('Ссылка на подтверждение'), blank=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    
    # Новые поля, используемые в шаблоне
    category = models.CharField(_('Категория'), max_length=100, blank=True)
    date_received = models.DateField(_('Дата получения'), null=True, blank=True)
    issuing_organization = models.CharField(_('Выдавшая организация'), max_length=100, blank=True)
    image = models.ImageField(_('Изображение'), upload_to='achievements_images/', blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Достижение')
        verbose_name_plural = _('Достижения')
        ordering = ['-date']


class Review(models.Model):
    """Модель отзыва преподавателя/ментора"""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_received')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_given')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='reviews', blank=True, null=True)
    text = models.TextField(_('Текст отзыва'))
    rating = models.PositiveSmallIntegerField(_('Оценка'), choices=[(i, i) for i in range(1, 6)])
    is_approved = models.BooleanField(_('Одобрен'), default=False)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    
    def __str__(self):
        return f"Отзыв от {self.reviewer.username} для {self.student.username}"
    
    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']
        unique_together = ('reviewer', 'student', 'project')


class ProjectPost(models.Model):
    """Модель публикации о проекте в ленте"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_posts')
    content = models.TextField(_('Содержание'))
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)
    
    def __str__(self):
        return f"Пост о проекте {self.project.title} от {self.author.username}"
    
    def like_count(self):
        return self.likes.count()
    
    class Meta:
        verbose_name = _('Пост о проекте')
        verbose_name_plural = _('Посты о проектах')
        ordering = ['-created_at']


class ProjectComment(models.Model):
    """Модель комментария к публикации о проекте"""
    post = models.ForeignKey(ProjectPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_comments')
    text = models.TextField(_('Текст комментария'))
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    
    def __str__(self):
        return f"Комментарий от {self.author.username} к посту {self.post.id}"
    
    class Meta:
        verbose_name = _('Комментарий к посту')
        verbose_name_plural = _('Комментарии к постам')
        ordering = ['created_at']


class ProjectView(models.Model):
    """Модель для отслеживания просмотров проекта"""
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='viewed_projects')
    ip_address = models.GenericIPAddressField(_('IP адрес'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    timestamp = models.DateTimeField(_('Время просмотра'), auto_now_add=True)
    referrer = models.URLField(_('Источник перехода'), max_length=500, blank=True)
    
    class Meta:
        verbose_name = _('Просмотр проекта')
        verbose_name_plural = _('Просмотры проекта')
        indexes = [
            models.Index(fields=['project', 'timestamp']),
        ]
    
    def __str__(self):
        viewer_info = self.viewer.username if self.viewer else self.ip_address
        return f"{viewer_info} просмотрел проект \"{self.project.title}\" в {self.timestamp}"
