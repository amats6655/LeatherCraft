// Переключатель стилей для слабовидящих
document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('accessibility-toggle');
    const toggleButtonMobile = document.getElementById('accessibility-toggle-mobile');
    const body = document.body;
    const ACCESSIBILITY_MODE_KEY = 'accessibilityMode';

    // Проверяем сохраненное состояние при загрузке страницы
    if (localStorage.getItem(ACCESSIBILITY_MODE_KEY) === 'enabled') {
        body.classList.add('accessibility-mode');
        updateButtonStates();
    }

    function toggleAccessibilityMode() {
        body.classList.toggle('accessibility-mode');

        // Сохраняем предпочтение пользователя
        if (body.classList.contains('accessibility-mode')) {
            localStorage.setItem(ACCESSIBILITY_MODE_KEY, 'enabled');
        } else {
            localStorage.setItem(ACCESSIBILITY_MODE_KEY, 'disabled');
        }

        updateButtonStates();
    }

    function updateButtonStates() {
        const isEnabled = body.classList.contains('accessibility-mode');
        if (toggleButton) {
            toggleButton.classList.toggle('text-leather-dark', isEnabled);
            toggleButton.classList.toggle('text-gray-700', !isEnabled);
        }
        if (toggleButtonMobile) {
            toggleButtonMobile.classList.toggle('text-leather-dark', isEnabled);
            toggleButtonMobile.classList.toggle('text-gray-700', !isEnabled);
        }
    }

    // Обработчики событий
    if (toggleButton) {
        toggleButton.addEventListener('click', toggleAccessibilityMode);
    }

    if (toggleButtonMobile) {
        toggleButtonMobile.addEventListener('click', toggleAccessibilityMode);
    }

    // Инициализация состояния кнопок
    updateButtonStates();
});
