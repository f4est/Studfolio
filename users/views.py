from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, Http404
from django.template.loader import get_template
# Импортируем WeasyPrint, но обрабатываем ошибку импорта
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML, CSS
    # Проверяем правильность загрузки библиотек с надежным обходом ошибок
    try:
        # Пустой HTML для тестирования
        test_html = HTML(string='<html><body>Test</body></html>')
        # Если дошли до этой точки без исключений, все работает
        WEASYPRINT_AVAILABLE = True
    except Exception as e:
        print(f"WeasyPrint доступен, но не может быть использован: {str(e)}")
        WEASYPRINT_AVAILABLE = False
except ImportError:
    print("WeasyPrint не установлен или не может быть импортирован")
    WEASYPRINT_AVAILABLE = False
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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, Count, F, Sum, Avg
from django.template import Template, Context

# Импортируем наши декораторы и функции для премиум-фич
from .decorators import require_premium, check_resource_limit, premium_feature_context
from .premium_features import can_use_feature, get_limit_value

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
from .models import CustomUser, Skill, PortfolioTheme, PortfolioSettings, SubscriptionCode, ProfileView, ResumeTemplate, UserResumeSettings
from .forms import ProfileForm, SkillForm, PortfolioSettingsForm, PortfolioAdvancedSettingsForm, SubscriptionActivationForm, CustomUserCreationForm, CustomUserChangeForm, UserProfileForm, SubscriptionCodeForm, UserResumeSettingsForm, ResumeAdvancedSettingsForm


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
@premium_feature_context(['enhanced_pdf', 'resume_templates', 'watermark'])
def generate_pdf_resume(request):
    """Генерирует PDF-резюме пользователя с использованием выбранного шаблона"""
    try:
        # Получаем данные пользователя
        user = request.user
        
        # Получаем настройки резюме пользователя
        resume_settings, created = UserResumeSettings.objects.get_or_create(user=user)
        
        # Получаем максимальные значения для количества элементов из настроек premium
        max_projects = get_limit_value(user, 'max_projects')
        max_certificates = get_limit_value(user, 'max_certificates')
        max_achievements = get_limit_value(user, 'max_achievements')
        
        # Получаем все необходимые данные в соответствии с настройками и лимитами
        skills = user.skills.all() if resume_settings.show_skills else []
        projects = user.projects.all().order_by('-created_at')[:max_projects] if resume_settings.show_projects else []
        certificates = user.certificates.all().order_by('-issue_date')[:max_certificates] if resume_settings.show_certificates else []
        achievements = user.achievements.all().order_by('-date')[:max_achievements] if resume_settings.show_achievements else []
        
        # Проверяем наличие шаблона и прав на его использование
        template = resume_settings.template
        if not template:
            # Если шаблон не выбран, используем первый базовый шаблон
            template = ResumeTemplate.objects.filter(is_premium=False, template_type='basic').first()
            
            # Если базовых шаблонов нет, создаем сообщение об ошибке
            if not template:
                messages.error(request, _('Не найдены шаблоны резюме. Пожалуйста, обратитесь к администратору.'))
                return redirect('users:profile')
        
        # Проверяем права на использование премиум шаблонов
        if template.is_premium and not can_use_feature(user, 'resume_templates'):
            messages.warning(request, _('У вас нет доступа к премиум шаблону. Используется базовый шаблон.'))
            template = ResumeTemplate.objects.filter(is_premium=False, template_type='basic').first()
        
        # Данные для передачи в шаблон
        context = {
            'user': user,
            'skills': skills,
            'projects': projects,
            'certificates': certificates,
            'achievements': achievements,
            'resume_settings': resume_settings,
            'template': template,
            'request': request,
        }
        
        # Если у шаблона есть собственный HTML, используем его, иначе используем базовый шаблон
        if template.html_template:
            html_string = Template(template.html_template).render(Context(context))
        else:
            # Используем стандартный шаблон
            html_template = get_template('users/pdf_resume.html')
            html_string = html_template.render(context)
        
        # Создаем HTTP ответ с опцией для отображения в браузере или скачивания
        if request.GET.get('view', False):
            # Если запрошен просмотр, возвращаем HTML
            return HttpResponse(html_string)
        
        # Настройка стилей для PDF
        css_string = template.css_template if template.css_template else ""
        
        # Добавляем пользовательские стили, если они есть
        if resume_settings.custom_css:
            css_string += "\n" + resume_settings.custom_css
        
        # Подставляем пользовательские цвета, если они заданы
        if resume_settings.primary_color:
            css_string = css_string.replace('#3498db', resume_settings.primary_color)
        if resume_settings.secondary_color:
            css_string = css_string.replace('#2c3e50', resume_settings.secondary_color)
        if resume_settings.accent_color:
            css_string = css_string.replace('#e74c3c', resume_settings.accent_color)
        if resume_settings.background_color:
            css_string = css_string.replace('#ffffff', resume_settings.background_color)
        if resume_settings.text_color:
            css_string = css_string.replace('#333333', resume_settings.text_color)
        if resume_settings.font_family:
            css_string = css_string.replace('Arial, sans-serif', resume_settings.font_family)
        
        # Проверяем доступность WeasyPrint
        if WEASYPRINT_AVAILABLE:
            # Используем WeasyPrint для генерации PDF
            pdf_buffer = io.BytesIO()
            
            # Добавляем базовые CSS-стили для предотвращения проблем с бесконечностью
            css_string += """
            @page {
                size: 210mm 297mm;
                margin: 20mm;
            }
            
            html, body {
                width: 210mm;
                max-width: 210mm;
                height: auto;
                margin: 0;
                padding: 0;
            }
            
            img {
                max-width: 100%;
                height: auto;
            }
            """
            
            try:
                # Создаем временные файлы
                with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                    temp_html.write(html_string.encode('utf-8'))
                    temp_html_path = temp_html.name
                
                with tempfile.NamedTemporaryFile(suffix='.css', delete=False) as temp_css:
                    temp_css.write(css_string.encode('utf-8'))
                    temp_css_path = temp_css.name
                
                try:
                    # Генерируем PDF с WeasyPrint
                    HTML(temp_html_path).write_pdf(pdf_buffer, stylesheets=[CSS(temp_css_path)])
                    
                    # Создаем HTTP ответ с PDF
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{user.username}_resume.pdf"'
                    response.write(pdf_buffer.getvalue())
                    
                    # Удаляем временные файлы
                    try:
                        os.unlink(temp_html_path)
                        os.unlink(temp_css_path)
                    except:
                        pass
                    
                    return response
                
                except Exception as e:
                    # Если возникла ошибка с WeasyPrint, используем ReportLab как запасной вариант
                    messages.warning(request, _('Не удалось создать PDF с помощью основного движка. Используется запасной вариант.'))
                    # Продолжаем выполнение и используем ReportLab ниже
            
            except Exception as e:
                messages.warning(request, _('Проблемы с созданием временных файлов. Используется запасной вариант.'))
                # Продолжаем выполнение и используем ReportLab ниже
        
        # Если WeasyPrint недоступен или возникла ошибка, используем ReportLab
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
        if resume_settings.show_contact_info:
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
        if skills and resume_settings.show_skills:
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
        if projects and resume_settings.show_projects:
            elements.append(Paragraph("Проекты", styles['Heading2']))
            for project in projects:
                elements.append(Paragraph(project.title, styles['Heading3']))
                elements.append(Paragraph(project.description, styles['Normal']))
                if project.technologies:
                    elements.append(Paragraph(f"Технологии: {project.technologies}", styles['Italic']))
                elements.append(Spacer(1, 0.3*cm))
            elements.append(Spacer(1, 0.5*cm))
        
        # Сертификаты
        if certificates and resume_settings.show_certificates:
            elements.append(Paragraph("Сертификаты", styles['Heading2']))
            for cert in certificates:
                elements.append(Paragraph(f"{cert.title} - {cert.issuer}", styles['Heading3']))
                if cert.description:
                    elements.append(Paragraph(cert.description, styles['Normal']))
                elements.append(Paragraph(f"Дата выдачи: {cert.issue_date.strftime('%d.%m.%Y')}", styles['Italic']))
                elements.append(Spacer(1, 0.3*cm))
            elements.append(Spacer(1, 0.5*cm))
        
        # Достижения
        if achievements and resume_settings.show_achievements:
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
def resume_settings_view(request):
    """Настройки резюме пользователя"""
    # Получаем или создаем объект настроек резюме для пользователя
    resume_settings, created = UserResumeSettings.objects.get_or_create(user=request.user)
    
    # Проверяем, имеет ли пользователь активную подписку
    is_premium = request.user.has_active_subscription()
    
    if request.method == 'POST':
        settings_form = UserResumeSettingsForm(
            request.POST, instance=resume_settings, premium=is_premium
        )
        
        if is_premium:
            advanced_form = ResumeAdvancedSettingsForm(request.POST, instance=resume_settings)
            if settings_form.is_valid() and advanced_form.is_valid():
                settings_form.save()
                advanced_form.save()
                messages.success(request, _('Настройки резюме успешно сохранены!'))
                return redirect('users:resume_settings')
        else:
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, _('Настройки резюме успешно сохранены!'))
                return redirect('users:resume_settings')
    else:
        settings_form = UserResumeSettingsForm(instance=resume_settings, premium=is_premium)
        if is_premium:
            advanced_form = ResumeAdvancedSettingsForm(instance=resume_settings)
        else:
            advanced_form = None
    
    # Получаем все шаблоны для отображения на странице
    free_templates = ResumeTemplate.objects.filter(is_premium=False)
    premium_templates = ResumeTemplate.objects.filter(is_premium=True)
    
    context = {
        'settings_form': settings_form,
        'advanced_form': advanced_form,
        'free_templates': free_templates,
        'premium_templates': premium_templates,
        'resume_settings': resume_settings,
        'is_premium': is_premium,
    }
    
    return render(request, 'users/resume_settings.html', context)


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
    profile_views_count = profile_views.count()
    
    # Получаем статистику для проектов пользователя
    project_views = ProjectView.objects.filter(project__user=request.user)
    project_views_count = project_views.count()
    
    # Получаем самые популярные проекты
    popular_projects = Project.objects.filter(user=request.user).annotate(
        views_count=Count('projectview')
    ).order_by('-views_count')[:5]
    
    # Получаем топ источников трафика (реферреры)
    top_referrers = ProfileView.objects.filter(profile_user=request.user).values(
        'referrer'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    # Подготавливаем данные для графиков
    profile_chart_data = []
    project_chart_data = []
    
    # Данные о зрителях
    viewers_data = {}
    
    context = {
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
