from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

from .models import SupportTicket, TicketResponse, TicketAttachment, SupportCategory, KnowledgeBaseArticle
from .forms import SupportTicketForm, TicketResponseForm, TicketFilterForm

# Вспомогательные функции
def user_can_view_ticket(user, ticket):
    """Проверяет, может ли пользователь просматривать тикет"""
    return user.is_support_staff() or ticket.user == user

def handle_ticket_attachments(attachments, ticket, user):
    """Обрабатывает загрузку файлов для тикета"""
    for attachment in attachments:
        TicketAttachment.objects.create(
            ticket=ticket,
            file=attachment,
            file_name=attachment.name
        )

# Представления страниц поддержки
@login_required
def support_home(request):
    """Главная страница поддержки"""
    user_tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')[:5]
    categories = SupportCategory.objects.all()
    popular_articles = KnowledgeBaseArticle.objects.filter(is_published=True).order_by('-views_count')[:5]
    
    context = {
        'user_tickets': user_tickets,
        'categories': categories,
        'popular_articles': popular_articles
    }
    
    return render(request, 'support/home.html', context)

@login_required
def ticket_list(request):
    """Список тикетов пользователя"""
    filter_form = TicketFilterForm(request.GET)
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    
    # Применяем фильтры, если они указаны
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        if data.get('status'):
            tickets = tickets.filter(status=data['status'])
        
        if data.get('priority'):
            tickets = tickets.filter(priority=data['priority'])
        
        if data.get('category'):
            tickets = tickets.filter(category=data['category'])
        
        if data.get('search'):
            search_query = data['search']
            tickets = tickets.filter(
                Q(subject__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        if data.get('date_from'):
            tickets = tickets.filter(created_at__gte=data['date_from'])
        
        if data.get('date_to'):
            tickets = tickets.filter(created_at__lte=data['date_to'])
    
    # Пагинация
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
    }
    
    return render(request, 'support/ticket_list.html', context)

@login_required
def ticket_create(request):
    """Создание нового тикета"""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ticket = form.save()
            
            # Обработка вложений
            if request.FILES.getlist('attachments'):
                handle_ticket_attachments(request.FILES.getlist('attachments'), ticket, request.user)
            
            messages.success(request, _('Ваш тикет успешно создан! Мы свяжемся с вами в ближайшее время.'))
            return redirect('support:ticket_detail', pk=ticket.pk)
    else:
        form = SupportTicketForm(user=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'support/ticket_create.html', context)

@login_required
def ticket_detail(request, pk):
    """Детальная информация о тикете и возможность ответа"""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    # Проверяем, имеет ли пользователь доступ к тикету
    if not user_can_view_ticket(request.user, ticket):
        raise Http404(_("У вас нет доступа к этому тикету."))
    
    # Обработка ответа на тикет
    if request.method == 'POST':
        form = TicketResponseForm(request.POST, request.FILES, user=request.user, ticket=ticket)
        if form.is_valid():
            response = form.save()
            
            # Обработка вложений
            if request.FILES.getlist('attachments'):
                handle_ticket_attachments(request.FILES.getlist('attachments'), ticket, request.user)
            
            messages.success(request, _('Ваш ответ успешно отправлен!'))
            return redirect('support:ticket_detail', pk=ticket.pk)
    else:
        form = TicketResponseForm(user=request.user, ticket=ticket)
    
    # Получаем все ответы на тикет
    responses = ticket.responses.order_by('created_at')
    
    # Если пользователь не является сотрудником поддержки, исключаем внутренние заметки
    if not request.user.is_support_staff():
        responses = responses.filter(is_internal_note=False)
    
    context = {
        'ticket': ticket,
        'responses': responses,
        'form': form,
    }
    
    return render(request, 'support/ticket_detail.html', context)

@login_required
@require_POST
def ticket_close(request, pk):
    """Закрытие тикета"""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    # Проверяем, имеет ли пользователь доступ к тикету
    if not user_can_view_ticket(request.user, ticket):
        raise Http404(_("У вас нет доступа к этому тикету."))
    
    ticket.close()
    messages.success(request, _('Тикет успешно закрыт.'))
    
    return redirect('support:ticket_detail', pk=ticket.pk)

@login_required
@require_POST
def ticket_reopen(request, pk):
    """Переоткрытие тикета"""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    # Проверяем, имеет ли пользователь доступ к тикету
    if not user_can_view_ticket(request.user, ticket):
        raise Http404(_("У вас нет доступа к этому тикету."))
    
    ticket.reopen()
    messages.success(request, _('Тикет успешно переоткрыт.'))
    
    return redirect('support:ticket_detail', pk=ticket.pk)

# Административные представления для поддержки
@login_required
def admin_ticket_list(request):
    """Список всех тикетов для администраторов и поддержки"""
    # Проверяем, имеет ли пользователь доступ к админке тикетов
    if not request.user.is_support_staff():
        raise Http404(_("У вас нет доступа к этой странице."))
    
    filter_form = TicketFilterForm(request.GET)
    
    # Если пользователь может управлять всеми тикетами, показываем все
    # Иначе показываем только те, которые назначены ему или еще не назначены
    if request.user.can_manage_all_tickets():
        tickets = SupportTicket.objects.all()
    else:
        tickets = SupportTicket.objects.filter(
            Q(assigned_to=request.user) | Q(assigned_to__isnull=True)
        )
    
    tickets = tickets.order_by('-created_at')
    
    # Применяем фильтры, если они указаны
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        if data.get('status'):
            tickets = tickets.filter(status=data['status'])
        
        if data.get('priority'):
            tickets = tickets.filter(priority=data['priority'])
        
        if data.get('category'):
            tickets = tickets.filter(category=data['category'])
        
        if data.get('search'):
            search_query = data['search']
            tickets = tickets.filter(
                Q(subject__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        if data.get('date_from'):
            tickets = tickets.filter(created_at__gte=data['date_from'])
        
        if data.get('date_to'):
            tickets = tickets.filter(created_at__lte=data['date_to'])
    
    # Пагинация
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
    }
    
    return render(request, 'support/admin/ticket_list.html', context)

@login_required
@require_POST
def admin_ticket_assign(request, pk):
    """Назначение тикета на сотрудника поддержки"""
    # Проверяем, имеет ли пользователь доступ к админке тикетов
    if not request.user.is_support_staff():
        raise Http404(_("У вас нет доступа к этой странице."))
    
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    # Назначаем тикет текущему пользователю
    ticket.assigned_to = request.user
    ticket.status = 'in_progress'
    ticket.save()
    
    # Создаем автоматическую внутреннюю заметку о назначении
    TicketResponse.objects.create(
        ticket=ticket,
        user=request.user,
        content=_('Тикет назначен на {}.').format(request.user.username),
        is_internal_note=True
    )
    
    messages.success(request, _('Тикет успешно назначен вам.'))
    
    return redirect('support:ticket_detail', pk=ticket.pk)

@login_required
@require_POST
def admin_ticket_resolve(request, pk):
    """Отметка тикета как решенного"""
    # Проверяем, имеет ли пользователь доступ к админке тикетов
    if not request.user.is_support_staff():
        raise Http404(_("У вас нет доступа к этой странице."))
    
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    ticket.resolve()
    
    # Создаем автоматическую внутреннюю заметку о решении
    TicketResponse.objects.create(
        ticket=ticket,
        user=request.user,
        content=_('Тикет отмечен как решенный.'),
        is_internal_note=True
    )
    
    messages.success(request, _('Тикет успешно отмечен как решенный.'))
    
    return redirect('support:ticket_detail', pk=ticket.pk)

# Представления для базы знаний
def knowledge_base(request):
    """Главная страница базы знаний"""
    categories = SupportCategory.objects.all()
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'support/knowledge/home.html', context)

def knowledge_category(request, category_slug):
    """Страница категории в базе знаний"""
    category = get_object_or_404(SupportCategory, slug=category_slug)
    articles = KnowledgeBaseArticle.objects.filter(category=category, is_published=True)
    
    context = {
        'category': category,
        'articles': articles,
    }
    
    return render(request, 'support/knowledge/category.html', context)

def knowledge_article(request, category_slug, article_slug):
    """Отображение статьи из базы знаний"""
    category = get_object_or_404(SupportCategory, slug=category_slug)
    article = get_object_or_404(KnowledgeBaseArticle, slug=article_slug, category=category, is_published=True)
    
    # Увеличиваем счетчик просмотров
    article.views_count += 1
    article.save()
    
    # Получаем связанные статьи из той же категории
    related_articles = KnowledgeBaseArticle.objects.filter(
        category=category, 
        is_published=True
    ).exclude(id=article.id).order_by('-created_at')[:3]
    
    context = {
        'article': article,
        'category': category,
        'related_articles': related_articles,
    }
    
    return render(request, 'support/knowledge/article.html', context)

# Новые представления для дополнительных страниц

def faq(request):
    """Страница часто задаваемых вопросов"""
    return render(request, 'support/knowledge/faq.html')

def premium_benefits(request):
    """Страница преимуществ премиум-подписки"""
    return render(request, 'support/knowledge/premium_benefits.html')

def terms_of_service(request):
    """Страница условий использования"""
    return render(request, 'support/knowledge/terms_of_service.html')

def privacy_policy(request):
    """Страница политики конфиденциальности"""
    return render(request, 'support/knowledge/privacy_policy.html')

def contact_us(request):
    """Страница с формой обратной связи"""
    return render(request, 'support/contact_us.html')

def contact_us_submit(request):
    """Обработка отправки формы обратной связи"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        category = request.POST.get('category')
        captcha = request.POST.get('captcha')
        
        # Валидация капчи
        if captcha != '5':
            messages.error(request, _('Неверный ответ на проверочный вопрос.'))
            return redirect('support:contact_us')
        
        # TODO: Здесь можно добавить отправку email или создание тикета
        # Или сохранение в базу данных
        
        # Пример создания тикета из формы обратной связи
        if request.user.is_authenticated:
            # Для авторизованных пользователей создаем тикет
            ticket = SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                description=message,
                category_id=1,  # ID категории "Общие вопросы"
                priority='medium'
            )
            messages.success(request, _('Ваше сообщение успешно отправлено. Мы ответим вам в ближайшее время. Тикет #{} создан.').format(ticket.id))
        else:
            # Для анонимных пользователей просто показываем сообщение об успехе
            # В реальном проекте здесь можно добавить отправку email
            messages.success(request, _('Ваше сообщение успешно отправлено. Мы ответим вам на указанный email в ближайшее время.'))
        
        return redirect('support:contact_us')
    
    # Если запрос не POST, перенаправляем на страницу формы
    return redirect('support:contact_us')
