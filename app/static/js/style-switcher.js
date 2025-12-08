// Переключатель стилей для сайта
(function() {
    'use strict';

    // Проверяем сохраненные настройки
    const savedStyle = localStorage.getItem('siteStyle') || 'standard';

    // Применяем сохраненный стиль
    if (savedStyle === 'accessibility') {
        document.body.classList.add('accessibility-mode');
    }

    // Создаем переключатель стилей
    function createStyleSwitcher() {
        const switcher = document.createElement('div');
        switcher.className = 'style-switcher';
        switcher.innerHTML = `
            <button id="standard-style" type="button">Стандартный стиль</button>
            <button id="accessibility-style" type="button">Версия для слабовидящих</button>
        `;

        document.body.appendChild(switcher);

        // Обработчики событий
        document.getElementById('standard-style').addEventListener('click', function() {
            document.body.classList.remove('accessibility-mode');
            localStorage.setItem('siteStyle', 'standard');
            updateButtonStates();
        });

        document.getElementById('accessibility-style').addEventListener('click', function() {
            document.body.classList.add('accessibility-mode');
            localStorage.setItem('siteStyle', 'accessibility');
            updateButtonStates();
        });

        // Обновление состояния кнопок
        function updateButtonStates() {
            const isAccessibility = document.body.classList.contains('accessibility-mode');
            document.getElementById('standard-style').style.opacity = isAccessibility ? '0.6' : '1';
            document.getElementById('accessibility-style').style.opacity = isAccessibility ? '1' : '0.6';
        }

        updateButtonStates();
    }

    // Создаем переключатель после загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createStyleSwitcher);
    } else {
        createStyleSwitcher();
    }
})();

