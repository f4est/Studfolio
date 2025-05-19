from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, Skill, Project, Certificate, Achievement,
    Review, PortfolioSettings, SubscriptionCode
)


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания нового пользователя"""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class CustomUserChangeForm(UserChangeForm):
    """Форма для изменения пользовательских данных"""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 
                  'phone_number', 'university', 'faculty', 'specialization', 
                  'graduation_year', 'is_public', 'user_type')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'university', 'faculty', 'specialization', 'graduation_year',
            'bio', 'is_public', 'profile_image'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class SkillForm(forms.ModelForm):
    """Форма для добавления/редактирования навыка"""
    class Meta:
        model = Skill
        fields = ['name', 'level']
        widgets = {
            'level': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class ProjectForm(forms.ModelForm):
    """Форма для добавления/редактирования проекта"""
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'link', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'technologies': forms.TextInput(attrs={'placeholder': 'Например: Python, Django, React'}),
        }


class CertificateForm(forms.ModelForm):
    """Форма для добавления/редактирования сертификата"""
    class Meta:
        model = Certificate
        fields = ['title', 'issuer', 'description', 'issue_date', 'link', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AchievementForm(forms.ModelForm):
    """Форма для добавления/редактирования достижения"""
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'organizer', 'date', 'place', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class ReviewForm(forms.ModelForm):
    """Форма для добавления отзыва"""
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class PortfolioSettingsForm(forms.ModelForm):
    """Форма настроек портфолио"""
    class Meta:
        model = PortfolioSettings
        fields = [
            'theme', 'show_skills', 'show_projects',
            'show_certificates', 'show_achievements', 'show_reviews',
            'custom_css', 'custom_js'
        ]
        widgets = {
            'custom_css': forms.Textarea(attrs={'rows': 4}),
            'custom_js': forms.Textarea(attrs={'rows': 4}),
        }


class PortfolioAdvancedSettingsForm(forms.ModelForm):
    """Расширенная форма настроек портфолио для премиум-пользователей"""
    class Meta:
        model = PortfolioSettings
        fields = ['custom_css', 'custom_js']
        widgets = {
            'custom_css': forms.Textarea(attrs={'rows': 8}),
            'custom_js': forms.Textarea(attrs={'rows': 8}),
        }


class SubscriptionActivationForm(forms.Form):
    """Форма активации кода подписки"""
    code = forms.CharField(
        max_length=20,
        label=_('Код активации'),
        widget=forms.TextInput(attrs={'placeholder': 'Введите код активации'})
    )


class SubscriptionCodeForm(forms.ModelForm):
    """Форма для создания кода подписки (админка)"""
    class Meta:
        model = SubscriptionCode
        fields = ['code', 'duration_days']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SecuritySettingsForm(forms.ModelForm):
    """Форма настроек безопасности пользователя"""
    class Meta:
        model = CustomUser
        fields = ['enable_2fa']
        labels = {
            'enable_2fa': _('Включить двухфакторную аутентификацию')
        }
        help_texts = {
            'enable_2fa': _('При включенной опции вам потребуется вводить код подтверждения при входе. '
                           'Код будет отправлен на ваш email.')
        } 