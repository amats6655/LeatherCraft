from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.admin import admin
from app import db
from app.models import ContactMessage, HeroSlide
from app.utils import admin_required
import os


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


# Управление слайдами Hero
@admin.route('/hero-slides')
@admin_required
def hero_slides():
    """Список слайдов Hero"""
    slides = HeroSlide.query.order_by(HeroSlide.order, HeroSlide.id).all()
    return render_template('admin/hero_slides.html', slides=slides)


@admin.route('/hero-slides/new', methods=['GET', 'POST'])
@admin_required
def hero_slide_new():
    """Создание нового слайда"""
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        image_url = request.form.get('image_url', '').strip()
        order = int(request.form.get('order', 0) or 0)
        is_active = request.form.get('is_active') == 'on'
        link_url = request.form.get('link_url', '').strip()
        link_text = request.form.get('link_text', '').strip()

        # Обработка загрузки файла
        image_file = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                from app.utils import save_uploaded_file
                image_file = save_uploaded_file(file)

        slide = HeroSlide(
            title=title,
            subtitle=subtitle,
            image_url=image_url if not image_file else None,
            image_file=image_file,
            order=order,
            is_active=is_active,
            link_url=link_url,
            link_text=link_text
        )

        try:
            db.session.add(slide)
            db.session.commit()
            flash('Слайд успешно создан', 'success')
            return redirect(url_for('admin.hero_slides'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании слайда: {str(e)}', 'error')

    return render_template('admin/hero_slide_edit.html', slide=None)


@admin.route('/hero-slides/<int:slide_id>/edit', methods=['GET', 'POST'])
@admin_required
def hero_slide_edit(slide_id):
    """Редактирование слайда"""
    slide = HeroSlide.query.get_or_404(slide_id)

    if request.method == 'POST':
        slide.title = request.form.get('title')
        slide.subtitle = request.form.get('subtitle')
        slide.order = int(request.form.get('order', 0) or 0)
        slide.is_active = request.form.get('is_active') == 'on'
        slide.link_url = request.form.get('link_url', '').strip()
        slide.link_text = request.form.get('link_text', '').strip()

        # Обработка загрузки нового файла
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                from app.utils import save_uploaded_file
                # Удаляем старый файл, если есть
                if slide.image_file:
                    old_path = os.path.join(current_app.root_path, 'static', 'uploads', slide.image_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                slide.image_file = save_uploaded_file(file)
                slide.image_url = None  # Очищаем URL, если загружен файл

        # Если указан URL и нет файла, используем URL
        image_url = request.form.get('image_url', '').strip()
        if image_url and not slide.image_file:
            slide.image_url = image_url

        try:
            db.session.commit()
            flash('Слайд успешно обновлен', 'success')
            return redirect(url_for('admin.hero_slides'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении слайда: {str(e)}', 'error')

    return render_template('admin/hero_slide_edit.html', slide=slide)


@admin.route('/hero-slides/<int:slide_id>/delete', methods=['POST'])
@admin_required
def hero_slide_delete(slide_id):
    """Удаление слайда"""
    slide = HeroSlide.query.get_or_404(slide_id)

    try:
        # Удаляем файл, если есть
        if slide.image_file:
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', slide.image_file)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(slide)
        db.session.commit()
        flash('Слайд успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении слайда: {str(e)}', 'error')

    return redirect(url_for('admin.hero_slides'))

