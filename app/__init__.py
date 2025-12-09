from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

@login_manager.user_loader
def load_users(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    # Загрузка конфигурации
    app.config.from_object(Config)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице'
    login_manager.login_message_category = 'info'

    # Регистрацию Blueprint'ов
    from app.routes import main
    from app.auth import auth
    from app.admin import admin
    from app.user import user

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')

    # Регистрация обработчиков ошибок на уровне приложения
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('500.html'), 500

    # Context processor для передачи данных во все шаблоны
    @app.context_processor
    def inject_social_links():
        """Добавляет ссылки на социальные сети во все шаблоны"""
        from app.models import Content
        social_instagram = Content.query.filter_by(key='social_instagram').first()
        social_facebook = Content.query.filter_by(key='social_facebook').first()
        social_telegram = Content.query.filter_by(key='social_telegram').first()

        return {
            'social_instagram_url': social_instagram.content if social_instagram and social_instagram.content else None,
            'social_facebook_url': social_facebook.content if social_facebook and social_facebook.content else None,
            'social_telegram_url': social_telegram.content if social_telegram and social_telegram.content else None,
        }

    return app