from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, RoleEnum
from app.utils import admin_required

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

        if user and user.check_password(password):
            if not user.is_active:
                flash('Ваш аккаунт деактивирован', 'error')
                return render_template('auth/login.html')

            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')

            # Перенаправление в зависимости от роли
            if user.is_admin() or user.is_manager():
                return redirect(next_page or url_for('admin.dashboard'))
            else:
                return redirect(next_page or url_for('main.index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
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
            flash('Регистрация успешна! Теперь вы можете войти в систему', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при регистрации', 'error')

    return render_template('auth/register.html')

