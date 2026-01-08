from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt, get_client_ip
from app.models import User, RoleEnum
from app.utils import admin_required
import logging

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')

        if not username or not password:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()
        auth_logger = logging.getLogger('app.auth')

        if user and user.check_password(password):
            if not user.is_active:
                # Логируем попытку входа в деактивированный аккаунт
                auth_logger.warning(
                    f"Login attempt to deactivated account: {username}",
                    extra={
                        'action': 'login_attempt',
                        'status': 'failed',
                        'reason': 'account_deactivated',
                        'username': username,
                        'user_id': user.id if user else None,
                        'ip_address': get_client_ip(),
                        'user_agent': request.headers.get('User-Agent', 'N/A')
                    }
                )
                flash('Ваш аккаунт деактивирован', 'error')
                return render_template('auth/login.html')

            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')

            # Логируем успешный вход
            auth_logger.info(
                f"User logged in successfully: {username}",
                extra={
                    'action': 'user_login',
                    'status': 'success',
                    'user_id': user.id,
                    'username': username,
                    'user_role': user.role.value if hasattr(user.role, 'value') else str(user.role),
                    'remember_me': bool(request.form.get('remember')),
                    'ip_address': get_client_ip(),
                    'user_agent': request.headers.get('User-Agent', 'N/A')
                }
            )

            # Перенаправление в зависимости от роли
            if user.is_admin() or user.is_manager():
                return redirect(next_page or url_for('admin.dashboard'))
            else:
                return redirect(next_page or url_for('main.index'))
        else:
            # Логируем неудачную попытку входа
            auth_logger.warning(
                f"Failed login attempt: {username}",
                extra={
                    'action': 'login_attempt',
                    'status': 'failed',
                    'reason': 'invalid_credentials',
                    'username': username,
                    'ip_address': get_client_ip(),
                    'user_agent': request.headers.get('User-Agent', 'N/A')
                }
            )
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    # Логируем выход перед logout_user, чтобы сохранить информацию о пользователе
    auth_logger = logging.getLogger('app.auth')
    user_id = current_user.id
    username = current_user.username
    
    logout_user()
    
    auth_logger.info(
        f"User logged out: {username}",
        extra={
            'action': 'user_logout',
            'status': 'success',
            'user_id': user_id,
            'username': username,
            'ip_address': get_client_ip(),
            'user_agent': request.headers.get('User-Agent', 'N/A')
        }
    )
    
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        full_name = request.form.get('full_name', '').strip() if request.form.get('full_name') else ''
        phone = request.form.get('phone', '').strip() if request.form.get('phone') else ''

        # Валидация
        if not all([username, email, password, password_confirm]):
            flash('Пожалуйста, заполните все обязательные поля', 'error')
            return render_template('auth/register.html')

        if password != password_confirm:
            flash('Пароли не совпадают', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('auth/register.html')

        # Создание пользователя
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=RoleEnum.USER
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            
            # Логируем успешную регистрацию
            auth_logger = logging.getLogger('app.auth')
            auth_logger.info(
                f"New user registered: {username}",
                extra={
                    'action': 'user_register',
                    'status': 'success',
                    'user_id': user.id,
                    'username': username,
                    'email': email,
                    'ip_address': get_client_ip(),
                    'user_agent': request.headers.get('User-Agent', 'N/A')
                }
            )
            
            flash('Регистрация успешна! Теперь вы можете войти в систему', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            
            # Логируем ошибку регистрации
            auth_logger = logging.getLogger('app.auth')
            auth_logger.error(
                f"Registration failed: {str(e)}",
                exc_info=True,
                extra={
                    'action': 'user_register',
                    'status': 'error',
                    'username': username,
                    'email': email,
                    'ip_address': get_client_ip(),
                    'user_agent': request.headers.get('User-Agent', 'N/A')
                }
            )
            
            flash('Произошла ошибка при регистрации', 'error')

    return render_template('auth/register.html')

