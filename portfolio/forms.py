from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Project, Certificate, Achievement, Review


class ProjectForm(forms.ModelForm):
    """Форма для добавления/редактирования проекта"""
    
    class Meta:
        model = Project
        fields = ('title', 'description', 'image', 'url', 'github_url', 
                  'technologies', 'start_date', 'end_date', 'is_featured')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'technologies': forms.TextInput(attrs={
                'placeholder': _('Например: Python, Django, JavaScript')
            }),
        }


class CertificateForm(forms.ModelForm):
    """Форма для добавления/редактирования сертификата"""
    
    class Meta:
        model = Certificate
        fields = ('title', 'issuer', 'description', 'certificate_id', 
                  'issue_date', 'expiry_date', 'certificate_file', 'certificate_url',
                  'credential_id', 'credential_url', 'issuing_organization', 'expiration_date', 'image')
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class AchievementForm(forms.ModelForm):
    """Форма для добавления/редактирования достижения"""
    
    class Meta:
        model = Achievement
        fields = ('title', 'organizer', 'description', 'date', 
                  'place', 'achievement_file', 'achievement_url',
                  'category', 'date_received', 'issuing_organization', 'image')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewForm(forms.ModelForm):
    """Форма для добавления отзыва"""
    
    class Meta:
        model = Review
        fields = ('project', 'text', 'rating')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.RadioSelect(),
        } 