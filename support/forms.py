from django import forms
from django.utils.translation import gettext_lazy as _
from .models import SupportTicket, TicketResponse, TicketAttachment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class SupportTicketForm(forms.ModelForm):
    """Форма создания нового тикета поддержки"""
    
    attachments = MultipleFileField(
        label=_('Вложения'),
        required=False,
        help_text=_('Вы можете загрузить до 5 файлов (макс. 10 МБ каждый).')
    )
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'description']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Кратко опишите вашу проблему')}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': _('Подробно опишите вашу проблему...')}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        
        if commit:
            instance.save()
            
        return instance


class TicketResponseForm(forms.ModelForm):
    """Форма для ответа на тикет"""
    
    attachments = MultipleFileField(
        label=_('Вложения'),
        required=False,
        help_text=_('Вы можете загрузить до 5 файлов (макс. 10 МБ каждый).')
    )
    
    class Meta:
        model = TicketResponse
        fields = ['content', 'is_internal_note']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Ваш ответ...')}),
            'is_internal_note': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.ticket = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)
        
        # Скрываем поле для внутренних заметок, если пользователь не является сотрудником поддержки
        if self.user and not self.user.is_support_staff():
            self.fields.pop('is_internal_note')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if self.ticket:
            instance.ticket = self.ticket
            
            # Если это не внутренняя заметка и это ответ от пользователя, 
            # изменяем статус тикета на "ожидает ответа" или "в обработке"
            if not instance.is_internal_note:
                if self.user.is_support_staff():
                    self.ticket.status = 'waiting'
                else:
                    self.ticket.status = 'in_progress'
                self.ticket.save()
        
        if commit:
            instance.save()
            
        return instance


class TicketFilterForm(forms.Form):
    """Форма для фильтрации тикетов"""
    
    STATUS_CHOICES = [('', _('Все статусы'))] + list(SupportTicket.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', _('Все приоритеты'))] + list(SupportTicket.PRIORITY_CHOICES)
    CATEGORY_CHOICES = [('', _('Все категории'))] + list(SupportTicket.CATEGORY_CHOICES)
    
    status = forms.ChoiceField(
        label=_('Статус'),
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    priority = forms.ChoiceField(
        label=_('Приоритет'),
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    category = forms.ChoiceField(
        label=_('Категория'),
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    search = forms.CharField(
        label=_('Поиск'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': _('Поиск по теме или описанию')})
    )
    
    date_from = forms.DateField(
        label=_('От даты'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        label=_('До даты'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    ) 