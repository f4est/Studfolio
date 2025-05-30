# Generated by Django 5.2.1 on 2025-05-11 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('organizer', models.CharField(max_length=100, verbose_name='Организатор')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('date', models.DateField(verbose_name='Дата')),
                ('place', models.CharField(blank=True, max_length=50, verbose_name='Занятое место')),
                ('achievement_file', models.FileField(blank=True, null=True, upload_to='achievements/', verbose_name='Подтверждающий документ')),
                ('achievement_url', models.URLField(blank=True, verbose_name='Ссылка на подтверждение')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
            ],
            options={
                'verbose_name': 'Достижение',
                'verbose_name_plural': 'Достижения',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('issuer', models.CharField(max_length=100, verbose_name='Выдан')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('certificate_id', models.CharField(blank=True, max_length=100, verbose_name='Номер сертификата')),
                ('issue_date', models.DateField(verbose_name='Дата выдачи')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='Срок действия')),
                ('certificate_file', models.FileField(blank=True, null=True, upload_to='certificates/', verbose_name='Файл сертификата')),
                ('certificate_url', models.URLField(blank=True, verbose_name='Ссылка на сертификат')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
            ],
            options={
                'verbose_name': 'Сертификат',
                'verbose_name_plural': 'Сертификаты',
                'ordering': ['-issue_date'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='project_images/', verbose_name='Изображение')),
                ('url', models.URLField(blank=True, verbose_name='Ссылка на проект')),
                ('github_url', models.URLField(blank=True, verbose_name='Ссылка на GitHub')),
                ('technologies', models.CharField(blank=True, max_length=200, verbose_name='Используемые технологии')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата завершения')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Избранный проект')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст отзыва')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Оценка')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Одобрен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ['-created_at'],
            },
        ),
    ]
