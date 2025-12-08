from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.admin import admin
from app import db
from app.models import ContactMessage
from app.utils import admin_required


# Управление обращениями
@admin.route('/messages')
@admin_required
def messages():
    """Список обращений"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    filter_unread = request.args.get('unread', 'false') == 'true'

    query = ContactMessage.query
    if filter_unread:
        query = query.filter_by(is_read=False)

    pagination = query.order_by(ContactMessage.created_at.desc()).paginate(page=page, per_page=per_page,
                                                                           error_out=False)
    messages_list = pagination.items

    return render_template('admin/messages.html', messages=messages_list, pagination=pagination,
                           filter_unread=filter_unread)


@admin.route('/messages/<int:message_id>')
@admin_required
def message_detail(message_id):
    """Детали обращения"""
    message = ContactMessage.query.get_or_404(message_id)

    # Помечаем как прочитанное
    if not message.is_read:
        message.is_read = True
        db.session.commit()

    return render_template('admin/message_detail.html', message=message)


@admin.route('/messages/<int:message_id>/delete', methods=['POST'])
@admin_required
def message_delete(message_id):
    """Удаление обращения"""
    message = ContactMessage.query.get_or_404(message_id)

    try:
        db.session.delete(message)
        db.session.commit()
        flash('Обращение успешно удалено', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении обращения', 'error')

    return redirect(url_for('admin.messages'))

