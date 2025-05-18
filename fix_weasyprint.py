#!/usr/bin/env python
import os
import sys
import subprocess
import platform

def install_requirements():
    """Устанавливает необходимые зависимости для WeasyPrint"""
    print("Устанавливаем зависимости для WeasyPrint...")
    
    # Установка зависимостей через pip
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
    
    # На Windows нужны дополнительные библиотеки
    if platform.system() == 'Windows':
        print("\nВы используете Windows. WeasyPrint требует GTK+.")
        print("Скачайте и установите GTK+ для Windows с https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
        print("После установки GTK+ перезапустите компьютер")
        
        # Проверяем установку GTK+
        try:
            import weasyprint
            print("\nWeasyPrint установлен, но для работы в Windows требуется GTK+")
            print("Проверьте, что вы установили GTK+ и перезагрузили компьютер")
        except ImportError:
            print("Не удалось импортировать weasyprint. Убедитесь, что все зависимости установлены правильно.")
    
    print("\nУстановка зависимостей завершена.")

def create_fallback_function():
    """Создаем запасную функцию для генерации PDF через reportlab"""
    print("Создаем запасную функцию для генерации PDF...")
    
    # Путь к файлу с представлениями
    views_path = "users/views.py"
    
    # Проверяем, что файл существует
    if not os.path.exists(views_path):
        print(f"Ошибка: Файл {views_path} не найден")
        return
    
    # Читаем содержимое файла
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже функция generate_pdf_fallback
    if "def generate_pdf_fallback" in content:
        print("Запасная функция для генерации PDF уже существует")
        return
    
    # Создаем код функции
    fallback_function = """
def generate_pdf_fallback(user, skills, projects, certificates, achievements, resume_settings):
    """Запасная функция для генерации PDF через ReportLab при проблемах с WeasyPrint"""
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
    
    # Возвращаем PDF из буфера
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
"""
    
    # Добавляем функцию в конец файла
    with open(views_path, 'a', encoding='utf-8') as f:
        f.write(fallback_function)
    
    print("Запасная функция для генерации PDF добавлена в файл views.py")

def modify_generate_pdf_resume():
    """Модифицируем функцию generate_pdf_resume для использования запасной функции"""
    print("Модифицируем функцию генерации PDF...")
    
    # Путь к файлу с представлениями
    views_path = "users/views.py"
    
    # Проверяем, что файл существует
    if not os.path.exists(views_path):
        print(f"Ошибка: Файл {views_path} не найден")
        return
    
    # Читаем содержимое файла
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # Находим строку с использованием reportlab
    reportlab_line_index = -1
    for i, line in enumerate(content):
        if "# Если WeasyPrint недоступен или возникла ошибка, используем ReportLab" in line:
            reportlab_line_index = i
            break
    
    if reportlab_line_index == -1:
        print("Не найдена строка с использованием ReportLab")
        return
    
    # Заменяем код после этой строки на использование запасной функции
    new_code = [
        "        # Если WeasyPrint недоступен или возникла ошибка, используем ReportLab\n",
        "        pdf = generate_pdf_fallback(user, skills, projects, certificates, achievements, resume_settings)\n",
        "        \n",
        "        # Создаем HTTP ответ с PDF\n",
        "        response = HttpResponse(content_type='application/pdf')\n",
        "        response['Content-Disposition'] = f'attachment; filename=\"{user.username}_resume.pdf\"'\n",
        "        response.write(pdf)\n",
        "        \n",
        "        return response\n"
    ]
    
    # Находим конец if-блока с WEASYPRINT_AVAILABLE
    end_if_index = reportlab_line_index
    indent_level = len(content[reportlab_line_index]) - len(content[reportlab_line_index].lstrip())
    
    # Заменяем код
    content = content[:reportlab_line_index] + new_code + content[end_if_index + 60:]
    
    # Записываем измененный файл
    with open(views_path, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print("Функция генерации PDF успешно модифицирована")

def fix_portfolio_preview():
    """Исправляем шаблон предпросмотра портфолио"""
    print("Исправляем шаблон предпросмотра портфолио...")
    
    # Путь к файлу с шаблоном
    template_path = "templates/users/portfolio_preview.html"
    
    # Проверяем, что файл существует
    if not os.path.exists(template_path):
        print(f"Ошибка: Файл {template_path} не найден")
        return
    
    # Создаем новый шаблон
    template_content = """{% extends "users/base.html" %}
{% load static %}
{% load i18n %}

{% block title %}{% trans "Предпросмотр темы" %} - {{ theme.name }}{% endblock %}

{% block extra_css %}
<style>
    /* Базовые стили для предпросмотра */
    body {
        background-color: {{ theme.background_color }};
        color: {{ theme.text_color }};
    }
    
    .theme-primary {
        color: {{ theme.primary_color }};
    }
    
    .theme-secondary {
        color: {{ theme.secondary_color }};
    }
    
    .theme-bg-primary {
        background-color: {{ theme.primary_color }};
        color: white;
    }
    
    .theme-bg-secondary {
        background-color: {{ theme.secondary_color }};
        color: white;
    }
    
    .navbar {
        background-color: {{ theme.primary_color }};
    }
    
    .navbar-brand, .navbar-nav .nav-link {
        color: white !important;
    }
    
    .card {
        border-color: {{ theme.secondary_color }};
    }
    
    .card-header {
        background-color: {{ theme.primary_color }};
        color: white;
    }
    
    .btn-primary {
        background-color: {{ theme.primary_color }};
        border-color: {{ theme.primary_color }};
    }
    
    .btn-secondary {
        background-color: {{ theme.secondary_color }};
        border-color: {{ theme.secondary_color }};
    }
    
    .preview-notice {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: rgba(0,0,0,0.8);
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        z-index: 1000;
    }
</style>
{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="preview-notice">
        {% trans "Предпросмотр темы" %}: {{ theme.name }}
    </div>
    
    <div class="row mb-4">
        <div class="col-12">
            <h1 class="theme-primary">{{ user.get_full_name }}</h1>
            <p class="lead">{{ user.user_type_display }}</p>
            <hr class="theme-secondary">
        </div>
    </div>
    
    <div class="row mb-4">
        <div class="col-md-8">
            <div class="card mb-4">
                <div class="card-header">
                    <h2 class="mb-0">{% trans "О себе" %}</h2>
                </div>
                <div class="card-body">
                    <p>{{ user.bio|default:"Информация о себе отсутствует" }}</p>
                </div>
            </div>
            
            {% if projects %}
            <div class="card mb-4">
                <div class="card-header">
                    <h2 class="mb-0">{% trans "Проекты" %}</h2>
                </div>
                <div class="card-body">
                    {% for project in projects %}
                    <div class="mb-3">
                        <h4 class="theme-primary">{{ project.title }}</h4>
                        <p>{{ project.description }}</p>
                        {% if project.technologies %}
                        <p><strong>{% trans "Технологии" %}:</strong> {{ project.technologies }}</p>
                        {% endif %}
                    </div>
                    {% if not forloop.last %}<hr>{% endif %}
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="col-md-4">
            <div class="card mb-4">
                <div class="card-header">
                    <h2 class="mb-0">{% trans "Навыки" %}</h2>
                </div>
                <div class="card-body">
                    {% if skills %}
                    <ul class="list-group list-group-flush">
                        {% for skill in skills %}
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            {{ skill.name }}
                            <span class="badge theme-bg-primary rounded-pill">{{ skill.level }}</span>
                        </li>
                        {% endfor %}
                    </ul>
                    {% else %}
                    <p>{% trans "Навыки не указаны" %}</p>
                    {% endif %}
                </div>
            </div>
            
            {% if certificates %}
            <div class="card mb-4">
                <div class="card-header">
                    <h2 class="mb-0">{% trans "Сертификаты" %}</h2>
                </div>
                <div class="card-body">
                    <ul class="list-group list-group-flush">
                        {% for cert in certificates %}
                        <li class="list-group-item">
                            <h5 class="theme-primary">{{ cert.title }}</h5>
                            <p class="mb-0"><small>{{ cert.issuer }} ({{ cert.issue_date|date:"d.m.Y" }})</small></p>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            {% endif %}
            
            {% if achievements %}
            <div class="card mb-4">
                <div class="card-header">
                    <h2 class="mb-0">{% trans "Достижения" %}</h2>
                </div>
                <div class="card-body">
                    <ul class="list-group list-group-flush">
                        {% for achievement in achievements %}
                        <li class="list-group-item">
                            <h5 class="theme-primary">{{ achievement.title }}</h5>
                            <p class="mb-0"><small>{{ achievement.organizer }} ({{ achievement.date|date:"d.m.Y" }})</small></p>
                            {% if achievement.place %}
                            <p class="mb-0"><small>{% trans "Место" %}: {{ achievement.place }}</small></p>
                            {% endif %}
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="row mt-5">
        <div class="col-12 text-center">
            <a href="{% url 'users:portfolio_settings' %}" class="btn btn-secondary">{% trans "Вернуться к настройкам" %}</a>
            <a href="{% url 'users:apply_portfolio_theme' theme.id %}" class="btn btn-primary">{% trans "Применить эту тему" %}</a>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    # Записываем шаблон в файл
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("Шаблон предпросмотра портфолио успешно обновлен")

if __name__ == "__main__":
    print("Начинаем исправление проблем с WeasyPrint и шаблонами...")
    
    # Устанавливаем зависимости
    install_requirements()
    
    # Создаем запасную функцию для генерации PDF
    create_fallback_function()
    
    # Модифицируем основную функцию
    modify_generate_pdf_resume()
    
    # Исправляем шаблон предпросмотра
    fix_portfolio_preview()
    
    print("\nГотово! Проблемы с WeasyPrint и шаблонами должны быть исправлены.")
    print("ВАЖНО: Для полной работы WeasyPrint в Windows необходимо установить GTK+.")
    print("Скачайте и установите GTK+ для Windows с https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases") 