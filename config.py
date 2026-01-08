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
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'  # DEBUG, INFO, WARNING, ERROR
    LOG_DIR = os.environ.get('LOG_DIR') or 'logs'  # Директория для логов
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB по умолчанию
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))  # Количество резервных файлов
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json')  # 'json', 'text', или 'auto' (auto = json для продакшена, text для разработки)

    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Роли пользователей
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_USER = 'user'
