from functools import wraps
from flask import abort, current_app, request
from flask_login import current_user
from app.models import RoleEnum
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime
from app import get_client_ip
from app.logging_config import mask_sensitive_data


def admin_required(f):
    """Декоратор для проверки прав администратора"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        if current_user.role != RoleEnum.ADMIN:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def manager_required(f):
    """Декоратор для проверки прав менеджера или администратора"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        if current_user.role not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Проверяет, разрешено ли расширение файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, folder=None):
    """Сохраняет загруженный файл и возвращает имя файла"""
    if file and allowed_file(file.filename):
        # Используем папку из конфигурации, если не указана
        if folder is None:
            folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        # Создаем уникальное имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"

        # Создаем папку, если её нет
        upload_path = os.path.join(current_app.root_path, 'static', folder)
        os.makedirs(upload_path, exist_ok=True)

        # Сохраняем файл
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)

        return unique_filename
    return None


def get_image_url(image_file=None, image_url=None):
    """Возвращает URL изображения (приоритет у загруженного файла)"""
    if image_file:
        return f'/static/uploads/{image_file}'
    return image_url or ''


def log_action(action_name, entity_type=None, entity_id=None, extra_data=None, logger_name='app.actions'):
    """
    Универсальный декоратор для логирования действий пользователей.
    
    Args:
        action_name: Название действия (например, 'user_login', 'product_create')
        entity_type: Тип сущности (например, 'product', 'user', 'order')
        entity_id: ID сущности
        extra_data: Дополнительные данные для логирования
        logger_name: Имя логгера ('app.actions', 'app.auth', и т.д.)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            
            # Получаем информацию о пользователе
            user_id = None
            username = None
            if current_user.is_authenticated:
                user_id = current_user.id
                username = current_user.username
            
            # Выполняем функцию
            try:
                result = func(*args, **kwargs)
                status = 'success'
                error_message = None
            except Exception as e:
                status = 'error'
                error_message = str(e)
                logger.error(
                    f"Action '{action_name}' failed: {error_message}",
                    exc_info=True,
                    extra={
                        'action': action_name,
                        'status': status,
                        'user_id': user_id,
                        'username': username,
                        'entity_type': entity_type,
                        'entity_id': entity_id,
                        'ip_address': get_client_ip(),
                        'extra_data': mask_sensitive_data(extra_data) if extra_data else None
                    }
                )
                raise
            
            # Логируем успешное выполнение
            log_data = {
                'action': action_name,
                'status': status,
                'user_id': user_id,
                'username': username,
                'ip_address': get_client_ip(),
                'method': request.method,
                'path': request.path
            }
            
            if entity_type:
                log_data['entity_type'] = entity_type
            if entity_id:
                log_data['entity_id'] = entity_id
            if extra_data:
                log_data['extra_data'] = mask_sensitive_data(extra_data)
            
            logger.info(
                f"Action '{action_name}' completed successfully",
                extra=log_data
            )
            
            return result
        return wrapper
    return decorator


def log_admin_action(action_name, entity_type=None, entity_id=None, extra_data=None):
    """
    Декоратор для логирования админских действий.
    Использует логгер 'app.actions' с пометкой о том, что это админское действие.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('app.actions')
            
            if not current_user.is_authenticated:
                abort(403)
            
            user_id = current_user.id
            username = current_user.username
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            
            try:
                result = func(*args, **kwargs)
                status = 'success'
            except Exception as e:
                status = 'error'
                logger.error(
                    f"Admin action '{action_name}' failed: {str(e)}",
                    exc_info=True,
                    extra={
                        'action': action_name,
                        'status': status,
                        'user_id': user_id,
                        'username': username,
                        'user_role': user_role,
                        'entity_type': entity_type,
                        'entity_id': entity_id,
                        'ip_address': get_client_ip(),
                        'extra_data': mask_sensitive_data(extra_data) if extra_data else None
                    }
                )
                raise
            
            logger.info(
                f"Admin action '{action_name}' completed",
                extra={
                    'action': action_name,
                    'status': status,
                    'user_id': user_id,
                    'username': username,
                    'user_role': user_role,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'ip_address': get_client_ip(),
                    'method': request.method,
                    'path': request.path,
                    'extra_data': mask_sensitive_data(extra_data) if extra_data else None
                }
            )
            
            return result
        return wrapper
    return decorator


def log_user_action(action_name, entity_type=None, entity_id=None, extra_data=None):
    """
    Декоратор для логирования пользовательских действий.
    Использует логгер 'app.actions'.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('app.actions')
            
            if not current_user.is_authenticated:
                abort(403)
            
            user_id = current_user.id
            username = current_user.username
            
            try:
                result = func(*args, **kwargs)
                status = 'success'
            except Exception as e:
                status = 'error'
                logger.error(
                    f"User action '{action_name}' failed: {str(e)}",
                    exc_info=True,
                    extra={
                        'action': action_name,
                        'status': status,
                        'user_id': user_id,
                        'username': username,
                        'entity_type': entity_type,
                        'entity_id': entity_id,
                        'ip_address': get_client_ip(),
                        'extra_data': mask_sensitive_data(extra_data) if extra_data else None
                    }
                )
                raise
            
            logger.info(
                f"User action '{action_name}' completed",
                extra={
                    'action': action_name,
                    'status': status,
                    'user_id': user_id,
                    'username': username,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'ip_address': get_client_ip(),
                    'method': request.method,
                    'path': request.path,
                    'extra_data': mask_sensitive_data(extra_data) if extra_data else None
                }
            )
            
            return result
        return wrapper
    return decorator
