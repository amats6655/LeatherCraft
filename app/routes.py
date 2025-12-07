from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from app.models import Product, Category, BlogPost, Content, HeroSlide
from app import db
from sqlalchemy import or_, func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """ Главная страница """
    # Получаем слайды Hero
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.order, HeroSlide.id).all()

    # Получаем блок УТП - уникальное торговое предложение
    usp_first = Content.query.filter_by(key='usp_first').first()
    usp_second = Content.query.filter_by(key='usp_second').first()
    usp_third = Content.query.filter_by(key='usp_third').first()

    # Получаем популярные товары
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.views_count.desc()).limit(6).all()

    # Получаем последние статьи в блоге
    recent_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).limit(3).all()

    return render_template('index.html',
                           hero_slides=hero_slides,
                           usp_first=usp_first,
                           usp_second=usp_second,
                           usp_third=usp_third,
                           featured_products=featured_products,
                           recent_posts=recent_posts)

@main.route('/catalog')
def catalog():
    """Каталог товаров"""
    category_slug = request.args.get('category')
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Product.query.filter_by(is_active=True)

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter(category_id=category.id)

    if search_query:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%'),
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    categories = Category.query.all()

    return render_template('catalog.html',
                           products=products,
                           categories=categories,
                           current_category=category,
                           search_query=search_query)


@main.route('/product/<slug>')
def product_detail(slug):
    """Страница товара"""
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Увеличиваем счетчик просмотров
    product.views_count += 1
    db.session.commit()

    # 4 случайных товара из той же категории
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).order_by(func.random()).limit(4).all()

    return render_template('product_detail.html',
                           product=product,
                           related_products=related_products)


@main.route('/blog')
def blog():
    """Список статей блога"""
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Не более 9 статей на странице

    pagination = BlogPost.query.filter_by(is_published=True) \
        .order_by(BlogPost.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    posts = pagination.items

    return render_template('blog.html', posts=posts, pagination=pagination)


@main.route('/blog/<slug>')
def blog_post(slug):
    """Страница статьи блога"""
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()

    # Увеличиваем счетчик просмотров
    post.views_count += 1
    db.session.commit()

    # Получаем 3 случайные опубликованные статьи (исключая текущую)
    related_posts = BlogPost.query.filter(
        BlogPost.id != post.id,
        BlogPost.is_published == True
    ).order_by(func.random()).limit(3).all()

    return render_template('blog_post.html', post=post, related_posts=related_posts)


@main.route('/about')
def about():
    """О компании"""
    about_content = Content.query.filter_by(key='about_content').first()
    stats = {
        'years': Content.query.filter_by(key='stats_years').first(),
        'masters': Content.query.filter_by(key='stats_masters').first(),
        'countries': Content.query.filter_by(key='stats_countries').first()
    }

    return render_template('about.html', about_content=about_content, stats=stats)


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Контакты"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        # Валидация
        if not all([name, email, message]):
            flash('Пожалуйста, заполните все обязательные поля', 'error')
            contact_info = {
                'address': Content.query.filter_by(key='contact_address').first(),
                'phone': Content.query.filter_by(key='contact_phone').first(),
                'email': Content.query.filter_by(key='contact_email').first(),
                'hours': Content.query.filter_by(key='contact_hours').first()
            }
            return render_template('contact.html', contact_info=contact_info)

        # Сохранение обращения в БД
        from app.models import ContactMessage
        contact_message = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        try:
            db.session.add(contact_message)
            db.session.commit()
            flash('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.', 'success')
            return redirect(url_for('main.contact'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при отправке сообщения. Попробуйте позже.', 'error')

    contact_info = {
        'address': Content.query.filter_by(key='contact_address').first(),
        'phone': Content.query.filter_by(key='contact_phone').first(),
        'email': Content.query.filter_by(key='contact_email').first(),
        'hours': Content.query.filter_by(key='contact_hours').first()
    }

    return render_template('contact.html', contact_info=contact_info)

@main.route('/sitemap')
def sitemap():
    """Карта сайта"""
    categories = Category.query.all()
    products = Product.query.filter_by(is_active=True).all()
    posts = BlogPost.query.filter_by(is_published=True).all()

    return render_template('sitemap.html',
                           categories=categories,
                           products=products,
                           posts=posts)


@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@main.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
