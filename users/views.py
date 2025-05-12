from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, Http404
from django.template.loader import get_template
# Удаляем неработающий импорт WeasyPrint
# from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.conf import settings
from django.db import models
import os
import tempfile
import io
from django.utils import timezone
import uuid
import random
import string
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Count, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from collections import defaultdict
from django.http import JsonResponse
import json
from portfolio.models import Project, Certificate, Achievement, Review, ProjectView

# Удаляем попытку импорта WeasyPrint
# try:
#     from weasyprint import HTML, CSS
#     WEASYPRINT_AVAILABLE = True
# except (ImportError, OSError):
#     WEASYPRINT_AVAILABLE = False
#     import logging
#     logger = logging.getLogger(__name__)
#     logger.warning("WeasyPrint не удалось импортировать. Функция генерации PDF будет отключена.")

# Добавляем импорт ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Остальные импорты оставляем без изменений
from .models import CustomUser, Skill, PortfolioTheme, PortfolioSettings, SubscriptionCode, ProfileView
from .forms import ProfileForm, SkillForm, PortfolioSettingsForm, PortfolioAdvancedSettingsForm, SubscriptionActivationForm


@login_required
def profile_view(request):
    """Отображение профиля пользователя"""
    # Получаем все элементы портфолио
    projects = Project.objects.filter(user=request.user).order_by('-created_at')[:5]
    certificates = Certificate.objects.filter(user=request.user).order_by('-issue_date')[:5]
    achievements = Achievement.objects.filter(user=request.user).order_by('-date')[:5]
    skills = Skill.objects.filter(user=request.user).order_by('name')
    
    # Для студентов получаем отзывы
    reviews = []
    if request.user.user_type == 'student':
        reviews = Review.objects.filter(student=request.user, is_approved=True).order_by('-created_at')[:3]
    
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


@login_required
def generate_pdf_resume(request):
    """Генерирует PDF-резюме пользователя с использованием ReportLab"""
    try:
        # Получаем данные пользователя
        user = request.user
        skills = user.skills.all()
        projects = user.projects.all().order_by('-created_at')[:5]
        certificates = user.certificates.all().order_by('-issue_date')[:5]
        achievements = user.achievements.all().order_by('-date')[:5]
        
        # Создаем буфер для PDF
        buffer = io.BytesIO()
        
        # Создаем PDF документ
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)
        
        # Контейнер для элементов PDF
        elements = []
        
        # Стили для PDF
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=1))
        styles.add(ParagraphStyle(name='Bold', fontName='Helvetica-Bold'))
        
        # Заголовок резюме
        elements.append(Paragraph(f"{user.get_full_name()} - Резюме", styles['Title']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Контактная информация
        contact_info = []
        if user.email:
            contact_info.append(f"Email: {user.email}")
        if user.phone_number:
            contact_info.append(f"Телефон: {user.phone_number}")
        if user.university:
            contact_info.append(f"Учебное заведение: {user.university}")
        if user.faculty:
            contact_info.append(f"Факультет: {user.faculty}")
        if user.specialization:
            contact_info.append(f"Специализация: {user.specialization}")
        
        for info in contact_info:
            elements.append(Paragraph(info, styles['Normal']))
        
        elements.append(Spacer(1, 1*cm))
        
        # Биография
        if user.bio:
            elements.append(Paragraph("О себе", styles['Heading2']))
            elements.append(Paragraph(user.bio, styles['Normal']))
            elements.append(Spacer(1, 0.5*cm))
        
        # Навыки
        if skills.exists():
            elements.append(Paragraph("Навыки", styles['Heading2']))
            skill_data = []
            for skill in skills:
                skill_level = "★" * skill.level + "☆" * (5 - skill.level)
                skill_data.append([skill.name, skill_level])
            
            if skill_data:
                skill_table = Table(skill_data, colWidths=[doc.width/2.0]*2)
                skill_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(skill_table)
                elements.append(Spacer(1, 0.5*cm))
        
        # Проекты
        if projects.exists():
            elements.append(Paragraph("Проекты", styles['Heading2']))
            for project in projects:
                elements.append(Paragraph(project.title, styles['Heading3']))
                elements.append(Paragraph(project.description, styles['Normal']))
                if project.technologies:
                    elements.append(Paragraph(f"Технологии: {project.technologies}", styles['Italic']))
                elements.append(Spacer(1, 0.3*cm))
            elements.append(Spacer(1, 0.5*cm))
        
        # Сертификаты
        if certificates.exists():
            elements.append(Paragraph("Сертификаты", styles['Heading2']))
            for cert in certificates:
                elements.append(Paragraph(f"{cert.title} - {cert.issuer}", styles['Heading3']))
                if cert.description:
                    elements.append(Paragraph(cert.description, styles['Normal']))
                elements.append(Paragraph(f"Дата выдачи: {cert.issue_date.strftime('%d.%m.%Y')}", styles['Italic']))
                elements.append(Spacer(1, 0.3*cm))
            elements.append(Spacer(1, 0.5*cm))
        
        # Достижения
        if achievements.exists():
            elements.append(Paragraph("Достижения", styles['Heading2']))
            for achievement in achievements:
                elements.append(Paragraph(f"{achievement.title} - {achievement.organizer}", styles['Heading3']))
                if achievement.description:
                    elements.append(Paragraph(achievement.description, styles['Normal']))
                if achievement.place:
                    elements.append(Paragraph(f"Место: {achievement.place}", styles['Italic']))
                elements.append(Paragraph(f"Дата: {achievement.date.strftime('%d.%m.%Y')}", styles['Italic']))
                elements.append(Spacer(1, 0.3*cm))
        
        # Строим PDF документ
        doc.build(elements)
        
        # PDF из буфера
        pdf = buffer.getvalue()
        buffer.close()
        
        # Создаем HTTP ответ с PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{user.username}_resume.pdf"'
        response.write(pdf)
        
        return response
    
    except Exception as e:
        messages.error(request, f'Ошибка при генерации PDF: {str(e)}')
        return redirect('users:profile')


def public_profile(request, username):
    """Просмотр публичного профиля пользователя"""
    user = get_object_or_404(CustomUser, username=username)
    
    # Проверяем, является ли профиль публичным
    if not user.is_public and request.user != user and not request.user.is_superuser:
        # Если профиль приватный и просматривает не владелец/админ
        return render(request, 'users/private_profile.html', {'username': username})
    
    # Получаем проекты, достижения, сертификаты пользователя
    projects = user.projects.all().order_by('-created_at')
    achievements = user.achievements.all().order_by('-date')
    certificates = user.certificates.all().order_by('-issue_date')
    
    # Если пользователь является авторизованным и не владельцем профиля
    if request.user.is_authenticated and request.user != user:
        # Записываем просмотр профиля для аналитики
        ProfileView.objects.create(
            profile=user,
            viewer=request.user,
            ip_address=request.META.get('REMOTE_ADDR', None),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', '')
        )
    
    # Если у пользователя есть пользовательские настройки портфолио
    try:
        portfolio_settings = user.portfolio_settings
    except:
        portfolio_settings = None
    
    context = {
        'profile_user': user,
        'projects': projects,
        'achievements': achievements,
        'certificates': certificates,
        'portfolio_settings': portfolio_settings,
        'is_owner': request.user == user,
    }
    
    return render(request, 'users/public_profile.html', context)


@login_required
def portfolio_settings_view(request):
    """Настройки портфолио пользователя"""
    # Получаем или создаем объект настроек портфолио для пользователя
    portfolio_settings, created = PortfolioSettings.objects.get_or_create(user=request.user)
    
    # Проверяем, имеет ли пользователь активную подписку
    is_premium = request.user.has_active_subscription()
    
    if request.method == 'POST':
        settings_form = PortfolioSettingsForm(
            request.POST, instance=portfolio_settings, premium=is_premium
        )
        
        if is_premium:
            advanced_form = PortfolioAdvancedSettingsForm(request.POST, instance=portfolio_settings)
            if settings_form.is_valid() and advanced_form.is_valid():
                settings_form.save()
                advanced_form.save()
                messages.success(request, _('Настройки портфолио успешно сохранены!'))
                return redirect('users:portfolio_settings')
        else:
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, _('Настройки портфолио успешно сохранены!'))
                return redirect('users:portfolio_settings')
    else:
        settings_form = PortfolioSettingsForm(instance=portfolio_settings, premium=is_premium)
        if is_premium:
            advanced_form = PortfolioAdvancedSettingsForm(instance=portfolio_settings)
        else:
            advanced_form = None
    
    # Получаем все темы для отображения на странице
    free_themes = PortfolioTheme.objects.filter(is_premium=False)
    premium_themes = PortfolioTheme.objects.filter(is_premium=True)
    
    context = {
        'settings_form': settings_form,
        'advanced_form': advanced_form,
        'free_themes': free_themes,
        'premium_themes': premium_themes,
        'portfolio_settings': portfolio_settings,
        'is_premium': is_premium,
    }
    
    return render(request, 'users/portfolio_settings.html', context)


@login_required
def subscription_view(request):
    """Страница управления подпиской"""
    # Проверяем, имеет ли пользователь активную подписку
    is_premium = request.user.has_active_subscription()
    
    if request.method == 'POST':
        form = SubscriptionActivationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                subscription_code = SubscriptionCode.objects.get(code=code, is_used=False)
                
                # Активируем код подписки
                if subscription_code.activate(request.user):
                    messages.success(
                        request, 
                        _('Подписка успешно активирована! Срок действия: %(days)d дней.') % 
                        {'days': subscription_code.duration_days}
                    )
                    return redirect('users:subscription')
                else:
                    messages.error(request, _('Ошибка активации подписки. Пожалуйста, попробуйте еще раз.'))
            except SubscriptionCode.DoesNotExist:
                messages.error(request, _('Неверный код активации.'))
    else:
        form = SubscriptionActivationForm()
    
    context = {
        'form': form,
        'is_premium': is_premium,
        'subscription_end_date': request.user.subscription_end_date,
    }
    
    return render(request, 'users/subscription.html', context)


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
def apply_portfolio_theme(request, theme_id):
    """Применение выбранной темы к портфолио"""
    # Получаем тему
    theme = get_object_or_404(PortfolioTheme, id=theme_id)
    
    # Проверяем, имеет ли пользователь доступ к премиум-темам
    if theme.is_premium and not request.user.has_active_subscription():
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
    """Страница аналитики просмотров портфолио и проектов"""
    # Проверяем, имеет ли пользователь премиум-подписку
    is_premium = request.user.has_active_subscription()
    
    # Базовая аналитика доступна всем, расширенная - только с премиум-подпиской
    profile = request.user
    
    # Получаем общую статистику
    profile_views_count = ProfileView.objects.filter(profile=profile).count()
    
    # Получаем проекты пользователя
    projects = Project.objects.filter(user=profile)
    project_views = ProjectView.objects.filter(project__in=projects)
    project_views_count = project_views.count()
    
    # Получаем популярные проекты
    popular_projects = projects.annotate(views_count=Count('views')).order_by('-views_count')[:5]
    
    # Получаем источники трафика
    top_referrers = ProfileView.objects.filter(profile=profile, referrer__isnull=False, referrer__gt='').values('referrer').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Если пользователь имеет премиум-подписку, предоставляем расширенную аналитику
    if is_premium:
        # Данные просмотров профиля по дням за последний месяц
        profile_views_by_date = ProfileView.objects.filter(
            profile=profile, 
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Данные просмотров проектов по дням за последний месяц
        project_views_by_date = ProjectView.objects.filter(
            project__in=projects,
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Преобразуем данные в формат для отображения на графике
        profile_chart_data = {str(item['date']): item['count'] for item in profile_views_by_date}
        project_chart_data = {str(item['date']): item['count'] for item in project_views_by_date}
        
        # Информация о пользователях, просматривающих профиль
        viewer_stats = ProfileView.objects.filter(profile=profile, viewer__isnull=False).values('viewer').annotate(count=Count('id')).order_by('-count')[:10]
        viewers = CustomUser.objects.filter(id__in=[item['viewer'] for item in viewer_stats])
        viewers_dict = {viewer.id: {'username': viewer.username, 'profile_image': viewer.profile_image.url if viewer.profile_image else None} for viewer in viewers}
        
        viewers_data = []
        for stat in viewer_stats:
            viewer_id = stat['viewer']
            if viewer_id in viewers_dict:
                viewers_data.append({
                    'viewer': viewers_dict[viewer_id],
                    'count': stat['count']
                })
    else:
        profile_chart_data = None
        project_chart_data = None
        viewers_data = None
    
    context = {
        'is_premium': is_premium,
        'profile_views_count': profile_views_count,
        'project_views_count': project_views_count,
        'popular_projects': popular_projects,
        'top_referrers': top_referrers,
        'profile_chart_data': json.dumps(profile_chart_data) if profile_chart_data else None,
        'project_chart_data': json.dumps(project_chart_data) if project_chart_data else None,
        'viewers_data': viewers_data,
    }
    
    return render(request, 'users/analytics.html', context)


@login_required
def premium_guide_view(request):
    """Страница с подробным руководством по использованию возможностей премиум-подписки"""
    return render(request, 'premium_guide.html')


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
