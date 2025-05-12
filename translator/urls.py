from django.urls import path
from . import views

app_name = 'translator'

urlpatterns = [
    path('api/translate/', views.translate_text, name='translate_text'),
    path('api/translate-content/', views.translate_content, name='translate_content'),
    path('dashboard/', views.translation_dashboard, name='dashboard'),
] 