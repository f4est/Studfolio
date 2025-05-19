from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Project, Certificate, Achievement, Review, ProjectPost, ProjectComment, ProjectView
from .forms import ProjectForm, CertificateForm, AchievementForm, ReviewForm
from users.models import CustomUser

# Импортируем наши декораторы и функции для премиум-функций
from users.decorators import require_premium, check_resource_limit, premium_feature_context
from users.premium_features import can_use_feature, get_limit_value

# Добавляем свою версию функции get_client_ip
def get_client_ip(request):
    """Получение IP-адреса клиента из запроса"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Функции для подсчета ресурсов
def count_user_projects(user):
    """Возвращает количество проектов пользователя"""
    return Project.objects.filter(user=user).count()

def count_user_certificates(user):
    """Возвращает количество сертификатов пользователя"""
    return Certificate.objects.filter(user=user).count()

def count_user_achievements(user):
    """Возвращает количество достижений пользователя"""
    return Achievement.objects.filter(user=user).count()

def count_user_skills(user):
    """Возвращает количество навыков пользователя"""
    return user.skills.count()

# Проекты
@login_required
def project_list_view(request):
    """Список проектов пользователя"""
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portfolio/project_list.html', {'projects': projects})


@login_required
@check_resource_limit('max_projects', count_user_projects)
@premium_feature_context(['max_projects'])
def project_add_view(request):
    """Добавление нового проекта"""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, _('Проект успешно добавлен!'))
            return redirect('portfolio:project_list')
    else:
        form = ProjectForm()
    
    # Добавляем информацию о лимите
    max_projects = get_limit_value(request.user, 'max_projects')
    current_projects = count_user_projects(request.user)
    
    return render(request, 'portfolio/project_form.html', {
        'form': form, 
        'action': 'add',
        'max_projects': max_projects,
        'current_projects': current_projects,
        'is_unlimited': max_projects == float('inf')
    })


@login_required
def project_detail_view(request, project_id):
    """Детальная информация о проекте"""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Проверяем доступ: только владелец или публичный профиль может видеть проект
        if project.user != request.user and not project.user.is_public:
            raise Http404(_("Проект не найден."))
        
        # Записываем просмотр проекта
        if project.user != request.user:  # Не считаем просмотры своих проектов
            # Получаем данные о пользователе и запросе
            viewer = request.user if request.user.is_authenticated else None
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referrer = request.META.get('HTTP_REFERER', '')
            
            # Создаем запись о просмотре
            ProjectView.objects.create(
                project=project,
                viewer=viewer,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer
            )
        
        # Получаем отзывы к проекту
        reviews = Review.objects.filter(project=project, is_approved=True).order_by('-created_at')
        
        # Проверяем, может ли текущий пользователь оставлять отзывы
        can_add_review = False
        if request.user.is_authenticated and request.user.user_type in ['teacher', 'admin'] and project.user.user_type == 'student':
            can_add_review = True
        
        return render(request, 'portfolio/project_detail.html', {
            'project': project, 
            'reviews': reviews,
            'can_add_review': can_add_review
        })
    except Http404:
        return render(request, '404.html', status=404)


@login_required
def project_edit_view(request, project_id):
    """Редактирование проекта"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, _('Проект успешно обновлен!'))
            return redirect('portfolio:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'portfolio/project_form.html', {
        'form': form, 
        'action': 'edit',
        'project': project
    })


@login_required
def project_delete_view(request, project_id):
    """Удаление проекта"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, _('Проект успешно удален!'))
        return redirect('portfolio:project_list')
    
    return render(request, 'portfolio/project_confirm_delete.html', {'project': project})


# Сертификаты
@login_required
def certificate_list_view(request):
    """Список сертификатов пользователя"""
    certificates = Certificate.objects.filter(user=request.user).order_by('-issue_date')
    return render(request, 'portfolio/certificate_list.html', {'certificates': certificates})


@login_required
@check_resource_limit('max_certificates', count_user_certificates)
@premium_feature_context(['max_certificates'])
def certificate_add_view(request):
    """Добавление нового сертификата"""
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.user = request.user
            
            # Если credential_id заполнено, используем его вместо certificate_id
            if certificate.credential_id:
                certificate.certificate_id = certificate.credential_id
                
            # Если credential_url заполнено, используем его вместо certificate_url
            if certificate.credential_url:
                certificate.certificate_url = certificate.credential_url
                
            # Если issuing_organization заполнено, используем его вместо issuer
            if certificate.issuing_organization:
                certificate.issuer = certificate.issuing_organization
                
            # Если expiration_date заполнено, используем его вместо expiry_date
            if certificate.expiration_date:
                certificate.expiry_date = certificate.expiration_date
                
            certificate.save()
            messages.success(request, _('Сертификат успешно добавлен!'))
            return redirect('portfolio:certificate_list')
    else:
        form = CertificateForm()
    
    # Добавляем информацию о лимите
    max_certificates = get_limit_value(request.user, 'max_certificates')
    current_certificates = count_user_certificates(request.user)
    
    return render(request, 'portfolio/certificate_form.html', {
        'form': form, 
        'action': 'add',
        'max_certificates': max_certificates,
        'current_certificates': current_certificates,
        'is_unlimited': max_certificates == float('inf')
    })


@login_required
def certificate_detail_view(request, certificate_id):
    """Детальная информация о сертификате"""
    try:
        certificate = get_object_or_404(Certificate, id=certificate_id)
        
        # Проверяем доступ: только владелец или публичный профиль может видеть сертификат
        if certificate.user != request.user and not certificate.user.is_public:
            raise Http404(_("Сертификат не найден."))
        
        return render(request, 'portfolio/certificate_detail.html', {'certificate': certificate})
    except Http404:
        return render(request, '404.html', status=404)


@login_required
def certificate_edit_view(request, certificate_id):
    """Редактирование сертификата"""
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            certificate = form.save(commit=False)
            
            # Если credential_id заполнено, используем его вместо certificate_id
            if certificate.credential_id:
                certificate.certificate_id = certificate.credential_id
                
            # Если credential_url заполнено, используем его вместо certificate_url
            if certificate.credential_url:
                certificate.certificate_url = certificate.credential_url
                
            # Если issuing_organization заполнено, используем его вместо issuer
            if certificate.issuing_organization:
                certificate.issuer = certificate.issuing_organization
                
            # Если expiration_date заполнено, используем его вместо expiry_date
            if certificate.expiration_date:
                certificate.expiry_date = certificate.expiration_date
                
            certificate.save()
            messages.success(request, _('Сертификат успешно обновлен!'))
            return redirect('portfolio:certificate_detail', certificate_id=certificate.id)
    else:
        form = CertificateForm(instance=certificate)
    
    return render(request, 'portfolio/certificate_form.html', {
        'form': form, 
        'action': 'edit',
        'certificate': certificate
    })


@login_required
def certificate_delete_view(request, certificate_id):
    """Удаление сертификата"""
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    if request.method == 'POST':
        certificate.delete()
        messages.success(request, _('Сертификат успешно удален!'))
        return redirect('portfolio:certificate_list')
    
    return render(request, 'portfolio/certificate_confirm_delete.html', {'certificate': certificate})


# Достижения
@login_required
def achievement_list_view(request):
    """Список достижений пользователя"""
    achievements = Achievement.objects.filter(user=request.user).order_by('-date')
    return render(request, 'portfolio/achievement_list.html', {'achievements': achievements})


@login_required
@check_resource_limit('max_achievements', count_user_achievements)
@premium_feature_context(['max_achievements'])
def achievement_add_view(request):
    """Добавление нового достижения"""
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.user = request.user
            achievement.save()
            messages.success(request, _('Достижение успешно добавлено!'))
            return redirect('portfolio:achievement_list')
    else:
        form = AchievementForm()
    
    # Добавляем информацию о лимите
    max_achievements = get_limit_value(request.user, 'max_achievements')
    current_achievements = count_user_achievements(request.user)
    
    return render(request, 'portfolio/achievement_form.html', {
        'form': form, 
        'action': 'add',
        'max_achievements': max_achievements,
        'current_achievements': current_achievements,
        'is_unlimited': max_achievements == float('inf')
    })


@login_required
def achievement_detail_view(request, achievement_id):
    """Детальная информация о достижении"""
    try:
        achievement = get_object_or_404(Achievement, id=achievement_id)
        
        # Проверяем доступ: только владелец или публичный профиль может видеть достижение
        if achievement.user != request.user and not achievement.user.is_public:
            raise Http404(_("Достижение не найдено."))
        
        return render(request, 'portfolio/achievement_detail.html', {'achievement': achievement})
    except Http404:
        return render(request, '404.html', status=404)


@login_required
def achievement_edit_view(request, achievement_id):
    """Редактирование достижения"""
    achievement = get_object_or_404(Achievement, id=achievement_id, user=request.user)
    
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES, instance=achievement)
        if form.is_valid():
            achievement = form.save(commit=False)
            
            # Если date_received заполнено, используем его вместо date
            if achievement.date_received:
                achievement.date = achievement.date_received
                
            # Если issuing_organization заполнено, используем его вместо organizer
            if achievement.issuing_organization:
                achievement.organizer = achievement.issuing_organization
                
            achievement.save()
            messages.success(request, _('Достижение успешно обновлено!'))
            return redirect('portfolio:achievement_detail', achievement_id=achievement.id)
    else:
        form = AchievementForm(instance=achievement)
    
    return render(request, 'portfolio/achievement_form.html', {
        'form': form, 
        'action': 'edit',
        'achievement': achievement
    })


@login_required
def achievement_delete_view(request, achievement_id):
    """Удаление достижения"""
    achievement = get_object_or_404(Achievement, id=achievement_id, user=request.user)
    
    if request.method == 'POST':
        achievement.delete()
        messages.success(request, _('Достижение успешно удалено!'))
        return redirect('portfolio:achievement_list')
    
    return render(request, 'portfolio/achievement_confirm_delete.html', {'achievement': achievement})


# Отзывы
@login_required
def review_list_view(request):
    """Список отзывов"""
    is_student = request.user.user_type == 'student'
    is_teacher = request.user.user_type == 'teacher'
    is_admin = request.user.user_type == 'admin'
    
    if is_student:
        # Студент видит все отзывы о себе, включая неодобренные
        reviews = Review.objects.filter(student=request.user).order_by('-created_at')
        
        # Отладочная информация
        print(f"Студент: {request.user.username}, ID: {request.user.id}")
        print(f"Всего отзывов: {reviews.count()}")
        print(f"Отзывы: {[r.id for r in reviews]}")
        
    elif is_teacher or is_admin:
        # Преподаватель или админ видит отзывы, которые он дал
        reviews = Review.objects.filter(reviewer=request.user).order_by('-created_at')
    else:
        reviews = []
    
    # Группируем отзывы по статусу одобрения
    approved_reviews = [review for review in reviews if review.is_approved]
    pending_reviews = [review for review in reviews if not review.is_approved]
    
    context = {
        'reviews': reviews,
        'approved_reviews': approved_reviews,
        'pending_reviews': pending_reviews,
        'is_student': is_student,
        'is_teacher': is_teacher,
        'is_admin': is_admin,
    }
    
    return render(request, 'portfolio/review_list.html', context)


@login_required
def review_add_view(request, student_id):
    """Добавление нового отзыва"""
    # Проверяем, что текущий пользователь - преподаватель или админ
    if request.user.user_type not in ['teacher', 'admin']:
        messages.error(request, _('У вас нет прав для добавления отзывов!'))
        return redirect('home')
    
    # Получаем студента
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = student
            review.reviewer = request.user
            
            # Админы могут сразу одобрять отзывы
            if request.user.user_type == 'admin':
                review.is_approved = True
            
            review.save()
            messages.success(request, _('Отзыв успешно добавлен и ожидает подтверждения!'))
            return redirect('portfolio:review_list')
    else:
        # Получаем проекты студента для выбора
        projects = Project.objects.filter(user=student)
        form = ReviewForm()
        form.fields['project'].queryset = projects
    
    return render(request, 'portfolio/review_form.html', {
        'form': form, 
        'action': 'add',
        'student': student
    })


@login_required
def review_detail_view(request, review_id):
    """Детальная информация об отзыве"""
    # Получаем отзыв
    review = get_object_or_404(Review, id=review_id)
    
    # Проверяем доступ: могут просматривать студент (о котором отзыв), автор или администратор
    if (review.student != request.user and review.reviewer != request.user and 
            request.user.user_type != 'admin'):
        if not (review.is_approved and review.student.is_public):
            raise Http404(_("Отзыв не найден."))
    
    return render(request, 'portfolio/review_detail.html', {'review': review})


@login_required
def review_edit_view(request, review_id):
    """Редактирование отзыва"""
    # Только автор или админ может редактировать отзыв
    review = get_object_or_404(Review, id=review_id)
    if review.reviewer != request.user and request.user.user_type != 'admin':
        messages.error(request, _('У вас нет прав для редактирования этого отзыва!'))
        return redirect('portfolio:review_list')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            # Сбрасываем статус одобрения при редактировании (если не админ)
            if request.user.user_type != 'admin':
                review.is_approved = False
            form.save()
            messages.success(request, _('Отзыв успешно обновлен!'))
            return redirect('portfolio:review_detail', review_id=review.id)
    else:
        form = ReviewForm(instance=review)
        # Ограничиваем выбор проектов студента
        form.fields['project'].queryset = Project.objects.filter(user=review.student)
    
    return render(request, 'portfolio/review_form.html', {
        'form': form, 
        'action': 'edit',
        'review': review,
        'student': review.student
    })


@login_required
def review_delete_view(request, review_id):
    """Удаление отзыва"""
    # Только автор или админ может удалить отзыв
    review = get_object_or_404(Review, id=review_id)
    if review.reviewer != request.user and request.user.user_type != 'admin':
        messages.error(request, _('У вас нет прав для удаления этого отзыва!'))
        return redirect('portfolio:review_list')
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, _('Отзыв успешно удален!'))
        return redirect('portfolio:review_list')
    
    return render(request, 'portfolio/review_confirm_delete.html', {'review': review})


@login_required
def review_approve_view(request, review_id):
    """Одобрение отзыва"""
    # Только администратор может одобрять отзывы
    if request.user.user_type != 'admin':
        messages.error(request, _('У вас нет прав для одобрения отзывов!'))
        return redirect('portfolio:review_list')
    
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = not review.is_approved
    review.save()
    
    if review.is_approved:
        message = _('Отзыв успешно одобрен!')
    else:
        message = _('Отзыв отмечен как неодобренный!')
    
    messages.success(request, message)
    return redirect('portfolio:review_detail', review_id=review.id)


# Лента проектов
@login_required
def project_feed(request):
    """Лента проектов от всех пользователей"""
    posts = ProjectPost.objects.select_related('project', 'author').prefetch_related('comments', 'likes').order_by('-created_at')
    return render(request, 'portfolio/project_feed.html', {'posts': posts})

@login_required
def create_project_post(request, project_id):
    """Создание публикации о проекте в ленте"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, _('Содержание публикации не может быть пустым'))
            return redirect('portfolio:project_detail', pk=project_id)
        
        post = ProjectPost.objects.create(
            project=project,
            author=request.user,
            content=content
        )
        
        messages.success(request, _('Публикация успешно создана'))
        return redirect('portfolio:project_feed')
    
    return render(request, 'portfolio/create_project_post.html', {'project': project})

@login_required
@require_POST
def like_post(request, post_id):
    """Лайк/анлайк публикации"""
    post = get_object_or_404(ProjectPost, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'likes_count': post.like_count(),
        'liked': liked
    })

@login_required
@require_POST
def add_comment(request, post_id):
    """Добавление комментария к публикации"""
    post = get_object_or_404(ProjectPost, id=post_id)
    
    data = json.loads(request.body)
    text = data.get('text', '').strip()
    
    if not text:
        return JsonResponse({'error': _('Комментарий не может быть пустым')}, status=400)
    
    comment = ProjectComment.objects.create(
        post=post,
        author=request.user,
        text=text
    )
    
    # Возвращаем данные нового комментария для добавления на страницу без перезагрузки
    return JsonResponse({
        'id': comment.id,
        'text': comment.text,
        'author': comment.author.username,
        'author_avatar': comment.author.profile_image.url if comment.author.profile_image else None,
        'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M')
    })

@login_required
def delete_post(request, post_id):
    """Удаление публикации"""
    post = get_object_or_404(ProjectPost, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, _('Публикация успешно удалена'))
        return redirect('portfolio:project_feed')
    
    return render(request, 'portfolio/delete_post_confirm.html', {'post': post})
