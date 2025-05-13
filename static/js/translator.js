/**
 * Система автоматического перевода Studfolio
 * Обеспечивает функционал перевода содержимого страницы
 */

class StudfolioTranslator {
    constructor(options = {}) {
        // Настройки по умолчанию
        this.options = {
            apiUrl: '/translator/api/translate/',
            translateButtonClass: 'auto-translate-btn',
            translateableSelector: '[data-translatable]',
            loadingClass: 'translation-loading',
            translatedClass: 'translated',
            debugMode: false, // Отключаем режим отладки по умолчанию
            autoTranslate: true, // Включаем автоматический перевод
            ...options
        };
        
        // Текущий язык пользователя
        this.currentLanguage = document.documentElement.lang || 'ru';
        
        // Кэш переводов в рамках текущей сессии
        this.translationCache = new Map();
        
        // Добавляем отладочный div только если включен режим отладки
        if (this.options.debugMode) {
            this.createDebugPanel();
        }
        
        // Инициализация
        this.init();
    }
    
    /**
     * Инициализация функционала перевода
     */
    init() {
        this.log('Инициализация системы перевода. Текущий язык: ' + this.currentLanguage);
        
        // Находим все элементы на странице, доступные для перевода
        this.translatableElements = document.querySelectorAll(this.options.translateableSelector);
        this.log(`Найдено ${this.translatableElements.length} элементов для перевода`);
        
        // Если включен режим автоперевода
        if (this.options.autoTranslate && this.currentLanguage !== 'ru') {
            // Автоматически переводим контент после загрузки страницы
            this.translateAllContent();
        }
        
        // Добавляем обработчик события для динамически добавленных элементов
        this.observeDynamicContent();
    }
    
    /**
     * Логирование отладочной информации
     */
    log(message, level = 'info') {
        if (!this.options.debugMode) return;
        
        console[level]('[Translator]', message);
        
        // Добавляем сообщение в отладочную панель
        if (this.debugPanel) {
            const logEntry = document.createElement('div');
            logEntry.className = `debug-log-entry log-${level}`;
            logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            this.debugPanel.appendChild(logEntry);
            this.debugPanel.scrollTop = this.debugPanel.scrollHeight;
        }
    }
    
    /**
     * Создает отладочную панель
     */
    createDebugPanel() {
        const existingPanel = document.querySelector('#translator-debug-panel');
        if (existingPanel) {
            this.debugPanel = existingPanel;
            return;
        }
        
        this.debugPanel = document.createElement('div');
        this.debugPanel.id = 'translator-debug-panel';
        this.debugPanel.className = 'translator-debug-panel';
        this.debugPanel.style.cssText = `
            position: fixed;
            bottom: 60px;
            right: 10px;
            width: 300px;
            height: 200px;
            background: rgba(0, 0, 0, 0.8);
            color: #fff;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
            z-index: 9999;
            overflow-y: auto;
            border-radius: 5px;
            display: none;
        `;
        
        // Добавляем заголовок и кнопку закрытия
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            border-bottom: 1px solid #555;
            padding-bottom: 5px;
        `;
        
        const title = document.createElement('span');
        title.textContent = 'Отладка перевода';
        header.appendChild(title);
        
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '×';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
        `;
        closeBtn.addEventListener('click', () => {
            this.debugPanel.style.display = 'none';
        });
        header.appendChild(closeBtn);
        
        this.debugPanel.appendChild(header);
        document.body.appendChild(this.debugPanel);
        
        // В режиме отладки создаем кнопку для отображения панели
        const debugButton = document.createElement('button');
        debugButton.textContent = 'Debug';
        debugButton.className = 'btn btn-sm btn-dark debug-toggle-btn';
        debugButton.style.cssText = `
            position: fixed;
            bottom: 10px;
            right: 10px;
            z-index: 9999;
            opacity: 0.7;
            display: ${this.options.debugMode ? 'block' : 'none'};
        `;
        debugButton.addEventListener('click', () => {
            this.debugPanel.style.display = this.debugPanel.style.display === 'none' ? 'block' : 'none';
        });
        document.body.appendChild(debugButton);
    }
    
    /**
     * Переводит весь доступный контент на странице
     */
    async translateAllContent() {
        const translatableElements = document.querySelectorAll(this.options.translateableSelector);
        
        if (translatableElements.length === 0) {
            this.log('На странице нет контента для перевода', 'warn');
            return;
        }
        
        this.log(`Начинаем перевод ${translatableElements.length} элементов на язык: ${this.currentLanguage}`);
        
        // Целевой язык - текущий язык пользователя
        const targetLang = this.currentLanguage;
        
        // Переводим каждый элемент
        const promises = Array.from(translatableElements).map(element => {
            return this.translateElement(element, 'ru', targetLang);
        });
        
        try {
            await Promise.all(promises);
            this.log('Перевод всех элементов завершен успешно');
        } catch (error) {
            this.log('Ошибка при переводе всего контента: ' + error, 'error');
            console.error('Ошибка при переводе всего контента:', error);
        }
    }
    
    /**
     * Переводит конкретный элемент
     */
    async translateElement(element, sourceLang = 'ru', targetLang) {
        // Если элемент уже переведен, пропускаем
        if (element.classList.contains(this.options.translatedClass)) {
            this.log(`Элемент уже переведен: ${element.textContent.substring(0, 30)}...`);
            return;
        }
        
        // Сохраняем оригинальный текст
        if (!element.dataset.originalText) {
            element.dataset.originalText = element.textContent;
        }
        
        const originalText = element.dataset.originalText;
        this.log(`Переводим: "${originalText.substring(0, 30)}..." с ${sourceLang} на ${targetLang}`);
        
        // Добавляем класс загрузки
        element.classList.add(this.options.loadingClass);
        
        try {
            const translatedText = await this.translateText(originalText, sourceLang, targetLang);
            
            // Устанавливаем переведенный текст
            element.textContent = translatedText;
            
            // Отмечаем элемент как переведенный
            element.classList.add(this.options.translatedClass);
            
            // Добавляем информацию о переводе и возможность вернуться к оригиналу
            this.addTranslationInfo(element);
            
            this.log(`Успешно переведено на ${targetLang}`);
        } catch (error) {
            this.log(`Ошибка при переводе элемента: ${error}`, 'error');
            console.error('Ошибка при переводе элемента:', error);
        } finally {
            // Убираем класс загрузки
            element.classList.remove(this.options.loadingClass);
        }
    }
    
    /**
     * Добавляет информацию о переводе и кнопку для возврата к оригиналу
     */
    addTranslationInfo(element) {
        // Проверяем, есть ли уже информация о переводе
        if (element.nextElementSibling && element.nextElementSibling.classList.contains('translation-info')) {
            return;
        }
        
        // Создаем элемент с информацией о переводе
        const infoElement = document.createElement('div');
        infoElement.className = 'translation-info text-muted small mt-1';
        infoElement.innerHTML = `
            <span>Переведено на ${this.currentLanguage}</span>
            <button class="btn btn-link btn-sm p-0 ms-2 restore-original">Вернуть оригинал</button>
        `;
        
        // Добавляем обработчик для возврата к оригиналу
        const restoreButton = infoElement.querySelector('.restore-original');
        restoreButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.log(`Возврат к оригиналу: ${element.dataset.originalText.substring(0, 30)}...`);
            element.textContent = element.dataset.originalText;
            element.classList.remove(this.options.translatedClass);
            infoElement.remove();
        });
        
        // Вставляем после переведенного элемента
        element.after(infoElement);
    }
    
    /**
     * Переводит текст с использованием API
     */
    async translateText(text, sourceLang = 'ru', targetLang) {
        if (!text || text.trim() === '') {
            return text;
        }
        
        // Проверяем кэш переводов
        const cacheKey = `${text}|${sourceLang}|${targetLang}`;
        if (this.translationCache.has(cacheKey)) {
            this.log('Использован кэш перевода');
            return this.translationCache.get(cacheKey);
        }
        
        try {
            this.log(`API запрос: ${text.substring(0, 30)}... (${sourceLang} → ${targetLang})`);
            
            const response = await fetch(this.options.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    source_lang: sourceLang,
                    target_lang: targetLang
                })
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            const translatedText = data.translated_text || text;
            
            // Сохраняем в кэш
            this.translationCache.set(cacheKey, translatedText);
            
            return translatedText;
        } catch (error) {
            this.log(`Ошибка при вызове API перевода: ${error}`, 'error');
            console.error('Ошибка при вызове API перевода:', error);
            
            // В случае ошибки возвращаем исходный текст с префиксом целевого языка
            return `[${targetLang}] ${text}`;
        }
    }
    
    /**
     * Наблюдает за добавлением новых элементов в DOM
     */
    observeDynamicContent() {
        // Используем MutationObserver для отслеживания изменений в DOM
        const observer = new MutationObserver((mutations) => {
            let newTranslatableElements = [];
            
            mutations.forEach(mutation => {
                // Проходим только по добавленным узлам
                if (mutation.type === 'childList' && mutation.addedNodes.length) {
                    mutation.addedNodes.forEach(node => {
                        // Проверяем только элементы (не текстовые узлы)
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Проверяем, является ли сам узел переводимым
                            if (node.matches && node.matches(this.options.translateableSelector)) {
                                newTranslatableElements.push(node);
                            }
                            
                            // Проверяем детей узла
                            const childTranslatables = node.querySelectorAll(this.options.translateableSelector);
                            if (childTranslatables.length) {
                                newTranslatableElements = [...newTranslatableElements, ...childTranslatables];
                            }
                        }
                    });
                }
            });
            
            // Если нашли новые элементы и включен автоперевод
            if (newTranslatableElements.length > 0 && this.options.autoTranslate && this.currentLanguage !== 'ru') {
                this.log(`Обнаружено ${newTranslatableElements.length} новых переводимых элементов`);
                
                // Переводим каждый новый элемент
                newTranslatableElements.forEach(element => {
                    this.translateElement(element, 'ru', this.currentLanguage);
                });
            }
        });
        
        // Наблюдаем за всем body, включая изменение потомков
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        this.log('Добавлен обработчик для динамического контента');
    }
}

// Инициализация системы перевода при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация системы перевода');
    
    // Создаем экземпляр переводчика
    window.studfolioTranslator = new StudfolioTranslator();
    
    // Добавляем стили для переводчика
    const style = document.createElement('style');
    style.textContent = `
        .translation-loading {
            opacity: 0.7;
            position: relative;
        }
        
        .translation-loading::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.5) url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid"><circle cx="50" cy="50" r="30" stroke="%236c757d" stroke-width="8" fill="none" stroke-dasharray="47.12388980384689 47.12388980384689"><animateTransform attributeName="transform" type="rotate" dur="1s" repeatCount="indefinite" keyTimes="0;1" values="0 50 50;360 50 50"></animateTransform></circle></svg>') center no-repeat;
            background-size: 2em;
            z-index: 1;
        }
        
        [data-translatable] {
            position: relative;
        }
        
        .translation-info {
            font-size: 0.8em;
            color: #6c757d;
            margin-top: 0.25rem;
        }
        
        .debug-log-entry {
            margin-bottom: 3px;
            border-bottom: 1px solid #333;
            padding-bottom: 3px;
        }
        
        .log-info {
            color: #7fc9ff;
        }
        
        .log-warn {
            color: #ffc107;
        }
        
        .log-error {
            color: #dc3545;
        }
        
        .debug-toggle-btn {
            font-size: 10px !important;
        }
    `;
    document.head.appendChild(style);
}); 