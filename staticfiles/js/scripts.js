document.addEventListener('DOMContentLoaded', () => {
    // Инициализация переключателя темы
    const themeToggler = document.getElementById('theme-toggler');
    const htmlElement = document.documentElement;
    
    // Проверяем, есть ли элементы для темной темы
    if (themeToggler) {
        const sunIcon = document.getElementById('theme-icon-sun');
        const moonIcon = document.getElementById('theme-icon-moon');
        
        // Функция для применения темы
        const applyTheme = (theme) => {
            htmlElement.setAttribute('data-bs-theme', theme);
            if (sunIcon && moonIcon) {
                if (theme === 'dark') {
                    sunIcon.classList.add('d-none');
                    moonIcon.classList.remove('d-none');
                } else {
                    sunIcon.classList.remove('d-none');
                    moonIcon.classList.add('d-none');
                }
            }
        };

        // Проверяем сохраненную тему при загрузке страницы
        const storedTheme = localStorage.getItem('theme');
        const preferredTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        const currentTheme = storedTheme || preferredTheme;
        
        applyTheme(currentTheme);

        // Обработчик клика по кнопке
        themeToggler.addEventListener('click', () => {
            const newTheme = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme); // Сохраняем выбор пользователя
            applyTheme(newTheme);
        });
    }

    // Инициализация Bootstrap компонентов, только если они доступны
    if (typeof bootstrap !== 'undefined') {
        // Убедимся, что все всплывающие подсказки Bootstrap инициализированы
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        if (tooltipTriggerList.length > 0) {
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // Убедимся, что все выпадающие меню Bootstrap инициализированы
        const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        if (dropdownElementList.length > 0) {
            dropdownElementList.map(function (dropdownToggleEl) {
                return new bootstrap.Dropdown(dropdownToggleEl);
            });
        }
    }

    // Обработка рейтинга в форме - работаем только если элементы существуют
    const ratingInputs = document.querySelectorAll('input[name="rating"]');
    const ratingStars = document.querySelectorAll('.rating-stars .fa-star');
    
    if (ratingInputs.length && ratingStars.length) {
        // Показать текущий рейтинг при загрузке
        ratingInputs.forEach(input => {
            if (input.checked) {
                const value = parseInt(input.value);
                updateRatingStars(value);
            }
        });
        
        // Обработка кликов по звездам
        ratingStars.forEach((star, index) => {
            star.addEventListener('click', () => {
                const value = index + 1;
                updateRatingStars(value);
                ratingInputs[index].checked = true;
            });
        });
        
        function updateRatingStars(value) {
            ratingStars.forEach((star, index) => {
                if (index < value) {
                    star.classList.add('checked');
                } else {
                    star.classList.remove('checked');
                }
            });
        }
    }
    
    // Анимация скролла - работаем только если элементы существуют
    const scrollLinks = document.querySelectorAll('a.scroll-link');
    if (scrollLinks.length > 0) {
        scrollLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    // Подтверждение удаления - работаем только если элементы существуют
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const confirmMessage = button.dataset.confirm || 'Вы уверены?';
                if (!confirm(confirmMessage)) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Предварительный просмотр изображения - работаем только если элементы существуют
    const imageInputs = document.querySelectorAll('.image-preview-input');
    if (imageInputs.length > 0) {
        imageInputs.forEach(input => {
            const previewId = input.dataset.preview;
            const previewElement = document.getElementById(previewId);
            
            if (previewElement) {
                input.addEventListener('change', function() {
                    if (this.files && this.files[0]) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            previewElement.src = e.target.result;
                            previewElement.style.display = 'block';
                        };
                        reader.readAsDataURL(this.files[0]);
                    }
                });
            }
        });
    }

    // Инициализация переводчика только если он существует
    if (typeof StudfolioTranslator !== 'undefined') {
        try {
            window.translator = new StudfolioTranslator({
                autoTranslate: true,
                debugMode: false
            });
        } catch (error) {
            console.error('Ошибка инициализации переводчика:', error);
        }
    }
}); 