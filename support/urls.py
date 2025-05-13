from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Основная страница поддержки
    path('', views.support_home, name='home'),
    
    # Пользовательские тикеты
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/close/', views.ticket_close, name='ticket_close'),
    path('tickets/<int:pk>/reopen/', views.ticket_reopen, name='ticket_reopen'),
    
    # Административные маршруты (только для поддержки и администраторов)
    path('admin/tickets/', views.admin_ticket_list, name='admin_ticket_list'),
    path('admin/tickets/<int:pk>/assign/', views.admin_ticket_assign, name='admin_ticket_assign'),
    path('admin/tickets/<int:pk>/resolve/', views.admin_ticket_resolve, name='admin_ticket_resolve'),
    
    # База знаний
    path('knowledge/', views.knowledge_base, name='knowledge_base'),
    path('knowledge/<slug:category_slug>/', views.knowledge_category, name='knowledge_category'),
    path('knowledge/<slug:category_slug>/<slug:article_slug>/', views.knowledge_article, name='knowledge_article'),
] 