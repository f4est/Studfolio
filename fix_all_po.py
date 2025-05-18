import os
import re
import glob

def fix_po_file(file_path):
    """
    Исправляет все распространенные ошибки в .po файлах:
    1. Отсутствие переносов строк между элементами
    2. Некорректные форматные строки %(count)d, %(name)s и т.д.
    """
    print(f"Обрабатываю файл: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return
    
    # Создаем резервную копию
    backup_path = file_path + '.bak'
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Ошибка при создании резервной копии {backup_path}: {e}")
        return
    
    # Исправление 1: добавление переносов строк между элементами
    modified_content = re.sub(r'(msgid "[^"]*")msgstr', r'\1\nmsgstr', content)
    
    # Исправление 2: исправление переносов строк между комментариями и msgid
    modified_content = re.sub(r'(#: [^\n]+)msgid', r'\1\nmsgid', modified_content)
    modified_content = re.sub(r'(#, [^\n]+)msgid', r'\1\nmsgid', modified_content)
    
    # Исправление 3: исправление форматных строк
    modified_content = re.sub(r'%\s*\(\s*Count\s*\)\s*D', r'%(count)d', modified_content, flags=re.IGNORECASE)
    modified_content = re.sub(r'%\s*\(\s*санау\s*\)', r'%(count)d', modified_content, flags=re.IGNORECASE)
    modified_content = re.sub(r'%\s*\(\s*count\s*\)\s*ddd', r'%(count)d', modified_content, flags=re.IGNORECASE)
    modified_content = re.sub(r'%\s*\(\s*Пайдаланушы\s+аты\s*\)', r'%(username)', modified_content, flags=re.IGNORECASE)
    modified_content = re.sub(r'%\s*\(\s*коды\s*\)', r'%(code)', modified_content, flags=re.IGNORECASE)
    modified_content = re.sub(r'%\s*\(\s*күн\s*\)', r'%(days)', modified_content, flags=re.IGNORECASE)
    modified_content = re.sub(r'%\s*s', r'%(count)s', modified_content)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"Файл {file_path} успешно обновлен")
    except Exception as e:
        print(f"Ошибка при записи файла {file_path}: {e}")
        print("Восстанавливаем из резервной копии...")
        try:
            with open(backup_path, 'r', encoding='utf-8') as f_bak:
                original_content = f_bak.read()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"Файл {file_path} восстановлен из резервной копии")
        except Exception as e2:
            print(f"Ошибка при восстановлении файла: {e2}")

def main():
    # Находим все .po файлы в директории locale
    po_files = glob.glob('locale/**/django.po', recursive=True)
    
    if not po_files:
        print("Файлы .po не найдены!")
        return
    
    print(f"Найдено {len(po_files)} файлов .po")
    
    # Исправляем каждый найденный файл
    for po_file in po_files:
        fix_po_file(po_file)
    
    print("Завершено! Пожалуйста, проверьте файлы и запустите compilemessages")

if __name__ == "__main__":
    main() 