/**
 * Studfolio - Main JavaScript File
 * Modern animation and UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {

    // Плавная прокрутка к якорям
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Анимация счетчиков
    const animateCounter = (el) => {
        const target = parseInt(el.getAttribute('data-count'));
        const duration = 1500; // ms
        const increment = target / (duration / 16); // 60fps → 16ms per frame
        
        let current = 0;
        const timer = setInterval(() => {
            current += increment;
            el.textContent = Math.round(current);
            
            if (current >= target) {
                el.textContent = target;
                clearInterval(timer);
            }
        }, 16);
    };

    // Инициализация счетчиков при видимости
    const counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => {
            observer.observe(counter);
        });
    }

    // Кнопка возврата наверх
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });

        backToTopButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Включение тултипов Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length) {
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    // Включение toast-уведомлений Bootstrap
    const toastElList = document.querySelectorAll('.toast');
    if (toastElList.length) {
        [...toastElList].map(toastEl => new bootstrap.Toast(toastEl, { delay: 5000 }));
    }
    
    // Сохранение активных табов в localStorage
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', event => {
            const id = event.target.getAttribute('data-bs-target');
            localStorage.setItem('activeTab', id);
        });
    });

    // Восстановление активного таба
    const activeTab = localStorage.getItem('activeTab');
    if (activeTab) {
        const triggerEl = document.querySelector(`[data-bs-toggle="tab"][data-bs-target="${activeTab}"]`);
        if (triggerEl) {
            new bootstrap.Tab(triggerEl).show();
        }
    }

    // Анимация карточек при наведении
    document.querySelectorAll('.floating-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.classList.add('floating-animation-up');
        });
        
        card.addEventListener('mouseleave', () => {
            card.classList.remove('floating-animation-up');
            setTimeout(() => {
                card.style.transform = 'translateY(0)';
            }, 300);
        });
    });

    // Инициализация ленивой загрузки изображений
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if ('loading' in HTMLImageElement.prototype) {
        console.log('Browser supports native image lazy-loading');
    } else {
        console.log('Browser does not support native image lazy-loading');
        // Здесь можно добавить полифил для lazy loading
    }
});

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const newContainer = document.createElement('div');
        newContainer.id = 'toast-container';
        newContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(newContainer);
    }
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toastEl);
    
    const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
    toast.show();
    
    // Удаляем toast после скрытия
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
} 