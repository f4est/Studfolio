// Объект для хранения переводов
let translations = {};

// Функция для получения текущего языка
function getCurrentLanguage() {
    // Определяем язык из URL (первый сегмент пути)
    const pathSegments = window.location.pathname.split('/').filter(segment => segment);
    if (pathSegments.length > 0 && ['ru', 'en', 'kk'].includes(pathSegments[0])) {
        return pathSegments[0];
    }
    
    // Если нет в URL, получаем из cookie или используем ru по умолчанию
    return getCookie('selected_language') || 'ru';
}

// Функция для получения cookie значения
function getCookie(name) {
    const cookieArr = document.cookie.split(';');
    
    for (let i = 0; i < cookieArr.length; i++) {
        const cookiePair = cookieArr[i].split('=');
        if (name === cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    
    return null;
}

// Функция для загрузки переводов
function loadTranslations(language) {
    console.log("Загрузка переводов для языка:", language);
    
    fetch(`/${language}/language/translations/`)
        .then(response => response.json())
        .then(data => {
            console.log("Получены переводы:", data);
            translations = data;
            translatePage();
        })
        .catch(error => console.error('Ошибка загрузки переводов:', error));
}

// Функция для перевода страницы
function translatePage() {
    console.log("Применение переводов");
    
    // Переводим все элементы с атрибутом data-translate
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[key]) {
            element.textContent = translations[key];
            console.log(`Переведен элемент ${key} -> ${translations[key]}`);
        }
    });
    
    // Также переводим элементы с атрибутом data-translatable, используя Django trans tags
    // Это нужно, если у вас динамически меняется контент через JavaScript
    document.querySelectorAll('[data-translatable]').forEach(element => {
        // Здесь мы не меняем содержимое, так как оно уже переведено через Django trans tags
        // Просто обновляем стиль или добавляем класс для индикации перевода, если нужно
        element.classList.add('translated');
    });
}

// Функция для изменения языка
function changeLanguage(language) {
    console.log("Смена языка на:", language);
    
    // Используем скрытую форму для переключения языка
    const form = document.getElementById('language-form');
    const input = document.getElementById('language-input');
    
    if (form && input) {
        input.value = language;
        form.submit();
    } else {
        // Запасной вариант, если форма не найдена
        // Получаем текущий URL и заменяем языковой префикс
        let currentPath = window.location.pathname;
        const languages = ['ru', 'en', 'kk'];
        const currentLang = getCurrentLanguage();
        
        // Если текущий путь уже содержит языковой префикс, заменяем его
        if (languages.includes(currentLang)) {
            if (currentPath.startsWith(`/${currentLang}/`)) {
                currentPath = currentPath.replace(`/${currentLang}/`, `/${language}/`);
                window.location.href = currentPath;
                return;
            }
        }
        
        // Если не содержит префикс, просто добавляем новый
        window.location.href = `/${language}/`;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log("Инициализация language_switcher.js");
    
    // Загружаем переводы для текущего языка
    const currentLanguage = getCurrentLanguage();
    console.log("Текущий язык:", currentLanguage);
    
    // Устанавливаем атрибут lang для HTML элемента
    document.documentElement.lang = currentLanguage;
    
    // Загружаем переводы для языка
    loadTranslations(currentLanguage);
    
    // Устанавливаем активный класс для текущего языка в меню
    document.querySelectorAll('.language-switcher').forEach(element => {
        if (element.getAttribute('data-language') === currentLanguage) {
            element.classList.add('active');
        } else {
            element.classList.remove('active');
        }
        
        // Добавляем обработчик клика для переключения языка
        element.addEventListener('click', function(e) {
            e.preventDefault();
            const language = this.getAttribute('data-language');
            changeLanguage(language);
        });
    });
}); 