"""
Конфигурация логирования для production-ready системы логирования.
Поддерживает JSON и текстовый форматы, ротацию файлов.
"""
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from flask import request, has_request_context
from app import get_client_ip


class JSONFormatter(logging.Formatter):
    """JSON форматтер для продакшена"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Добавляем контекст запроса, если доступен
        if has_request_context():
            log_data['ip_address'] = get_client_ip() or 'N/A'
            log_data['method'] = request.method
            log_data['path'] = request.path
            log_data['user_agent'] = request.headers.get('User-Agent', 'N/A')
            
            # Добавляем информацию о пользователе, если есть
            try:
                from flask_login import current_user
                if current_user.is_authenticated:
                    log_data['user_id'] = current_user.id
                    log_data['username'] = current_user.username
            except:
                pass
        
        # Добавляем дополнительные поля из record
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'status'):
            log_data['status'] = record.status
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'entity_type'):
            log_data['entity_type'] = record.entity_type
        if hasattr(record, 'entity_id'):
            log_data['entity_id'] = record.entity_id
        if hasattr(record, 'extra_data'):
            log_data['extra_data'] = record.extra_data
        
        # Добавляем информацию об исключении, если есть
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Текстовый форматтер для разработки"""
    
    def format(self, record):
        # Базовый формат
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname
        logger = record.name
        message = record.getMessage()
        
        # Добавляем IP адрес
        ip = 'N/A'
        if has_request_context():
            ip = get_client_ip() or 'N/A'
        
        # Формируем строку
        log_line = f"{timestamp} - {logger} - {level} - [IP: {ip}]"
        
        # Добавляем информацию о пользователе
        if hasattr(record, 'user_id'):
            log_line += f" - User: {getattr(record, 'username', 'N/A')} (ID: {record.user_id})"
        
        # Добавляем действие
        if hasattr(record, 'action'):
            log_line += f" - Action: {record.action}"
        
        # Добавляем статус
        if hasattr(record, 'status'):
            log_line += f" - Status: {record.status}"
        
        # Добавляем время выполнения
        if hasattr(record, 'duration_ms'):
            log_line += f" - Duration: {record.duration_ms}ms"
        
        # Добавляем статус код
        if hasattr(record, 'status_code'):
            log_line += f" - Status Code: {record.status_code}"
        
        # Добавляем информацию о сущности
        if hasattr(record, 'entity_type') and hasattr(record, 'entity_id'):
            log_line += f" - {record.entity_type}: {record.entity_id}"
        
        # Добавляем сообщение
        log_line += f" - {message}"
        
        # Добавляем исключение, если есть
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"
        
        return log_line


def mask_sensitive_data(data):
    """
    Маскирует чувствительные данные в словаре для логирования.
    """
    if not isinstance(data, dict):
        return data
    
    sensitive_keys = ['password', 'password_hash', 'token', 'secret', 'api_key', 'authorization']
    masked_data = {}
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            masked_data[key] = '***MASKED***'
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value)
        else:
            masked_data[key] = value
    
    return masked_data


def setup_logging(app):
    """
    Настраивает систему логирования для приложения.
    
    Args:
        app: Flask приложение
    """
    # Получаем настройки из конфигурации
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_dir = app.config.get('LOG_DIR', 'logs')
    log_max_bytes = app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024)  # 10MB
    log_backup_count = app.config.get('LOG_BACKUP_COUNT', 5)
    log_format = app.config.get('LOG_FORMAT', 'auto')
    
    # Определяем формат (auto = json для продакшена, text для разработки)
    if log_format == 'auto':
        use_json = not app.debug
    elif log_format == 'json':
        use_json = True
    else:
        use_json = False
    
    # Преобразуем относительный путь в абсолютный относительно корня приложения
    # Это важно для работы с Gunicorn, где рабочая директория может отличаться
    if not os.path.isabs(log_dir):
        # Получаем корневую директорию приложения (родительскую от app/)
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(app_root, log_dir)
    
    # Создаем директорию для логов, если её нет
    # Используем exist_ok=True для безопасности в многопроцессном режиме
    os.makedirs(log_dir, exist_ok=True)
    
    # Выбираем форматтер
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - [IP: %(client_ip)s] - %(message)s'
        )
    
    # Настройка основного логгера приложения
    app.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Удаляем существующие хендлеры
    # В Gunicorn это важно делать, так как хендлеры могут дублироваться
    app.logger.handlers.clear()
    
    # Консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # Отключаем распространение логов в корневой логгер
    # Это предотвращает дублирование логов в Gunicorn
    app.logger.propagate = False
    
    # Файловый хендлер для общих логов
    app_log_file = os.path.join(log_dir, 'app.log')
    app_file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding='utf-8'
    )
    app_file_handler.setLevel(logging.DEBUG)
    app_file_handler.setFormatter(formatter)
    app.logger.addHandler(app_file_handler)
    
    # Логгер для HTTP запросов
    requests_logger = logging.getLogger('app.requests')
    requests_logger.setLevel(logging.INFO)
    requests_log_file = os.path.join(log_dir, 'requests.log')
    requests_file_handler = RotatingFileHandler(
        requests_log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding='utf-8'
    )
    requests_file_handler.setLevel(logging.INFO)
    requests_file_handler.setFormatter(formatter)
    requests_logger.addHandler(requests_file_handler)
    requests_logger.addHandler(console_handler)
    requests_logger.propagate = False
    
    # Логгер для действий пользователей
    actions_logger = logging.getLogger('app.actions')
    actions_logger.setLevel(logging.INFO)
    actions_log_file = os.path.join(log_dir, 'actions.log')
    actions_file_handler = RotatingFileHandler(
        actions_log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding='utf-8'
    )
    actions_file_handler.setLevel(logging.INFO)
    actions_file_handler.setFormatter(formatter)
    actions_logger.addHandler(actions_file_handler)
    actions_logger.addHandler(console_handler)
    actions_logger.propagate = False
    
    # Логгер для аутентификации
    auth_logger = logging.getLogger('app.auth')
    auth_logger.setLevel(logging.INFO)
    auth_log_file = os.path.join(log_dir, 'auth.log')
    auth_file_handler = RotatingFileHandler(
        auth_log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding='utf-8'
    )
    auth_file_handler.setLevel(logging.INFO)
    auth_file_handler.setFormatter(formatter)
    auth_logger.addHandler(auth_file_handler)
    auth_logger.addHandler(console_handler)
    auth_logger.propagate = False
    
    # Логгер для ошибок
    errors_logger = logging.getLogger('app.errors')
    errors_logger.setLevel(logging.ERROR)
    errors_log_file = os.path.join(log_dir, 'errors.log')
    errors_file_handler = RotatingFileHandler(
        errors_log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding='utf-8'
    )
    errors_file_handler.setLevel(logging.ERROR)
    errors_file_handler.setFormatter(formatter)
    errors_logger.addHandler(errors_file_handler)
    errors_logger.addHandler(console_handler)
    errors_logger.propagate = False
    
    # Настройка логгера Werkzeug (встроенный сервер Flask)
    # Полностью отключаем стандартное логирование Werkzeug в консоль,
    # так как мы логируем все запросы через наш middleware в нужном формате
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.handlers.clear()  # Удаляем все стандартные хендлеры
    werkzeug_logger.setLevel(logging.CRITICAL)  # Устанавливаем высокий уровень, чтобы ничего не показывать
    werkzeug_logger.propagate = False  # Отключаем распространение логов
    
    # Также отключаем логирование запросов Flask в консоль
    # (они дублируют наши логи из middleware)
    flask_logger = logging.getLogger('flask')
    flask_logger.handlers.clear()
    flask_logger.setLevel(logging.CRITICAL)
    flask_logger.propagate = False
    
    # Настройка логгера Gunicorn для работы с нашей системой логирования
    # Gunicorn использует свой собственный логгер, который может конфликтовать
    gunicorn_logger = logging.getLogger('gunicorn')
    gunicorn_logger.propagate = False  # Отключаем распространение, чтобы не дублировать логи
    
    # Логируем информацию о настройке
    # Используем файловый хендлер, так как консольный может не работать в Gunicorn
    app.logger.info(f"Logging configured: format={'JSON' if use_json else 'Text'}, level={log_level}, dir={log_dir}")
