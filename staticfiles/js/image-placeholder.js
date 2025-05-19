/**
 * Скрипт для обработки отсутствующих изображений
 * Автоматически заменяет отсутствующие изображения заглушками
 */

document.addEventListener('DOMContentLoaded', function() {
    // Обработка всех изображений на странице
    handleAllImages();
    
    // Наблюдатель за изменениями DOM для динамически добавляемых изображений
    setupMutationObserver();
});

/**
 * Обрабатывает все изображения на странице
 */
function handleAllImages() {
    // Выбираем все изображения с атрибутами data-placeholder
    const images = document.querySelectorAll('img[data-placeholder]');
    
    images.forEach(setupImageFallback);
    
    // Также обрабатываем все обычные изображения
    const allImages = document.querySelectorAll('img:not([data-placeholder])');
    allImages.forEach(img => {
        if (!img.hasAttribute('data-no-placeholder')) {
            setupGenericFallback(img);
        }
    });
}

/**
 * Настраивает запасной вариант для изображения с указанным типом заглушки
 */
function setupImageFallback(img) {
    // Получаем тип заглушки из атрибута data-placeholder
    const placeholderType = img.getAttribute('data-placeholder');
    
    // Устанавливаем обработчик ошибки загрузки
    img.onerror = function() {
        replaceWithPlaceholder(img, placeholderType);
    };
    
    // Проверяем, загружено ли уже изображение
    if (img.complete && (img.naturalWidth === 0 || img.naturalHeight === 0)) {
        replaceWithPlaceholder(img, placeholderType);
    }
}

/**
 * Настраивает общий запасной вариант для обычного изображения
 */
function setupGenericFallback(img) {
    // Определяем тип заглушки по классам или размерам изображения
    let placeholderType = determinePlaceholderType(img);
    
    // Устанавливаем обработчик ошибки загрузки
    img.onerror = function() {
        replaceWithPlaceholder(img, placeholderType);
    };
    
    // Проверяем, загружено ли уже изображение
    if (img.complete && (img.naturalWidth === 0 || img.naturalHeight === 0)) {
        replaceWithPlaceholder(img, placeholderType);
    }
}

/**
 * Определяет подходящий тип заглушки по классам и размерам изображения
 */
function determinePlaceholderType(img) {
    const classList = img.classList;
    
    // Проверяем классы для определения типа изображения
    if (classList.contains('avatar') || classList.contains('profile-image') || 
        classList.contains('user-img') || classList.contains('rounded-circle')) {
        
        // Определяем размер аватара
        const width = img.width || img.clientWidth || 0;
        if (width <= 50) return 'avatar_small';
        if (width >= 200) return 'avatar_large';
        return 'avatar';
    }
    
    if (classList.contains('certificate') || img.src.includes('certificate')) {
        if (classList.contains('thumbnail') || classList.contains('small')) {
            return 'certificate_thumb';
        }
        return 'certificate';
    }
    
    if (classList.contains('achievement') || img.src.includes('achievement')) {
        if (classList.contains('small')) {
            return 'achievement_small';
        }
        return 'achievement';
    }
    
    if (classList.contains('project') || img.src.includes('project')) {
        if (classList.contains('thumbnail') || classList.contains('thumb')) {
            return 'project_thumb';
        }
        return 'project';
    }
    
    // По умолчанию возвращаем универсальную заглушку
    return 'project';
}

/**
 * Заменяет изображение на соответствующую заглушку
 */
function replaceWithPlaceholder(img, placeholderType) {
    // Базовый путь к заглушкам
    const basePath = '/static/img/placeholders/';
    
    // Определяем URL заглушки по типу
    let placeholderUrl;
    
    switch (placeholderType) {
        case 'avatar':
            placeholderUrl = `${basePath}avatars/default.jpg`;
            break;
        case 'avatar_small':
            placeholderUrl = `${basePath}avatars/small.jpg`;
            break;
        case 'avatar_large':
            placeholderUrl = `${basePath}avatars/large.jpg`;
            break;
        case 'project':
            placeholderUrl = `${basePath}projects/default.jpg`;
            break;
        case 'project_thumb':
            placeholderUrl = `${basePath}projects/thumbnail.jpg`;
            break;
        case 'certificate':
            placeholderUrl = `${basePath}certificates/default.jpg`;
            break;
        case 'certificate_thumb':
            placeholderUrl = `${basePath}certificates/thumbnail.jpg`;
            break;
        case 'achievement':
            placeholderUrl = `${basePath}achievements/default.jpg`;
            break;
        case 'achievement_small':
            placeholderUrl = `${basePath}achievements/small.jpg`;
            break;
        default:
            placeholderUrl = `${basePath}projects/default.jpg`;
    }
    
    // Сохраняем оригинальный URL для отладки
    img.setAttribute('data-original-src', img.src);
    
    // Устанавливаем заглушку
    img.src = placeholderUrl;
    
    // Отмечаем изображение как замененное на заглушку
    img.classList.add('using-placeholder');
}

/**
 * Настраивает MutationObserver для обработки динамически добавляемых изображений
 */
function setupMutationObserver() {
    // Создаем экземпляр наблюдателя с функцией обратного вызова
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            // Проверяем добавленные узлы
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    // Проверяем, является ли узел элементом img
                    if (node.nodeType === 1 && node.tagName === 'IMG') {
                        if (node.hasAttribute('data-placeholder')) {
                            setupImageFallback(node);
                        } else if (!node.hasAttribute('data-no-placeholder')) {
                            setupGenericFallback(node);
                        }
                    }
                    
                    // Если узел содержит другие узлы, проверяем наличие изображений
                    if (node.nodeType === 1 && node.querySelectorAll) {
                        const nestedImages = node.querySelectorAll('img[data-placeholder]');
                        nestedImages.forEach(setupImageFallback);
                        
                        const allNestedImages = node.querySelectorAll('img:not([data-placeholder]):not([data-no-placeholder])');
                        allNestedImages.forEach(setupGenericFallback);
                    }
                });
            }
        });
    });
    
    // Настраиваем наблюдателя для отслеживания всего документа
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
} 