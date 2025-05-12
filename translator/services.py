import logging
import time
from django.conf import settings
from .models import TranslationCache

logger = logging.getLogger(__name__)

# Базовый словарь с переводами для основных фраз
TRANSLATIONS = {
    # Русский -> Английский
    'ru': {
        'en': {
            'Создайте ваше электронное портфолио': 'Create your electronic portfolio',
            'Studfolio - платформа для студентов, где вы можете презентовать свои учебные и профессиональные достижения, проекты и получать отзывы от преподавателей.': 
                'Studfolio - a platform for students where you can present your academic and professional achievements, projects and receive feedback from teachers.',
            'Мой профиль': 'My Profile',
            'Мои проекты': 'My Projects',
            'Почему Studfolio?': 'Why Studfolio?',
            'Управление проектами': 'Project Management',
            'Создавайте и управляйте вашими учебными и профессиональными проектами в одном месте.': 
                'Create and manage your educational and professional projects in one place.',
            'Сертификаты и достижения': 'Certificates and Achievements',
            'Сохраняйте и демонстрируйте ваши сертификаты, награды и достижения.': 
                'Save and showcase your certificates, awards and achievements.',
            'Отзывы преподавателей': 'Teacher Reviews',
            'Получайте конструктивную обратную связь от преподавателей по вашим работам и проектам.': 
                'Get constructive feedback from teachers on your work and projects.'
        },
        'pl': {
            'Создайте ваше электронное портфолио': 'Utwórz swoje elektroniczne portfolio',
            'Studfolio - платформа для студентов, где вы можете презентовать свои учебные и профессиональные достижения, проекты и получать отзывы от преподавателей.': 
                'Studfolio - platforma dla studentów, gdzie możesz prezentować swoje osiągnięcia akademickie i zawodowe, projekty oraz otrzymywać opinie od nauczycieli.',
            'Мой профиль': 'Mój profil',
            'Мои проекты': 'Moje projekty',
            'Почему Studfolio?': 'Dlaczego Studfolio?',
            'Управление проектами': 'Zarządzanie projektami',
            'Создавайте и управляйте вашими учебными и профессиональными проектами в одном месте.': 
                'Twórz i zarządzaj swoimi projektami edukacyjnymi i zawodowymi w jednym miejscu.',
            'Сертификаты и достижения': 'Certyfikaty i osiągnięcia',
            'Сохраняйте и демонстрируйте ваши сертификаты, награды и достижения.': 
                'Zapisuj i prezentuj swoje certyfikaty, nagrody i osiągnięcia.',
            'Отзывы преподавателей': 'Opinie nauczycieli',
            'Получайте конструктивную обратную связь от преподавателей по вашим работам и проектам.': 
                'Otrzymuj konstruktywną informację zwrotną od nauczycieli na temat swoich prac i projektów.'
        }
    }
}

class TranslationService:
    """
    Сервис для автоматического перевода текста с использованием локального словаря
    и кэша переводов
    """
    def __init__(self):
        self.translations = TRANSLATIONS
    
    def translate_text(self, text, source_lang='auto', target_lang='en', use_cache=True):
        """
        Переводит текст с использованием словаря и кэша
        
        Args:
            text: Текст для перевода
            source_lang: Исходный язык (по умолчанию 'auto' для автоопределения)
            target_lang: Целевой язык (по умолчанию 'en')
            use_cache: Использовать ли кэш переводов (по умолчанию True)
            
        Returns:
            str: Переведенный текст
        """
        if not text or source_lang == target_lang:
            return text
            
        # Если язык не указан, используем русский по умолчанию
        if source_lang == 'auto':
            source_lang = 'ru'
            
        # Проверяем, есть ли перевод в кэше
        if use_cache:
            cache = self._get_from_cache(text, source_lang, target_lang)
            if cache:
                return cache.translated_text
        
        try:
            # Пытаемся найти перевод в словаре
            if source_lang in self.translations and target_lang in self.translations[source_lang]:
                translated_text = self.translations[source_lang][target_lang].get(text, text)
            else:
                # Если не нашли точное соответствие, пробуем перевести каждое слово
                words = text.split()
                translated_words = []
                for word in words:
                    if source_lang in self.translations and target_lang in self.translations[source_lang]:
                        translated_word = self.translations[source_lang][target_lang].get(word, word)
                        translated_words.append(translated_word)
                    else:
                        translated_words.append(word)
                translated_text = ' '.join(translated_words)
                
                # Если перевод не изменился, просто возвращаем исходный текст
                if translated_text == text:
                    translated_text = f"[{target_lang}] {text}"
            
            # Сохраняем перевод в кэш
            if use_cache:
                self._save_to_cache(text, source_lang, target_lang, translated_text)
                
            return translated_text
            
        except Exception as e:
            logger.error(f"Ошибка при переводе текста: {e}")
            return text  # В случае ошибки возвращаем исходный текст
    
    def batch_translate(self, texts, source_lang='auto', target_lang='en', use_cache=True):
        """
        Переводит списки текстов
        
        Args:
            texts: Список текстов для перевода
            source_lang: Исходный язык
            target_lang: Целевой язык
            use_cache: Использовать ли кэш переводов
            
        Returns:
            list: Список переведенных текстов
        """
        if not texts:
            return []
            
        results = []
        for text in texts:
            translated = self.translate_text(text, source_lang, target_lang, use_cache)
            results.append(translated)
            
        return results
    
    def _get_from_cache(self, text, source_lang, target_lang):
        """Получает перевод из кэша"""
        try:
            if source_lang == 'auto':
                # Если язык автоопределяемый, ищем по любому исходному языку
                cache = TranslationCache.objects.filter(
                    source_text=text,
                    target_language=target_lang
                ).first()
            else:
                cache = TranslationCache.objects.filter(
                    source_text=text,
                    source_language=source_lang,
                    target_language=target_lang
                ).first()
            
            return cache
            
        except Exception as e:
            logger.error(f"Ошибка при получении перевода из кэша: {e}")
            return None
    
    def _save_to_cache(self, text, source_lang, target_lang, translated_text):
        """Сохраняет перевод в кэш"""
        try:
            cache, created = TranslationCache.objects.get_or_create(
                source_text=text,
                source_language=source_lang,
                target_language=target_lang,
                defaults={'translated_text': translated_text}
            )
            
            if not created and cache.translated_text != translated_text:
                cache.translated_text = translated_text
                cache.save()
                
        except Exception as e:
            logger.error(f"Ошибка при сохранении перевода в кэш: {e}")
            
    def add_translation(self, source_lang, target_lang, source_text, target_text):
        """
        Добавляет новый перевод в словарь
        
        Args:
            source_lang: Исходный язык
            target_lang: Целевой язык
            source_text: Исходный текст
            target_text: Переведенный текст
        """
        if source_lang not in self.translations:
            self.translations[source_lang] = {}
            
        if target_lang not in self.translations[source_lang]:
            self.translations[source_lang][target_lang] = {}
            
        self.translations[source_lang][target_lang][source_text] = target_text 