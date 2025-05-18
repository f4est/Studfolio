import os
import polib
from googletrans import Translator
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path

class Command(BaseCommand):
    help = 'Автоматически переводит строки в .po файлах используя Google Translate API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source', 
            dest='source_language',
            default='ru',
            help='Исходный язык для перевода (по умолчанию: ru)'
        )
        parser.add_argument(
            '--languages', 
            dest='languages',
            help='Целевые языки для перевода, разделенные запятыми (по умолчанию: en,kk)'
        )
        parser.add_argument(
            '--path', 
            dest='po_path',
            help='Путь к .po файлам (по умолчанию: locale)'
        )
        parser.add_argument(
            '--untranslated-only',
            action='store_true',
            dest='untranslated_only',
            default=False,
            help='Переводить только непереведенные строки (по умолчанию: False)'
        )

    def handle(self, *args, **options):
        # Инициализация переводчика
        translator = Translator()
        
        # Получение параметров
        source_language = options['source_language']
        languages = options.get('languages', 'en,kk').split(',')
        
        # Получаем корректный путь к локализации
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        po_path = options.get('po_path') or os.path.join(base_dir, 'locale')
        
        untranslated_only = options['untranslated_only']
        
        # Вывод информации о начале перевода
        self.stdout.write(self.style.SUCCESS(f'Начинаем автоматический перевод c {source_language} на {", ".join(languages)}'))
        
        # Чтение и перевод файлов
        source_po_path = os.path.join(po_path, source_language, 'LC_MESSAGES', 'django.po')
        if not os.path.exists(source_po_path):
            raise CommandError(f'Исходный файл не найден: {source_po_path}')
        
        source_po = polib.pofile(source_po_path)
        
        for lang in languages:
            if lang == source_language:
                self.stdout.write(self.style.WARNING(f'Пропускаем перевод на исходный язык {lang}'))
                continue
                
            target_po_path = os.path.join(po_path, lang, 'LC_MESSAGES', 'django.po')
            if not os.path.exists(target_po_path):
                self.stdout.write(self.style.WARNING(f'Целевой файл не найден: {target_po_path}'))
                continue
                
            target_po = polib.pofile(target_po_path)
            
            # Словарь для хранения существующих переводов по msgid
            existing_translations = {entry.msgid: entry.msgstr for entry in target_po}
            
            # Счетчики для статистики
            count_total = 0
            count_translated = 0
            
            # Обрабатываем каждую запись в исходном файле
            for entry in source_po:
                # Пропускаем заголовки
                if entry.msgid == '':
                    continue
                    
                # Найти соответствующую запись в целевом файле
                target_entry = None
                for te in target_po:
                    if te.msgid == entry.msgid:
                        target_entry = te
                        break
                
                # Если записи нет в целевом файле, создаем новую
                if target_entry is None:
                    target_entry = polib.POEntry(
                        msgid=entry.msgid,
                        msgstr='',
                        occurrences=entry.occurrences,
                        comment=entry.comment
                    )
                    target_po.append(target_entry)
                
                # Переводим только если строка не переведена или необходимо обновить все
                if not untranslated_only or not target_entry.msgstr:
                    count_total += 1
                    try:
                        # Перевод текста с помощью Google Translate
                        translation = translator.translate(
                            entry.msgid, 
                            src=source_language, 
                            dest=lang
                        )
                        translated_text = translation.text
                        
                        # Обновляем перевод
                        target_entry.msgstr = translated_text
                        count_translated += 1
                        
                        self.stdout.write(f'Переведено ({source_language} -> {lang}): {entry.msgid[:30]}... -> {translated_text[:30]}...')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Ошибка при переводе {entry.msgid}: {str(e)}'))
            
            # Сохраняем результаты
            target_po.save(target_po_path)
            
            self.stdout.write(self.style.SUCCESS(f'Перевод на {lang} завершен. Обработано: {count_total}, переведено: {count_translated}'))
        
        self.stdout.write(self.style.SUCCESS('Автоматический перевод завершен')) 