// Управление компактной статистикой - одна кнопка для всех секций
document.addEventListener('DOMContentLoaded', function() {
    const statsContainer = document.getElementById('stats-container');
    const toggleAllBtn = document.getElementById('toggle-all-stats');
    
    if (!statsContainer || !toggleAllBtn) return;
    
    // Проверяем состояние из localStorage
    const isCollapsed = localStorage.getItem('statsCollapsed') === 'true';
    
    // Устанавливаем начальное состояние
    if (isCollapsed) {
        collapseAllStats();
        updateToggleButton(true);
    } else {
        expandAllStats();
        updateToggleButton(false);
    }
    
    // Обработчик клика на кнопку
    toggleAllBtn.addEventListener('click', function() {
        const currentlyCollapsed = statsContainer.classList.contains('all-collapsed');
        
        if (currentlyCollapsed) {
            expandAllStats();
            updateToggleButton(false);
            localStorage.setItem('statsCollapsed', 'false');
        } else {
            collapseAllStats();
            updateToggleButton(true);
            localStorage.setItem('statsCollapsed', 'true');
        }
        
        // Запускаем анимацию счетчиков при разворачивании
        if (!currentlyCollapsed) {
            setTimeout(animateCounters, 300);
        }
    });
    
    // Функция свернуть все
    function collapseAllStats() {
        statsContainer.classList.add('all-collapsed');
        
        // Анимация для каждого блока с задержкой
        const cards = document.querySelectorAll('.compact-stat-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            }, index * 50);
        });
    }
    
    // Функция развернуть все
    function expandAllStats() {
        statsContainer.classList.remove('all-collapsed');
        
        // Анимация для каждого блока с задержкой
        const cards = document.querySelectorAll('.compact-stat-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            }, index * 50);
        });
    }
    
    // Обновление текста и иконки кнопки
    function updateToggleButton(isCollapsed) {
        if (isCollapsed) {
            toggleAllBtn.innerHTML = `
                <i class="fas fa-chevron-down"></i>
                <span>Развернуть статистику</span>
            `;
            toggleAllBtn.classList.add('collapsed');
        } else {
            toggleAllBtn.innerHTML = `
                <i class="fas fa-chevron-up"></i>
                <span>Свернуть статистику</span>
            `;
            toggleAllBtn.classList.remove('collapsed');
        }
    }
    
    // Анимация счетчиков при загрузке
    function animateCounters() {
        const counters = document.querySelectorAll('.compact-stat-value, .compact-time-count, .compact-quality-value');
        
        counters.forEach(counter => {
            const finalValue = parseFloat(counter.textContent.replace(/[^\d.]/g, ''));
            if (!isNaN(finalValue) && finalValue > 0) {
                animateCounter(counter, finalValue);
            }
        });
    }
    
    // Функция анимации счетчика
    function animateCounter(element, target) {
        const duration = 1000;
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        // Сохраняем оригинальный текст если он содержит не только число
        const originalText = element.textContent;
        const hasSymbols = /[^\d.]/.test(originalText);
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = originalText;
                clearInterval(timer);
            } else {
                if (hasSymbols) {
                    // Если есть символы (% и т.д.), сохраняем их
                    const match = originalText.match(/([^\d.]*)([\d.]+)([^\d.]*)/);
                    if (match) {
                        element.textContent = match[1] + Math.round(current) + match[3];
                    }
                } else {
                    element.textContent = Math.round(current);
                }
            }
        }, 16);
    }
    
    // Анимация прогресс-баров
    function animateProgressBars() {
        const progressBars = document.querySelectorAll('.compact-progress-fill');
        
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
                bar.style.width = width;
            }, 300);
        });
    }
    
    // Горячая клавиша для сворачивания/разворачивания (Space)
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        if (e.code === 'Space' && e.ctrlKey) {
            e.preventDefault();
            toggleAllBtn.click();
        }
    });
    
    // Добавляем подсказку для кнопки
    toggleAllBtn.title = 'Клик - свернуть/развернуть все\nCtrl+Space - горячая клавиша';
    
    // Запускаем анимации при загрузке
    setTimeout(() => {
        if (!isCollapsed) {
            animateCounters();
            animateProgressBars();
        }
    }, 500);
    
    // Функции для глобального использования
    window.statsManager = {
        collapseAll: collapseAllStats,
        expandAll: expandAllStats,
        toggleAll: function() {
            toggleAllBtn.click();
        }
    };
});