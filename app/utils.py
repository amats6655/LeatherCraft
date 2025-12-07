from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from app.models import RoleEnum

def role_required(*roles):
    """Декоратор для проверки роли пользователя"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    @role_required(RoleEnum.ADMIN)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Декоратор для проверки прав менеджера или администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def content_manager_required(f):
    """Декоратор для проверки прав управления контентом"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.can_manage_content():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

