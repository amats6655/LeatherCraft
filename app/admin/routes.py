from flask import render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from app.admin import admin
from app import db
from app.models import User, Product, Category, Order, BlogPost, Content, ContactMessage, HeroSlide, RoleEnum, \
    OrderStatusEnum
from app.utils import admin_required, manager_required
from sqlalchemy import func
from datetime import datetime
import re
import os


def slugify(text):
    """Создание slug из текста"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


@admin.route('/')
@manager_required
def dashboard():
    """Главная страница админ-панели"""
    stats = {
        'users_count': User.query.count() if current_user.role == RoleEnum.ADMIN else None,
        'products_count': Product.query.count(),
        'orders_count': Order.query.count(),
        'orders_pending': Order.query.filter_by(status=OrderStatusEnum.PENDING).count(),
        'blog_posts_count': BlogPost.query.count(),
        'content_items': Content.query.count() if current_user.role == RoleEnum.ADMIN else None,
        'messages_unread': ContactMessage.query.filter_by(is_read=False).count()
    }

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)


# Управление пользователями
@admin.route('/users')
@admin_required
def users():
    """Список пользователей"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users_list = pagination.items

    return render_template('admin/users.html', users=users_list, pagination=pagination)


@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Редактирование пользователя"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form.get('username', '').strip()
        user.email = request.form.get('email', '').strip()
        user.full_name = request.form.get('full_name', '').strip() if request.form.get('full_name') else None
        user.phone = request.form.get('phone', '').strip() if request.form.get('phone') else None
        user.address = request.form.get('address', '').strip() if request.form.get('address') else None
        user.role = RoleEnum(request.form.get('role'))
        user.is_active = request.form.get('is_active') == 'on'

        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)

        try:
            db.session.commit()
            flash('Пользователь успешно обновлен', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении пользователя', 'error')

    return render_template('admin/edit_user.html', user=user)


@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Удаление пользователя"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Нельзя удалить самого себя', 'error')
        return redirect(url_for('admin.users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении пользователя', 'error')

    return redirect(url_for('admin.users'))


# Управление контентом (CMS)
@admin.route('/content')
@admin_required
def content_list():
    """Список контента"""
    # Получаем все элементы контента, отсортированные по секциям и ключам
    content_items = Content.query.order_by(Content.section, Content.key).all()

    # Группировка по секциям
    sections = {}
    for item in content_items:
        section = item.section or 'other'
        if section not in sections:
            sections[section] = []
        sections[section].append(item)

    return render_template('admin/content_list.html', sections=sections)


@admin.route('/content/new', methods=['GET', 'POST'])
@admin_required
def content_new():
    """Создание нового контента"""
    if request.method == 'POST':
        key = request.form.get('key')
        title = request.form.get('title')
        content_text = request.form.get('content')
        content_type = request.form.get('content_type', 'text')
        section = request.form.get('section', '')

        if Content.query.filter_by(key=key).first():
            flash('Контент с таким ключом уже существует', 'error')
            return render_template('admin/content_edit.html')

        content = Content(
            key=key,
            title=title,
            content=content_text,
            content_type=content_type,
            section=section,
            updated_by_id=current_user.id
        )

        try:
            db.session.add(content)
            db.session.commit()
            flash('Контент успешно создан', 'success')
            return redirect(url_for('admin.content_list'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при создании контента', 'error')

    return render_template('admin/content_edit.html')


@admin.route('/content/<int:content_id>/edit', methods=['GET', 'POST'])
@admin_required
def content_edit(content_id):
    """Редактирование контента"""
    content = Content.query.get_or_404(content_id)

    if request.method == 'POST':
        content.title = request.form.get('title')
        content.content = request.form.get('content')
        content.content_type = request.form.get('content_type', 'text')
        content.section = request.form.get('section', '')
        content.updated_by_id = current_user.id
        content.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            flash('Контент успешно обновлен', 'success')
            return redirect(url_for('admin.content_list'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении контента', 'error')

    return render_template('admin/content_edit.html', content=content)


@admin.route('/content/<int:content_id>/delete', methods=['POST'])
@admin_required
def content_delete(content_id):
    """Удаление контента"""
    content = Content.query.get_or_404(content_id)

    try:
        db.session.delete(content)
        db.session.commit()
        flash('Контент успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении контента', 'error')

    return redirect(url_for('admin.content_list'))


# Управление категориями
@admin.route('/categories')
@admin_required
def categories():
    """Список категорий"""
    categories_list = Category.query.all()
    return render_template('admin/categories.html', categories=categories_list)


@admin.route('/categories/new', methods=['GET', 'POST'])
@admin_required
def category_new():
    """Создание категории"""
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug') or slugify(name)
        description = request.form.get('description')

        if Category.query.filter_by(slug=slug).first():
            flash('Категория с таким slug уже существует', 'error')
            return render_template('admin/category_edit.html')

        category = Category(name=name, slug=slug, description=description)

        try:
            db.session.add(category)
            db.session.commit()
            flash('Категория успешно создана', 'success')
            return redirect(url_for('admin.categories'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при создании категории', 'error')

    return render_template('admin/category_edit.html')


@admin.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def category_edit(category_id):
    """Редактирование категории"""
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('slug') or slugify(category.name)
        category.description = request.form.get('description')

        try:
            db.session.commit()
            flash('Категория успешно обновлена', 'success')
            return redirect(url_for('admin.categories'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении категории', 'error')

    return render_template('admin/category_edit.html', category=category)


@admin.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def category_delete(category_id):
    """Удаление категории"""
    category = Category.query.get_or_404(category_id)

    if category.products.count() > 0:
        flash('Нельзя удалить категорию, в которой есть товары', 'error')
        return redirect(url_for('admin.categories'))

    try:
        db.session.delete(category)
        db.session.commit()
        flash('Категория успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении категории', 'error')

    return redirect(url_for('admin.categories'))


# Управление товарами
@admin.route('/products')
@manager_required
def products():
    """Список товаров"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    products_list = pagination.items

    return render_template('admin/products.html', products=products_list, pagination=pagination)


@admin.route('/products/new', methods=['GET', 'POST'])
@manager_required
def product_new():
    """Создание товара"""
    categories = Category.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug') or slugify(name)
        description = request.form.get('description')
        short_description = request.form.get('short_description')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity', 0)
        category_id = request.form.get('category_id')
        is_active = request.form.get('is_active') == 'on'

        # Обработка загрузки изображения
        image_file = None
        image_url = request.form.get('image_url', '').strip()
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                from app.utils import save_uploaded_file
                image_file = save_uploaded_file(file)
                image_url = None  # Очищаем URL, если загружен файл

        if Product.query.filter_by(slug=slug).first():
            flash('Товар с таким slug уже существует', 'error')
            return render_template('admin/product_edit.html', categories=categories)

        product = Product(
            name=name,
            slug=slug,
            description=description,
            short_description=short_description,
            price=price,
            stock_quantity=int(stock_quantity),
            category_id=category_id,
            image_url=image_url,
            is_active=is_active
        )
        # Устанавливаем image_file отдельно после создания объекта
        if image_file:
            product.image_file = image_file

        try:
            db.session.add(product)
            db.session.commit()
            flash('Товар успешно создан', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при создании товара', 'error')

    return render_template('admin/product_edit.html', categories=categories)


@admin.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@manager_required
def product_edit(product_id):
    """Редактирование товара"""
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.slug = request.form.get('slug') or slugify(product.name)
        product.description = request.form.get('description')
        product.short_description = request.form.get('short_description')
        product.price = request.form.get('price')
        product.stock_quantity = int(request.form.get('stock_quantity', 0))
        product.category_id = request.form.get('category_id')
        product.is_active = request.form.get('is_active') == 'on'

        # Обработка загрузки изображения
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                from app.utils import save_uploaded_file
                # Удаляем старый файл, если есть
                if hasattr(product, 'image_file') and product.image_file:
                    old_path = os.path.join(current_app.root_path, 'static', 'uploads', product.image_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                product.image_file = save_uploaded_file(file)
                product.image_url = None  # Очищаем URL, если загружен файл

        # Если указан URL и нет файла, используем URL
        image_url = request.form.get('image_url', '').strip()
        if image_url and not getattr(product, 'image_file', None):
            product.image_url = image_url

        try:
            db.session.commit()
            flash('Товар успешно обновлен', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении товара', 'error')

    return render_template('admin/product_edit.html', product=product, categories=categories)


@admin.route('/products/<int:product_id>/delete', methods=['POST'])
@manager_required
def product_delete(product_id):
    """Удаление товара"""
    product = Product.query.get_or_404(product_id)

    try:
        db.session.delete(product)
        db.session.commit()
        flash('Товар успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении товара', 'error')

    return redirect(url_for('admin.products'))


# Управление заказами
@admin.route('/orders')
@manager_required
def orders():
    """Список заказов"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status')

    query = Order.query
    if status_filter:
        query = query.filter_by(status=OrderStatusEnum(status_filter))

    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    orders_list = pagination.items

    return render_template('admin/orders.html', orders=orders_list, pagination=pagination, status_filter=status_filter)


@admin.route('/orders/<int:order_id>')
@manager_required
def order_detail(order_id):
    """Детали заказа"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin.route('/orders/<int:order_id>/update_status', methods=['POST'])
@manager_required
def order_update_status(order_id):
    """Обновление статуса заказа"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    try:
        order.status = OrderStatusEnum(new_status)
        db.session.commit()
        flash('Статус заказа обновлен', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при обновлении статуса', 'error')

    return redirect(url_for('admin.order_detail', order_id=order_id))


# Управление блогом
@admin.route('/blog')
@manager_required
def blog_posts():
    """Список статей блога"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=per_page,
                                                                              error_out=False)
    posts = pagination.items

    return render_template('admin/blog_posts.html', posts=posts, pagination=pagination)


@admin.route('/blog/new', methods=['GET', 'POST'])
@manager_required
def blog_post_new():
    """Создание статьи"""
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug') or slugify(title)
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        is_published = request.form.get('is_published') == 'on'

        # Обработка загрузки изображения
        image_file = None
        image_url = request.form.get('image_url', '').strip()
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                from app.utils import save_uploaded_file
                image_file = save_uploaded_file(file)
                image_url = None  # Очищаем URL, если загружен файл

        if BlogPost.query.filter_by(slug=slug).first():
            flash('Статья с таким slug уже существует', 'error')
            return render_template('admin/blog_post_edit.html')

        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            image_url=image_url,
            author_id=current_user.id,
            is_published=is_published
        )
        # Устанавливаем image_file отдельно после создания объекта
        if image_file:
            post.image_file = image_file

        if is_published:
            post.published_at = datetime.utcnow()

        try:
            db.session.add(post)
            db.session.commit()
            flash('Статья успешно создана', 'success')
            return redirect(url_for('admin.blog_posts'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при создании статьи', 'error')

    return render_template('admin/blog_post_edit.html')


@admin.route('/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@manager_required
def blog_post_edit(post_id):
    """Редактирование статьи"""
    post = BlogPost.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.slug = request.form.get('slug') or slugify(post.title)
        post.content = request.form.get('content')
        post.excerpt = request.form.get('excerpt')
        was_published = post.is_published
        post.is_published = request.form.get('is_published') == 'on'

        # Обработка загрузки изображения
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                from app.utils import save_uploaded_file
                # Удаляем старый файл, если есть
                if post.image_file:
                    old_path = os.path.join(current_app.root_path, 'static', 'uploads', post.image_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                post.image_file = save_uploaded_file(file)
                post.image_url = None  # Очищаем URL, если загружен файл

        # Если указан URL и нет файла, используем URL
        image_url = request.form.get('image_url', '').strip()
        if image_url and not post.image_file:
            post.image_url = image_url

        if post.is_published and not was_published:
            post.published_at = datetime.utcnow()

        try:
            db.session.commit()
            flash('Статья успешно обновлена', 'success')
            return redirect(url_for('admin.blog_posts'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении статьи', 'error')

    return render_template('admin/blog_post_edit.html', post=post)


@admin.route('/blog/<int:post_id>/delete', methods=['POST'])
@manager_required
def blog_post_delete(post_id):
    """Удаление статьи"""
    post = BlogPost.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Статья успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении статьи', 'error')

    return redirect(url_for('admin.blog_posts'))

