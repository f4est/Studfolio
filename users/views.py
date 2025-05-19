from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import Template, Context
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.utils import timezone
from datetime import timedelta
import json
import os
import logging

from .models import (
    CustomUser, Skill, Project, Certificate, Achievement,
    Review, ProfileView, ProjectView, PortfolioTheme,
    PortfolioSettings, SubscriptionCode
)
from .forms import (
    ProfileForm, SkillForm, ProjectForm, CertificateForm,
    AchievementForm, ReviewForm, PortfolioSettingsForm,
    PortfolioAdvancedSettingsForm, SubscriptionActivationForm,
    SecuritySettingsForm
)
from .decorators import require_premium, check_resource_limit, premium_feature_context
from .premium_features import can_use_feature, get_limit_value

import random
import string
import io
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Q, Sum, Avg
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from collections import defaultdict
from django.http import JsonResponse
import matplotlib.pyplot as plt
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.contrib.auth import login, authenticate

# Импортируем модели из portfolio для правильной работы с проектами
from portfolio.models import Project as PortfolioProject
from portfolio.models import Certificate as PortfolioCertificate
from portfolio.models import Achievement as PortfolioAchievement
from portfolio.models import Review as PortfolioReview


@login_required
def profile_view(request):
    """Отображение профиля пользователя"""
    # Получаем все элементы портфолио
    projects = PortfolioProject.objects.filter(user=request.user).order_by('-created_at')[:5]
    certificates = PortfolioCertificate.objects.filter(user=request.user).order_by('-issue_date')[:5]
    achievements = PortfolioAchievement.objects.filter(user=request.user).order_by('-date')[:5]
    skills = Skill.objects.filter(user=request.user).order_by('name')
    
    # Для студентов получаем отзывы
    reviews = []
    if request.user.user_type == 'student':
        reviews = PortfolioReview.objects.filter(student=request.user, is_approved=True).order_by('-created_at')[:3]
    
    context = {
        'projects': projects,
        'certificates': certificates,
        'achievements': achievements,
        'skills': skills,
        'reviews': reviews,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    """Редактирование профиля пользователя"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль успешно обновлен!'))
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def skill_add_view(request):
    """Добавление нового навыка"""
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            
            # Проверяем, есть ли уже такой навык
            if Skill.objects.filter(user=request.user, name=skill.name).exists():
                messages.error(request, _('Такой навык уже существует!'))
                return redirect('users:profile')
                
            skill.save()
            messages.success(request, _('Навык успешно добавлен!'))
            return redirect('users:profile')
    else:
        form = SkillForm()
    
    return render(request, 'users/skill_form.html', {'form': form, 'action': 'add'})


@login_required
def skill_edit_view(request, skill_id):
    """Редактирование навыка"""
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, _('Навык успешно обновлен!'))
            return redirect('users:profile')
    else:
        form = SkillForm(instance=skill)
    
    return render(request, 'users/skill_form.html', {'form': form, 'action': 'edit', 'skill': skill})


@login_required
def skill_delete_view(request, skill_id):
    """Удаление навыка"""
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    
    if request.method == 'POST':
        skill.delete()
        messages.success(request, _('Навык успешно удален!'))
        return redirect('users:profile')
    
    return render(request, 'users/skill_confirm_delete.html', {'skill': skill})


def public_profile(request, username):
    """Просмотр публичного профиля пользователя"""
    user = get_object_or_404(CustomUser, username=username)
    
    # Проверяем, является ли профиль публичным
    if not user.is_public and request.user != user and not request.user.is_superuser:
        # Если профиль приватный и просматривает не владелец/админ
        return render(request, 'users/private_profile.html', {'username': username})
    
    # Получаем проекты, достижения, сертификаты пользователя из portfolio моделей
    projects = PortfolioProject.objects.filter(user=user).order_by('-created_at')
    achievements = PortfolioAchievement.objects.filter(user=user).order_by('-date')
    certificates = PortfolioCertificate.objects.filter(user=user).order_by('-issue_date')
    skills = Skill.objects.filter(user=user).order_by('-level')
    
    # Получаем только одобренные отзывы
    reviews = PortfolioReview.objects.filter(student=user, is_approved=True).order_by('-created_at')
    
    # Отладочная информация
    print(f"Пользователь: {user.username}, ID: {user.id}")
    print(f"Проектов (portfolio): {projects.count()}")
    print(f"Отзывов (portfolio): {reviews.count()}")
    print(f"Отзывы: {[r.id for r in reviews]}")
    
    # Определяем, может ли текущий пользователь оставить отзыв
    can_add_review = False
    if request.user.is_authenticated and request.user != user:
        if request.user.user_type in ['teacher', 'admin'] and user.user_type == 'student':
            can_add_review = True
    
    context = {
        'profile_user': user,
        'projects': projects,
        'achievements': achievements,
        'certificates': certificates,
        'skills': skills,
        'reviews': reviews,
        'can_add_review': can_add_review,
        'is_teacher': request.user.is_authenticated and request.user.user_type == 'teacher',
        'is_admin': request.user.is_authenticated and request.user.user_type == 'admin',
        'is_student': request.user.is_authenticated and request.user.user_type == 'student',
    }
    
    return render(request, 'users/public_profile.html', context)


@login_required
def portfolio_settings_view(request):
    """Настройки портфолио пользователя"""
    # Получаем или создаем объект настроек портфолио для пользователя
    portfolio_settings, created = PortfolioSettings.objects.get_or_create(user=request.user)
    
    # Проверяем, имеет ли пользователь активную подписку
    is_premium = request.user.has_active_subscription()
    
    # Получаем все доступные темы
    free_themes = PortfolioTheme.objects.filter(is_premium=False)
    premium_themes = PortfolioTheme.objects.filter(is_premium=True)
    
    if request.method == 'POST':
        settings_form = PortfolioSettingsForm(request.POST, instance=portfolio_settings)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, _('Настройки портфолио успешно сохранены!'))
            return redirect('users:portfolio_settings')
    else:
        settings_form = PortfolioSettingsForm(instance=portfolio_settings)
    
    context = {
        'is_premium': is_premium,
        'portfolio_settings': portfolio_settings,
        'settings_form': settings_form,
        'free_themes': free_themes,
        'premium_themes': premium_themes,
    }
    
    return render(request, 'users/portfolio_settings.html', context)


@login_required
def subscription_view(request):
    """Страница управления подпиской"""
    
    # Обрабатываем активацию кода, если это POST-запрос
    if request.method == 'POST':
        code_value = request.POST.get('activation_code')
        
        if not code_value:
            messages.error(request, _('Пожалуйста, введите код активации.'))
            return redirect('users:subscription')
        
        try:
            # Ищем код в базе данных
            subscription_code = SubscriptionCode.objects.get(code=code_value, is_used=False)
            
            # Активируем код для пользователя
            if subscription_code.activate(request.user):
                messages.success(
                    request, 
                    _('Код активирован! Ваша подписка продлена на %(days)s дней.') % 
                    {'days': subscription_code.duration_days}
                )
            else:
                messages.error(request, _('Этот код уже был использован.'))
        except SubscriptionCode.DoesNotExist:
            messages.error(request, _('Неверный код активации или код уже использован.'))
    
    return render(request, 'users/subscription.html')


@login_required
def generate_subscription_code(request):
    """Функция для генерации кода подписки (для демонстрации)"""
    if not request.user.is_superuser:
        messages.error(request, _('У вас нет прав для выполнения этой операции.'))
        return redirect('users:subscription')
    
    # Генерируем уникальный код
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    
    # Создаем код подписки
    subscription_code = SubscriptionCode.objects.create(
        code=code,
        duration_days=30
    )
    
    messages.success(
        request, 
        _('Код подписки успешно создан: %(code)s') % {'code': code}
    )
    
    return redirect('users:subscription')


@login_required
def admin_subscription_codes_view(request):
    """Страница администрирования кодов подписки"""
    # Проверяем, является ли пользователь администратором
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, _('У вас нет прав для доступа к этой странице.'))
        return redirect('users:subscription')
    
    # Получаем все коды подписки
    subscription_codes = SubscriptionCode.objects.all().order_by('-created_at')
    
    # Обработка формы для создания нового кода
    if request.method == 'POST':
        if 'generate_code' in request.POST:
            # Генерируем уникальный код
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            duration_days = int(request.POST.get('duration_days', 30))
            
            # Создаем код подписки
            subscription_code = SubscriptionCode.objects.create(
                code=code,
                duration_days=duration_days
            )
            
            messages.success(
                request, 
                _('Код подписки успешно создан: %(code)s') % {'code': code}
            )
            return redirect('users:admin_subscription_codes')
        
        elif 'delete_code' in request.POST:
            code_id = request.POST.get('code_id')
            try:
                code = SubscriptionCode.objects.get(id=code_id)
                code.delete()
                messages.success(request, _('Код подписки успешно удален.'))
            except SubscriptionCode.DoesNotExist:
                messages.error(request, _('Код подписки не найден.'))
            return redirect('users:admin_subscription_codes')
    
    context = {
        'subscription_codes': subscription_codes,
    }
    
    return render(request, 'users/admin_subscription_codes.html', context)


@login_required
def activate_subscription_code(request):
    """Активация кода подписки пользователем"""
    if request.method == 'POST':
        code_value = request.POST.get('activation_code')
        
        if not code_value:
            messages.error(request, _('Пожалуйста, введите код активации.'))
            return redirect('users:subscription')
        
        try:
            # Ищем код в базе данных
            subscription_code = SubscriptionCode.objects.get(code=code_value, is_used=False)
            
            # Активируем код для пользователя
            if subscription_code.activate(request.user):
                messages.success(
                    request, 
                    _('Код активирован! Ваша подписка продлена на %(days)s дней.') % 
                    {'days': subscription_code.duration_days}
                )
            else:
                messages.error(request, _('Этот код уже был использован.'))
        except SubscriptionCode.DoesNotExist:
            messages.error(request, _('Неверный код активации или код уже использован.'))
        
        return redirect('users:subscription')
    
    return redirect('users:subscription')


@login_required
@require_premium('theme_access')
def apply_portfolio_theme(request, theme_id):
    """Применение выбранной темы к портфолио"""
    # Получаем тему
    theme = get_object_or_404(PortfolioTheme, id=theme_id)
    
    # Проверяем, имеет ли пользователь доступ к премиум-темам
    if theme.is_premium and not can_use_feature(request.user, 'theme_access'):
        messages.error(request, _('Для использования этой темы необходима премиум-подписка.'))
        return redirect('users:portfolio_settings')
    
    # Получаем или создаем настройки портфолио
    portfolio_settings, created = PortfolioSettings.objects.get_or_create(user=request.user)
    
    # Применяем тему
    portfolio_settings.theme = theme
    portfolio_settings.save()
    
    messages.success(request, _('Тема успешно применена!'))
    return redirect('users:portfolio_settings')


@login_required
def preview_portfolio_theme(request, theme_id):
    """Предварительный просмотр темы портфолио"""
    # Получаем тему
    theme = get_object_or_404(PortfolioTheme, id=theme_id)
    
    # Получаем текущие настройки портфолио
    try:
        portfolio_settings = PortfolioSettings.objects.get(user=request.user)
    except PortfolioSettings.DoesNotExist:
        portfolio_settings = None
    
    # Получаем данные пользователя для предпросмотра
    projects = Project.objects.filter(user=request.user)[:3]
    certificates = Certificate.objects.filter(user=request.user)[:2]
    achievements = Achievement.objects.filter(user=request.user)[:2]
    skills = Skill.objects.filter(user=request.user)[:5]
    
    context = {
        'user': request.user,
        'theme': theme,
        'portfolio_settings': portfolio_settings,
        'projects': projects,
        'certificates': certificates,
        'achievements': achievements,
        'skills': skills,
        'is_preview': True,
    }
    
    return render(request, 'users/portfolio_preview.html', context)


def get_client_ip(request):
    """Получение IP-адреса клиента из запроса"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def analytics_view(request):
    """Страница с аналитикой портфолио"""
    # Получаем статистику для профиля пользователя
    profile_views = ProfileView.objects.filter(profile_user=request.user)
    profile_views_count = profile_views.count() or 142  # Фиктивные данные, если нет настоящих
    
    # Получаем статистику для проектов пользователя
    project_views = ProjectView.objects.filter(project__user=request.user)
    project_views_count = project_views.count() or 89  # Фиктивные данные, если нет настоящих
    
    # Фиктивные данные для уникальных посетителей и отзывов
    unique_visitors_count = 28
    reviews_count = 5
    
    # Фиктивные данные для популярных проектов
    popular_projects = [
        {'title': 'Веб-приложение "Студенческий портал"', 'views_count': 42, 'unique_visitors_count': 18, 'average_view_time': '2:35', 'color': '#3498db'},
        {'title': 'Мобильное приложение "ЭкоТрекер"', 'views_count': 37, 'unique_visitors_count': 14, 'average_view_time': '1:58', 'color': '#2ecc71'},
        {'title': 'Дизайн-макет "Интерфейс библиотеки"', 'views_count': 28, 'unique_visitors_count': 12, 'average_view_time': '2:15', 'color': '#e74c3c'}
    ]
    
    # Фиктивные данные городов
    city_data = {
        'Москва': {'count': 36, 'percentage': 42},
        'Санкт-Петербург': {'count': 18, 'percentage': 21},
        'Казань': {'count': 12, 'percentage': 14},
        'Новосибирск': {'count': 8, 'percentage': 9},
        'Екатеринбург': {'count': 6, 'percentage': 7},
        'Другие': {'count': 6, 'percentage': 7}
    }
    
    # Проверяем, имеет ли пользователь активную подписку
    is_premium = request.user.has_active_subscription()
    
    context = {
        'profile_views_count': profile_views_count,
        'project_views_count': project_views_count,
        'unique_visitors_count': unique_visitors_count,
        'reviews_count': reviews_count,
        'popular_projects': popular_projects,
        'city_data': city_data,
        'is_premium': is_premium
    }
    
    return render(request, 'users/analytics.html', context)


@login_required
def premium_guide_view(request):
    """Страница с руководством по премиум-функциям"""
    return render(request, 'users/premium_guide.html')


@login_required
def security_settings_view(request):
    """Страница настроек безопасности аккаунта"""
    if request.method == 'POST':
        form = SecuritySettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Настройки безопасности успешно обновлены!'))
            return redirect('users:security_settings')
    else:
        form = SecuritySettingsForm(instance=request.user)
    
    return render(request, 'users/security_settings.html', {'form': form})


@login_required
def search_users(request):
    """Поиск пользователей по различным параметрам"""
    query = request.GET.get('q', '')
    users = None
    
    if query:
        # Поиск по username, first_name, last_name, university
        # и возвращаем только публичные профили
        users = CustomUser.objects.filter(
            models.Q(username__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(university__icontains=query),
            is_public=True
        ).distinct()
        
    return render(request, 'users/search_results.html', {
        'users': users,
        'query': query
    })

