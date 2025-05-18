import os
import re
import polib

def fix_format_strings(po_path):
    """
    Исправляет ошибки форматирования в файлах переводов .po
    """
    po = polib.pofile(po_path)
    changes_made = 0
    
    for entry in po:
        if '%(' in entry.msgid and ')' in entry.msgid:
            # Находим все форматирующие шаблоны в исходной строке
            patterns = re.findall(r'%\([^)]+\)[ds]', entry.msgid)
            
            # Проверяем, есть ли эти шаблоны в переводе
            changed = False
            new_msgstr = entry.msgstr
            
            for pattern in patterns:
                var_name = re.search(r'%\(([^)]+)\)', pattern).group(1)
                
                # Ищем неправильные варианты шаблона
                wrong_patterns = [
                    r'%\s*\(\s*' + var_name.capitalize() + r'\s*\)\s*[DS]',  # %(Count) D
                    r'%\s*\(\s*' + var_name + r'\s*\)\s*[DS]',               # %(count) D
                    r'%\s*\(' + var_name + r'\)',                           # %(count)
                    r'%\s*\([^)]*\)',                                      # %(something)
                    r'%\s*\([сс][аа][нн][аа][уу]\)',                       # %(санау) - казахский вариант
                ]
                
                for wrong in wrong_patterns:
                    if re.search(wrong, new_msgstr, re.IGNORECASE):
                        new_msgstr = re.sub(wrong, pattern, new_msgstr, flags=re.IGNORECASE)
                        changed = True
            
            if changed:
                entry.msgstr = new_msgstr
                changes_made += 1
    
    if changes_made > 0:
        po.save()
        print(f"В файле {po_path} исправлено {changes_made} строк")
    else:
        print(f"Файл {po_path} не требует исправлений")

def main():
    locale_dir = 'locale'
    languages = ['en', 'kk']
    
    for lang in languages:
        po_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.po')
        if os.path.exists(po_path):
            print(f"Обрабатываю {po_path}...")
            fix_format_strings(po_path)
        else:
            print(f"Файл {po_path} не найден")
            
if __name__ == "__main__":
    main() 