from django.urls import path
from . import views

app_name = 'language'

urlpatterns = [
    path('set/', views.set_language, name='set_language'),
    path('translations/', views.get_translations, name='get_translations'),
    path('admin/', views.translation_admin, name='translation_admin'),
] 