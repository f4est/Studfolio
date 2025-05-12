from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Профиль пользователя
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Навыки
    path('skills/add/', views.skill_add_view, name='skill_add'),
    path('skills/<int:skill_id>/edit/', views.skill_edit_view, name='skill_edit'),
    path('skills/<int:skill_id>/delete/', views.skill_delete_view, name='skill_delete'),
    
    # Генерация PDF
    path('profile/pdf/', views.generate_pdf_resume, name='generate_pdf'),
    
    # Публичные профили
    path('public/<str:username>/', views.public_profile, name='public_profile'),
    
    # Настройки портфолио
    path('portfolio/settings/', views.portfolio_settings_view, name='portfolio_settings'),
    path('portfolio/theme/<int:theme_id>/apply/', views.apply_portfolio_theme, name='apply_theme'),
    path('portfolio/theme/<int:theme_id>/preview/', views.preview_portfolio_theme, name='preview_theme'),
    
    # Подписка
    path('subscription/', views.subscription_view, name='subscription'),
    path('subscription/generate_code/', views.generate_subscription_code, name='generate_code'),
    path('premium_guide/', views.premium_guide_view, name='premium_guide'),
    
    # Аналитика
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Поиск пользователей
    path('search/', views.search_users, name='search_users'),
    
    # Публичный профиль
    path('<str:username>/', views.public_profile, name='public_profile'),
] 