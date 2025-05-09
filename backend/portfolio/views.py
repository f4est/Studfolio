from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import os
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import tempfile

from .models import (
    Portfolio, 
    AboutSection, 
    Education, 
    Skill, 
    Project, 
    Certificate, 
    PortfolioComment
)
from .serializers import (
    PortfolioSerializer,
    PortfolioCreateSerializer,
    AboutSectionSerializer,
    EducationSerializer,
    SkillSerializer,
    ProjectSerializer,
    CertificateSerializer,
    PortfolioCommentSerializer,
    PortfolioCommentCreateSerializer
)
from users.permissions import IsOwnerOrTeacherOrAdmin, IsAdminOrTeacherOrReadOnly


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PortfolioCreateSerializer
        return PortfolioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Для неаутентифицированных пользователей показываем только публичные портфолио
        if not self.request.user.is_authenticated:
            return queryset.filter(is_public=True)
        
        user = self.request.user
        # Фильтрация портфолио в зависимости от роли пользователя
        if user.is_admin() or user.is_teacher():
            # Администраторы и преподаватели видят все портфолио
            return queryset
        
        # Обычные пользователи видят только публичные портфолио или свои
        return queryset.filter(is_public=True) | queryset.filter(user=user)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Разрешить всем просматривать список и детали портфолио
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Разрешить обновление/удаление только владельцу/преподавателю/админу
            return [IsOwnerOrTeacherOrAdmin()]
        elif self.action == 'create':
            # Разрешить создание только аутентифицированным пользователям
            return [permissions.IsAuthenticated()]
        
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        portfolio = self.get_object()
        
        # Создаем временный файл для PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Создаем PDF
        c = canvas.Canvas(temp_path, pagesize=A4)
        width, height = A4
        
        # Зарегистрируем шрифт (в реальном проекте нужно использовать доступные шрифты)
        # pdfmetrics.registerFont(TTFont('Arial', os.path.join(settings.BASE_DIR, 'fonts/arial.ttf')))
        
        # Создаем стили для параграфов
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle(
            'Heading1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            spaceAfter=6
        )
        
        # Заголовок
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(width/2, height-50, portfolio.title)
        c.setFont('Helvetica', 12)
        c.drawCentredString(width/2, height-70, f"Портфолио студента: {portfolio.user.get_full_name() or portfolio.user.username}")
        c.line(50, height-80, width-50, height-80)
        
        y_position = height - 100
        
        # Раздел "Обо мне"
        try:
            about = portfolio.about
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, y_position, "Обо мне")
            y_position -= 20
            
            # Добавляем текст "Обо мне"
            text = Paragraph(about.content, normal_style)
            text.wrapOn(c, width-100, height)
            text.drawOn(c, 50, y_position - text.height)
            y_position -= text.height + 20
        except AboutSection.DoesNotExist:
            pass
        
        # Образование
        educations = portfolio.educations.all()
        if educations:
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, y_position, "Образование")
            y_position -= 20
            
            for edu in educations:
                c.setFont('Helvetica-Bold', 12)
                c.drawString(50, y_position, edu.institution)
                y_position -= 15
                
                c.setFont('Helvetica', 12)
                c.drawString(50, y_position, f"{edu.degree}, {edu.start_date.year}-{edu.end_date.year if edu.end_date else 'настоящее время'}")
                y_position -= 15
                
                if edu.description:
                    text = Paragraph(edu.description, normal_style)
                    text.wrapOn(c, width-100, height)
                    text.drawOn(c, 50, y_position - text.height)
                    y_position -= text.height + 10
                
                y_position -= 10
                
                # Проверяем, нужна ли новая страница
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
        
        # Навыки
        if y_position < 100:
            c.showPage()
            y_position = height - 50
            
        skills = portfolio.skills.all()
        if skills:
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, y_position, "Навыки")
            y_position -= 20
            
            # Группируем навыки по категориям
            skill_categories = {}
            for skill in skills:
                category = skill.category or "Общие"
                if category not in skill_categories:
                    skill_categories[category] = []
                skill_categories[category].append(skill)
            
            for category, category_skills in skill_categories.items():
                c.setFont('Helvetica-Bold', 12)
                c.drawString(50, y_position, category)
                y_position -= 15
                
                c.setFont('Helvetica', 12)
                for skill in category_skills:
                    c.drawString(50, y_position, f"{skill.name} - {skill.level}/5")
                    y_position -= 15
                
                y_position -= 5
                
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
        
        # Проекты
        if y_position < 100:
            c.showPage()
            y_position = height - 50
            
        projects = portfolio.projects.all()
        if projects:
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, y_position, "Проекты")
            y_position -= 20
            
            for project in projects:
                c.setFont('Helvetica-Bold', 12)
                c.drawString(50, y_position, project.title)
                y_position -= 15
                
                date_range = f"{project.start_date.year}"
                if project.is_ongoing:
                    date_range += " - настоящее время"
                elif project.end_date:
                    date_range += f" - {project.end_date.year}"
                
                c.setFont('Helvetica-Oblique', 10)
                c.drawString(50, y_position, date_range)
                y_position -= 15
                
                if project.description:
                    text = Paragraph(project.description, normal_style)
                    text.wrapOn(c, width-100, height)
                    text.drawOn(c, 50, y_position - text.height)
                    y_position -= text.height + 5
                
                if project.url:
                    c.setFont('Helvetica', 10)
                    c.drawString(50, y_position, f"URL: {project.url}")
                    y_position -= 12
                
                if project.github_url:
                    c.setFont('Helvetica', 10)
                    c.drawString(50, y_position, f"GitHub: {project.github_url}")
                    y_position -= 12
                
                y_position -= 10
                
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
        
        # Сертификаты
        if y_position < 100:
            c.showPage()
            y_position = height - 50
            
        certificates = portfolio.certificates.all()
        if certificates:
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, y_position, "Сертификаты")
            y_position -= 20
            
            for cert in certificates:
                c.setFont('Helvetica-Bold', 12)
                c.drawString(50, y_position, cert.title)
                y_position -= 15
                
                c.setFont('Helvetica', 12)
                c.drawString(50, y_position, f"Выдан: {cert.issuer}, {cert.issue_date.strftime('%d.%m.%Y')}")
                y_position -= 15
                
                if cert.description:
                    text = Paragraph(cert.description, normal_style)
                    text.wrapOn(c, width-100, height)
                    text.drawOn(c, 50, y_position - text.height)
                    y_position -= text.height + 5
                
                if cert.credential_id:
                    c.setFont('Helvetica', 10)
                    c.drawString(50, y_position, f"ID: {cert.credential_id}")
                    y_position -= 12
                
                y_position -= 10
                
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
        
        # Финальная страница
        c.setFont('Helvetica', 10)
        c.drawString(50, 40, f"Документ сформирован: {portfolio.updated_at.strftime('%d.%m.%Y')}")
        c.drawRightString(width-50, 40, f"Страница {c.getPageNumber()}")
        
        c.save()
        
        # Отправляем PDF пользователю
        with open(temp_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=portfolio_{portfolio.user.username}.pdf'
        
        # Удаляем временный файл
        os.unlink(temp_path)
        
        return response


class AboutSectionViewSet(viewsets.ModelViewSet):
    serializer_class = AboutSectionSerializer
    permission_classes = [IsOwnerOrTeacherOrAdmin]
    
    def get_queryset(self):
        return AboutSection.objects.filter(portfolio__user=self.request.user)
    
    def perform_create(self, serializer):
        portfolio = get_object_or_404(Portfolio, user=self.request.user)
        serializer.save(portfolio=portfolio)


class EducationViewSet(viewsets.ModelViewSet):
    serializer_class = EducationSerializer
    permission_classes = [IsOwnerOrTeacherOrAdmin]
    
    def get_queryset(self):
        return Education.objects.filter(portfolio__user=self.request.user)
    
    def perform_create(self, serializer):
        portfolio = get_object_or_404(Portfolio, user=self.request.user)
        serializer.save(portfolio=portfolio)


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [IsOwnerOrTeacherOrAdmin]
    
    def get_queryset(self):
        return Skill.objects.filter(portfolio__user=self.request.user)
    
    def perform_create(self, serializer):
        portfolio = get_object_or_404(Portfolio, user=self.request.user)
        serializer.save(portfolio=portfolio)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrTeacherOrAdmin]
    
    def get_queryset(self):
        return Project.objects.filter(portfolio__user=self.request.user)
    
    def perform_create(self, serializer):
        portfolio = get_object_or_404(Portfolio, user=self.request.user)
        serializer.save(portfolio=portfolio)


class CertificateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsOwnerOrTeacherOrAdmin]
    
    def get_queryset(self):
        return Certificate.objects.filter(portfolio__user=self.request.user)
    
    def perform_create(self, serializer):
        portfolio = get_object_or_404(Portfolio, user=self.request.user)
        serializer.save(portfolio=portfolio)


class PortfolioCommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrTeacherOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PortfolioCommentCreateSerializer
        return PortfolioCommentSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Преподаватели и администраторы видят все комментарии
        if user.is_teacher() or user.is_admin():
            return PortfolioComment.objects.all()
        
        # Студенты видят только комментарии к своему портфолио
        return PortfolioComment.objects.filter(portfolio__user=user)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 