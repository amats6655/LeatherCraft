from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
import logging

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


@login_manager.user_loader
def load_users(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def get_client_ip():
    """
    Получение реального IP адреса клиента.
    Работает только в контексте запроса.
    """
    if not request:
        return None

    # Проверяем заголовки в порядке приоритета
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For может содержать цепочку: client, proxy1, proxy2
        ip_chain = request.headers.get('X-Forwarded-For', '').split(',')
        # Берем первый IP в цепочке (клиентский)
        return ip_chain[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('CF-Connecting-IP'):  # Для Cloudflare
        return request.headers.get('CF-Connecting-IP')
    else:
        return request.remote_addr


def create_app():
    app = Flask(__name__)

    # Загрузка конфигурации
    app.config.from_object(Config)

    # ВАЖНО: Middleware для работы за прокси (должен быть ПЕРВЫМ)
    # Указываем количество доверенных прокси (обычно 1 для Nginx)
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # Количество прокси для X-Forwarded-For
        x_proto=1,  # Количество прокси для X-Forwarded-Proto
        x_host=1,  # Количество прокси для X-Host
        x_port=0,  # Не используем X-Port
        x_prefix=0  # Не используем X-Prefix
    )

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице'
    login_manager.login_message_category = 'info'

    # Настройка логирования
    setup_request_logging(app)

    # Регистрацию Blueprint'ов
    from app.routes import main
    from app.auth import auth
    from app.admin import admin
    from app.user import user

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')

    # Middleware для логирования всех запросов
    @app.before_request
    def log_request_info():
        """Логирование информации о каждом запросе"""
        if app.debug:  # Логируем только в режиме отладки
            client_ip = get_client_ip()
            app.logger.info(
                f"Request: {request.method} {request.path} | "
                f"IP: {client_ip} | "
                f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
            )

    # Регистрация обработчиков ошибок на уровне приложения
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        app.logger.warning(f"403 Forbidden: IP={get_client_ip()}, Path={request.path}")
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        app.logger.info(f"404 Not Found: IP={get_client_ip()}, Path={request.path}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        app.logger.error(f"500 Internal Error: IP={get_client_ip()}, Path={request.path}, Error={error}")
        db.session.rollback()
        return render_template('500.html'), 500

    # Context processor для передачи данных во все шаблоны
    @app.context_processor
    def inject_global_data():
        """Добавляет глобальные данные во все шаблоны"""
        from app.models import Content

        # Социальные сети
        social_instagram = Content.query.filter_by(key='social_instagram').first()
        social_facebook = Content.query.filter_by(key='social_facebook').first()
        social_telegram = Content.query.filter_by(key='social_telegram').first()

        return {
            'social_instagram_url': social_instagram.content if social_instagram and social_instagram.content else None,
            'social_facebook_url': social_facebook.content if social_facebook and social_facebook.content else None,
            'social_telegram_url': social_telegram.content if social_telegram and social_telegram.content else None,
            'get_client_ip': get_client_ip,  # Функция для получения IP
        }

    return app


def setup_request_logging(app):
    """Настройка форматирования логов с IP-адресами"""

    class IPAddressFormatter(logging.Formatter):
        """Кастомный форматтер для логов с IP-адресом"""

        def format(self, record):
            # Добавляем IP адрес к записи лога если есть контекст запроса
            try:
                # Используем get_client_ip через app context
                with app.app_context():
                    if hasattr(request, 'url_rule') and request.url_rule:
                        record.client_ip = get_client_ip() or 'N/A'
                    else:
                        record.client_ip = 'N/A'
            except RuntimeError:
                record.client_ip = 'N/A'

            return super().format(record)

    # Настраиваем формат логов
    formatter = IPAddressFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - [IP: %(client_ip)s] - %(message)s'
    )

    # Применяем форматтер к хендлеру
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)