from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Профиль пользователя
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    
    # Навыки
    path('skills/add/', views.skill_add_view, name='skill_add'),
    path('skills/<int:skill_id>/edit/', views.skill_edit_view, name='skill_edit'),
    path('skills/<int:skill_id>/delete/', views.skill_delete_view, name='skill_delete'),
    
    # Портфолио
    path('portfolio/settings/', views.portfolio_settings_view, name='portfolio_settings'),
    path('portfolio/theme/<int:theme_id>/preview/', views.preview_portfolio_theme, name='preview_portfolio_theme'),
    path('portfolio/theme/<int:theme_id>/apply/', views.apply_portfolio_theme, name='apply_portfolio_theme'),
    
    # Подписка
    path('subscription/', views.subscription_view, name='subscription'),
    path('subscription/generate-code/', views.generate_subscription_code, name='generate_subscription_code'),
    path('subscription/activate-code/', views.activate_subscription_code, name='activate_subscription_code'),
    path('subscription/admin-codes/', views.admin_subscription_codes_view, name='admin_subscription_codes'),
    
    # Аналитика
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Поиск
    path('search/', views.search_users, name='search_users'),
    
    # Премиум-руководство
    path('premium-guide/', views.premium_guide_view, name='premium_guide'),

    # Настройки безопасности
    path('security/', views.security_settings_view, name='security_settings'),
] 