from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from app.models import RoleEnum
from werkzeug.utils import secure_filename
import os
from datetime import datetime


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


def save_uploaded_file(file, folder='uploads'):
    """Сохраняет загруженный файл и возвращает имя файла"""
    if file and allowed_file(file.filename):
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
