import os
import re

def fix_po_file(file_path):
    """
    Исправляет проблемы с форматированием в .po файлах:
    1. Отсутствие переносов строк между msgid и msgstr
    2. Некорректное форматирование строк типа %(count)d, %(name)s и т.д.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправление форматирования - добавление переноса строки между msgid и msgstr
    fixed_content = re.sub(r'(msgid "[^"]*")msgstr', r'\1\nmsgstr', content)
    
    # Поиск всех msgid с форматными строками Python
    format_strings = {}
    for match in re.finditer(r'msgid "([^"]*%\([^)]+\)[ds][^"]*)"', fixed_content):
        msgid = match.group(1)
        # Собираем все форматные строки вида %(name)s, %(count)d и т.д.
        formats = re.findall(r'%\(([^)]+)\)([ds])', msgid)
        if formats:
            format_strings[msgid] = formats
    
    # Исправление некорректных форматных строк в msgstr
    for msgid, formats in format_strings.items():
        # Ищем соответствующий msgstr
        msgstr_pattern = r'msgid "' + re.escape(msgid) + r'"\s*\nmsgstr "([^"]*)"'
        msgstr_match = re.search(msgstr_pattern, fixed_content)
        if msgstr_match:
            msgstr = msgstr_match.group(1)
            fixed_msgstr = msgstr
            
            # Исправляем каждый формат
            for var_name, format_type in formats:
                # Варианты некорректного форматирования
                patterns = [
                    r'%\s*\(\s*' + var_name.capitalize() + r'\s*\)\s*[DS]',  # %(Count) D
                    r'%\s*\(\s*' + var_name + r'\s*\)\s*[DS]',               # %(count) D
                    r'%\s*\(' + var_name + r'\)',                           # %(count)
                    r'%\s*\([^\)]*[' + var_name + r'][^\)]*\)',              # %(something with name)
                    r'%[ds]',                                               # %s или %d (без скобок)
                ]
                
                correct_format = '%(' + var_name + ')' + format_type
                
                # Проверяем каждый вариант неправильного форматирования
                for pattern in patterns:
                    if re.search(pattern, fixed_msgstr, re.IGNORECASE):
                        fixed_msgstr = re.sub(pattern, correct_format, fixed_msgstr, flags=re.IGNORECASE)
            
            # Заменяем в файле, если были изменения
            if fixed_msgstr != msgstr:
                fixed_content = fixed_content.replace(
                    f'msgid "{msgid}"\nmsgstr "{msgstr}"',
                    f'msgid "{msgid}"\nmsgstr "{fixed_msgstr}"'
                )
    
    # Дополнительно исправляем наиболее распространенные проблемы
    replacements = [
        (r'%\s*\(\s*Count\s*\)\s*D', r'%(count)d'),
        (r'%\s*\(\s*санау\s*\)', r'%(count)d'),
        (r'%\s*\(\s*S\s*\)', r'%(s)s'),
        (r'%\s*\(\s*D\s*\)', r'%(d)d'),
        (r'%\([^)]*\)\s*[DS]', lambda m: m.group(0).lower()),  # Lower case D/S
    ]
    
    for pattern, replacement in replacements:
        fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.IGNORECASE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Файл {file_path} исправлен")

def main():
    locale_dir = 'locale'
    for lang in ['en', 'kk']:
        po_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.po')
        if os.path.exists(po_path):
            fix_po_file(po_path)
        else:
            print(f"Файл не найден: {po_path}")

if __name__ == "__main__":
    main() 