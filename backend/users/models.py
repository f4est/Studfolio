from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Пользовательская модель пользователя с необходимыми ролями.
    """
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Студент'),
        (TEACHER, 'Преподаватель'),
        (ADMIN, 'Администратор'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=STUDENT,
        verbose_name='Роль'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        verbose_name='Фото профиля'
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def is_student(self):
        return self.role == self.STUDENT
    
    def is_teacher(self):
        return self.role == self.TEACHER
    
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser 