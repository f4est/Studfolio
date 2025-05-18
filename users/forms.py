from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Skill, PortfolioSettings, PortfolioTheme, SubscriptionCode, UserResumeSettings, ResumeTemplate


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
                  'profile_image', 'date_of_birth', 'phone_number',
                  'university', 'faculty', 'specialization', 'year_of_study',
                  'is_public', 'custom_url', 'notifications_enabled')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_image', 
                 'university', 'faculty', 'specialization', 'year_of_study', 
                 'date_of_birth', 'phone_number', 'is_public', 'custom_url', 'notifications_enabled']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


# Для обратной совместимости с существующим кодом
ProfileForm = UserProfileForm


class SkillForm(forms.ModelForm):
    """Форма для добавления и редактирования навыков"""
    
    class Meta:
        model = Skill
        fields = ['name', 'level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
        }


class CustomUserTeacherCreationForm(UserCreationForm):
    """Форма для создания нового преподавателя"""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'teacher'
        if commit:
            user.save()
        return user


class PortfolioSettingsForm(forms.ModelForm):
    """Форма для настройки портфолио"""
    
    class Meta:
        model = PortfolioSettings
        fields = ('theme', 'layout', 'show_skills', 'show_education', 
                  'show_certificates', 'show_achievements', 'show_contact_info')
    
    def __init__(self, *args, **kwargs):
        # Проверяем наличие premium параметра
        premium = kwargs.pop('premium', False)
        super().__init__(*args, **kwargs)
        
        # Если пользователь не премиум, ограничиваем выбор тем
        if not premium:
            self.fields['theme'].queryset = PortfolioTheme.objects.filter(is_premium=False)
            self.fields['theme'].help_text = _('Для доступа к премиум темам необходима платная подписка')


class PortfolioAdvancedSettingsForm(forms.ModelForm):
    """Форма расширенных настроек портфолио (доступна только с премиум-подпиской)"""
    class Meta:
        model = PortfolioSettings
        fields = ['custom_css', 'custom_domain', 'subdomain', 'use_subdomain']
        widgets = {
            'custom_css': forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'placeholder': '/* Ваш CSS код здесь */'}),
            'custom_domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example.com'}),
            'subdomain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'}),
            'use_subdomain': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'custom_css': _('Введите свой CSS код для кастомизации внешнего вида портфолио'),
            'custom_domain': _('Укажите свой домен (требуется настройка DNS)'),
            'subdomain': _('Укажите желаемый субдомен (только латинские буквы, цифры и дефисы)'),
            'use_subdomain': _('Включите, чтобы использовать субдомен для вашего портфолио'),
        }


class UserResumeSettingsForm(forms.ModelForm):
    """Форма для настройки резюме пользователя"""
    
    class Meta:
        model = UserResumeSettings
        fields = ('template', 'show_profile_image', 'show_skills', 'show_education', 
                  'show_projects', 'show_certificates', 'show_achievements', 
                  'show_contact_info', 'max_projects', 'max_certificates', 'max_achievements')
    
    def __init__(self, *args, **kwargs):
        # Проверяем наличие premium параметра
        premium = kwargs.pop('premium', False)
        super().__init__(*args, **kwargs)
        
        # Если пользователь не премиум, ограничиваем выбор шаблонов
        if not premium:
            self.fields['template'].queryset = ResumeTemplate.objects.filter(is_premium=False)
            self.fields['template'].help_text = _('Для доступа к премиум шаблонам необходима платная подписка')


class ResumeAdvancedSettingsForm(forms.ModelForm):
    """Форма для расширенных настроек резюме (для премиум пользователей)"""
    
    class Meta:
        model = UserResumeSettings
        fields = ('primary_color', 'secondary_color', 'accent_color', 
                  'background_color', 'text_color', 'font_family', 'custom_css')
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'custom_css': forms.Textarea(attrs={'rows': 6, 'class': 'form-control code-editor'}),
        }


class SubscriptionActivationForm(forms.Form):
    """Форма для активации подписки по коду"""
    code = forms.CharField(
        label=_('Код активации'), 
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXX-XXXX-XXXX'})
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