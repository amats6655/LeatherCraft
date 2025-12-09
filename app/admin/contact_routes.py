"""Маршруты для управления страницей Contact"""
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.admin import admin
from app import db
from app.models import Content
from app.utils import admin_required
from datetime import datetime


@admin.route('/contact', methods=['GET', 'POST'])
@admin_required
def contact_edit():
    """Редактирование страницы Contact"""
    # Получаем текущие данные
    contact_address = Content.query.filter_by(key='contact_address').first()
    contact_phone = Content.query.filter_by(key='contact_phone').first()
    contact_email = Content.query.filter_by(key='contact_email').first()
    contact_hours = Content.query.filter_by(key='contact_hours').first()

    if request.method == 'POST':
        # Сохраняем адрес
        address = request.form.get('address', '')
        if contact_address:
            contact_address.content = address
            contact_address.updated_by_id = current_user.id
            contact_address.updated_at = datetime.utcnow()
        else:
            contact_address = Content(
                key='contact_address',
                title='Адрес',
                content=address,
                section='contact',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(contact_address)

        # Сохраняем телефон
        phone = request.form.get('phone', '')
        if contact_phone:
            contact_phone.content = phone
            contact_phone.updated_by_id = current_user.id
            contact_phone.updated_at = datetime.utcnow()
        else:
            contact_phone = Content(
                key='contact_phone',
                title='Телефон',
                content=phone,
                section='contact',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(contact_phone)

        # Сохраняем email
        email = request.form.get('email', '')
        if contact_email:
            contact_email.content = email
            contact_email.updated_by_id = current_user.id
            contact_email.updated_at = datetime.utcnow()
        else:
            contact_email = Content(
                key='contact_email',
                title='Email',
                content=email,
                section='contact',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(contact_email)

        # Сохраняем часы работы
        hours = request.form.get('hours', '')
        if contact_hours:
            contact_hours.content = hours
            contact_hours.updated_by_id = current_user.id
            contact_hours.updated_at = datetime.utcnow()
        else:
            contact_hours = Content(
                key='contact_hours',
                title='Часы работы',
                content=hours,
                section='contact',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(contact_hours)

        try:
            db.session.commit()
            flash('Страница Contact успешно обновлена', 'success')
            return redirect(url_for('admin.contact_edit'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении страницы: {e}', 'error')

    return render_template('admin/contact_edit.html',
                           contact_address=contact_address,
                           contact_phone=contact_phone,
                           contact_email=contact_email,
                           contact_hours=contact_hours)

