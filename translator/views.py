from django.shortcuts import render
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.translation import get_language

from .models import TranslationCache, AutoTranslatedContent
from .services import TranslationService

# Сервис перевода (один экземпляр для всего приложения)
translation_service = TranslationService()


@csrf_exempt
@require_POST
def translate_text(request):
    """
    API для перевода текста
    POST запрос с параметрами:
    - text: текст для перевода
    - source_lang: исходный язык (по умолчанию 'auto')
    - target_lang: целевой язык (по умолчанию текущий язык пользователя)
    """
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', get_language())
        
        if not text:
            return JsonResponse({'error': 'Не указан текст для перевода'}, status=400)
            
        # Переводим текст
        translated_text = translation_service.translate_text(
            text, 
            source_lang=source_lang, 
            target_lang=target_lang
        )
        
        return JsonResponse({
            'source_text': text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def translate_content(request):
    """
    API для перевода контента объекта
    POST запрос с параметрами:
    - content_type: тип контента (например, 'portfolio.project')
    - object_id: ID объекта
    - field_name: имя поля для перевода
    - text: текст для перевода
    - source_lang: исходный язык (по умолчанию 'auto')
    - target_langs: список целевых языков (по умолчанию все доступные языки)
    """
    try:
        data = json.loads(request.body)
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        field_name = data.get('field_name')
        text = data.get('text')
        source_lang = data.get('source_lang', 'auto')
        target_langs = data.get('target_langs', [lang[0] for lang in settings.LANGUAGES if lang[0] != source_lang])
        
        if not all([content_type, object_id, field_name, text]):
            return JsonResponse({'error': 'Не все обязательные параметры указаны'}, status=400)
            
        # Переводим на все указанные языки
        translations = {}
        for lang in target_langs:
            if lang != source_lang:
                translated = translation_service.translate_text(
                    text, 
                    source_lang=source_lang, 
                    target_lang=lang
                )
                translations[lang] = translated
                
        # Сохраняем переводы в базу данных
        auto_trans, created = AutoTranslatedContent.objects.update_or_create(
            content_type=content_type,
            object_id=object_id,
            field_name=field_name,
            source_language=source_lang,
            defaults={'translations': translations}
        )
        
        return JsonResponse({
            'success': True,
            'translations': translations
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def translation_dashboard(request):
    """
    Панель управления переводами
    """
    # Получаем статистику кэша переводов
    cache_count = TranslationCache.objects.count()
    language_stats = {}
    
    for lang_code, lang_name in settings.LANGUAGES:
        source_count = TranslationCache.objects.filter(source_language=lang_code).count()
        target_count = TranslationCache.objects.filter(target_language=lang_code).count()
        language_stats[lang_code] = {
            'name': lang_name,
            'source_count': source_count,
            'target_count': target_count
        }
    
    # Получаем статистику автоматических переводов
    auto_trans_count = AutoTranslatedContent.objects.count()
    
    context = {
        'cache_count': cache_count,
        'language_stats': language_stats,
        'auto_trans_count': auto_trans_count,
    }
    
    return render(request, 'translator/dashboard.html', context)
