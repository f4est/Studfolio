from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Проекты
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/add/', views.project_add_view, name='project_add'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_edit_view, name='project_edit'),
    path('projects/<int:project_id>/delete/', views.project_delete_view, name='project_delete'),
    
    # Лента проектов
    path('feed/', views.project_feed, name='project_feed'),
    path('projects/<int:project_id>/post/', views.create_project_post, name='create_post'),
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # Сертификаты
    path('certificates/', views.certificate_list_view, name='certificate_list'),
    path('certificates/add/', views.certificate_add_view, name='certificate_add'),
    path('certificates/<int:certificate_id>/', views.certificate_detail_view, name='certificate_detail'),
    path('certificates/<int:certificate_id>/edit/', views.certificate_edit_view, name='certificate_edit'),
    path('certificates/<int:certificate_id>/delete/', views.certificate_delete_view, name='certificate_delete'),
    
    # Достижения
    path('achievements/', views.achievement_list_view, name='achievement_list'),
    path('achievements/add/', views.achievement_add_view, name='achievement_add'),
    path('achievements/<int:achievement_id>/', views.achievement_detail_view, name='achievement_detail'),
    path('achievements/<int:achievement_id>/edit/', views.achievement_edit_view, name='achievement_edit'),
    path('achievements/<int:achievement_id>/delete/', views.achievement_delete_view, name='achievement_delete'),
    
    # Отзывы
    path('reviews/', views.review_list_view, name='review_list'),
    path('reviews/add/<int:student_id>/', views.review_add_view, name='review_add'),
    path('reviews/<int:review_id>/', views.review_detail_view, name='review_detail'),
    path('reviews/<int:review_id>/edit/', views.review_edit_view, name='review_edit'),
    path('reviews/<int:review_id>/delete/', views.review_delete_view, name='review_delete'),
    path('reviews/approve/<int:review_id>/', views.review_approve_view, name='review_approve'),
] 