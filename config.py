import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///leathercraft.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Настройки для работы за прокси
    TRUSTED_PROXIES = ['127.0.0.1']  # IP адреса доверенных прокси
    PROXY_COUNT = 1  # Количество прокси перед приложением

    # Настройки логирования
    LOG_IP_ADDRESSES = True

    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Роли пользователей
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_USER = 'user'
