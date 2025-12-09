"""Маршруты для управления страницей About"""
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.admin import admin
from app import db
from app.models import Content
from app.utils import admin_required, save_uploaded_file
from datetime import datetime
import os
from flask import current_app

@admin.route('/about', methods=['GET', 'POST'])
@admin_required
def about_edit():
    """Редактирование страницы About"""
    # Получаем текущие данные
    about_content = Content.query.filter_by(key='about_content').first()
    stats_years = Content.query.filter_by(key='stats_years').first()
    stats_masters = Content.query.filter_by(key='stats_masters').first()
    stats_countries = Content.query.filter_by(key='stats_countries').first()

    # Получаем изображения
    about_images = {}
    for i in range(1, 5):
        img_key = f'about_image_{i}'
        about_images[i] = Content.query.filter_by(key=img_key).first()

    if request.method == 'POST':
        # Сохраняем текст
        content_text = request.form.get('content', '')
        if about_content:
            about_content.content = content_text
            about_content.updated_by_id = current_user.id
            about_content.updated_at = datetime.utcnow()
        else:
            about_content = Content(
                key='about_content',
                title='О компании',
                content=content_text,
                section='about',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(about_content)

        # Сохраняем статистику
        years = request.form.get('stats_years', '')
        if stats_years:
            stats_years.content = years
            stats_years.updated_by_id = current_user.id
            stats_years.updated_at = datetime.utcnow()
        else:
            stats_years = Content(
                key='stats_years',
                title='Статистика: годы',
                content=years,
                section='about',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(stats_years)

        masters = request.form.get('stats_masters', '')
        if stats_masters:
            stats_masters.content = masters
            stats_masters.updated_by_id = current_user.id
            stats_masters.updated_at = datetime.utcnow()
        else:
            stats_masters = Content(
                key='stats_masters',
                title='Статистика: мастера',
                content=masters,
                section='about',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(stats_masters)

        countries = request.form.get('stats_countries', '')
        if stats_countries:
            stats_countries.content = countries
            stats_countries.updated_by_id = current_user.id
            stats_countries.updated_at = datetime.utcnow()
        else:
            stats_countries = Content(
                key='stats_countries',
                title='Статистика: страны',
                content=countries,
                section='about',
                content_type='text',
                updated_by_id=current_user.id
            )
            db.session.add(stats_countries)

        # Обрабатываем загрузку изображений
        for i in range(1, 5):
            img_key = f'about_image_{i}'
            img_content = Content.query.filter_by(key=img_key).first()

            # Проверяем загрузку файла
            file_key = f'image_file_{i}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    # Удаляем старое изображение, если есть (только если это файл, а не URL)
                    if img_content and img_content.content:
                        if isinstance(img_content.content, str) and not img_content.content.startswith('http'):
                            old_path = os.path.join(current_app.root_path, 'static', 'uploads', img_content.content)
                            if os.path.exists(old_path):
                                os.remove(old_path)

                    # Сохраняем новое изображение
                    filename = save_uploaded_file(file)
                    if filename:
                        if img_content:
                            img_content.content = filename
                            img_content.updated_by_id = current_user.id
                            img_content.updated_at = datetime.utcnow()
                        else:
                            img_content = Content(
                                key=img_key,
                                title=f'Изображение {i} страницы About',
                                content=filename,
                                section='about',
                                content_type='image',
                                updated_by_id=current_user.id
                            )
                            db.session.add(img_content)

            # Проверяем URL изображения (только если не был загружен файл)
            url_key = f'image_url_{i}'
            image_url = request.form.get(url_key, '').strip()
            if image_url:
                # Проверяем, был ли загружен файл в этом запросе
                file_uploaded = file_key in request.files and request.files[file_key] and request.files[file_key].filename

                if not file_uploaded:
                    # Если файл не был загружен, используем URL
                    if img_content:
                        # Если есть загруженный файл (не URL), не перезаписываем
                        if not img_content.content or (isinstance(img_content.content, str) and img_content.content.startswith('http')):
                            img_content.content = image_url
                            img_content.updated_by_id = current_user.id
                            img_content.updated_at = datetime.utcnow()
                    else:
                        img_content = Content(
                            key=img_key,
                            title=f'Изображение {i} страницы About',
                            content=image_url,
                            section='about',
                            content_type='image',
                            updated_by_id=current_user.id
                        )
                        db.session.add(img_content)

        try:
            db.session.commit()
            flash('Страница About успешно обновлена', 'success')
            return redirect(url_for('admin.about_edit'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении страницы: {e}', 'error')

    return render_template('admin/about_edit.html',
                         about_content=about_content,
                         stats_years=stats_years,
                         stats_masters=stats_masters,
                         stats_countries=stats_countries,
                         about_images=about_images)

