"""Модуль для инициализации начальных данных в базе данных"""
from app import db
from app.models import User, Category, Product, Content, BlogPost, RoleEnum
from datetime import datetime


def init_database_data():
    """Инициализация базы данных начальными данными, если она пустая"""

    # Проверяем, есть ли уже данные в базе
    if User.query.first() is not None:
        return False  # База уже содержит данные

    print("Инициализация базы данных...")

    # Создаем пользователей
    admin = User(
        username='admin',
        email='admin@leathercraft.ru',
        full_name='Администратор',
        role=RoleEnum.ADMIN
    )
    admin.set_password('admin123')
    db.session.add(admin)
    print('✓ Создан администратор: admin / admin123')

    manager = User(
        username='manager',
        email='manager@leathercraft.ru',
        full_name='Менеджер',
        role=RoleEnum.MANAGER
    )
    manager.set_password('manager123')
    db.session.add(manager)
    print('✓ Создан менеджер: manager / manager123')

    user = User(
        username='user',
        email='user@leathercraft.ru',
        full_name='Тестовый пользователь',
        role=RoleEnum.USER
    )
    user.set_password('user123')
    db.session.add(user)
    print('✓ Создан пользователь: user / user123')

    # Сохраняем пользователей, чтобы получить их ID
    db.session.flush()

    # Создаем категории
    categories_data = [
        {'name': 'Сумки', 'slug': 'bags', 'description': 'Деловые и городские сумки из натуральной кожи'},
        {'name': 'Кошельки', 'slug': 'wallets', 'description': 'Кошельки и картхолдеры премиум качества'},
        {'name': 'Ремни', 'slug': 'belts', 'description': 'Кожаные ремни для делового и повседневного стиля'},
        {'name': 'Аксессуары', 'slug': 'accessories', 'description': 'Кожаные аксессуары и подарки'}
    ]

    categories = {}
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)
        categories[cat_data['slug']] = category
        print(f'✓ Создана категория: {cat_data["name"]}')

    # Сохраняем категории, чтобы получить их ID
    db.session.flush()

    # Создаем товары
    products_data = [
        {
            'name': 'Деловая сумка Classic',
            'slug': 'business-bag-classic',
            'description': 'Премиум кожаная деловая сумка ручной работы. Идеально подходит для деловых встреч и повседневного использования. Вместительные отделения, удобные ручки, качественная фурнитура.',
            'short_description': 'Премиум кожа, ручная прошивка',
            'price': 15000.00,
            'stock_quantity': 15,
            'category_slug': 'bags',
            'image_url': 'https://placehold.co/600x400'
        },
        {
            'name': 'Кошелек Minimalist',
            'slug': 'wallet-minimalist',
            'description': 'Компактный кошелек из итальянской кожи. Ультратонкий дизайн, вмещает все необходимое. Отделения для карт, купюр и монет.',
            'short_description': 'Компактный дизайн, итальянская кожа',
            'price': 4500.00,
            'stock_quantity': 25,
            'category_slug': 'wallets',
            'image_url': 'https://placehold.co/600x400'
        },
        {
            'name': 'Ремень Executive',
            'slug': 'belt-executive',
            'description': 'Классический кожаный ремень для делового стиля. Цельнокроеная кожа, латунная пряжка. Доступен в нескольких размерах.',
            'short_description': 'Цельнокроеная кожа, латунная пряжка',
            'price': 3800.00,
            'stock_quantity': 30,
            'category_slug': 'belts',
            'image_url': 'https://placehold.co/600x400'
        },
        {
            'name': 'Рюкзак Urban',
            'slug': 'backpack-urban',
            'description': 'Городской рюкзак из натуральной кожи. Вместительный, стильный, удобный. Подходит для работы и путешествий.',
            'short_description': 'Городской стиль, вместительный',
            'price': 18500.00,
            'stock_quantity': 10,
            'category_slug': 'bags',
            'image_url': 'https://placehold.co/600x400'
        },
        {
            'name': 'Набор аксессуаров',
            'slug': 'accessories-set',
            'description': 'Набор из трех аксессуаров: ключница, визитница и обложка для документов. Премиум кожа, ручная работа.',
            'short_description': 'Ключница, визитница, обложка',
            'price': 6200.00,
            'stock_quantity': 20,
            'category_slug': 'accessories',
            'image_url': 'https://placehold.co/600x400'
        },
        {
            'name': 'Картхолдер Slim',
            'slug': 'cardholder-slim',
            'description': 'Ультратонкий картхолдер с RFID защитой. Вмещает до 6 карт. Минималистичный дизайн, максимальная функциональность.',
            'short_description': 'Ультратонкий, RFID защита',
            'price': 2900.00,
            'stock_quantity': 35,
            'category_slug': 'wallets',
            'image_url': 'https://placehold.co/600x400'
        }
    ]

    for prod_data in products_data:
        category_slug = prod_data.pop('category_slug')
        product = Product(
            category_id=categories[category_slug].id,
            **prod_data
        )
        db.session.add(product)
        print(f'✓ Создан товар: {prod_data["name"]}')

    # Создаем начальный контент для CMS
    content_data = [
        {'key': 'about_content', 'title': 'О компании',
         'content': 'С 1985 года мы создаем изделия из натуральной кожи, сочетая традиционные техники ручной работы с современными технологиями производства. Наша мастерская начиналась как небольшое семейное предприятие и выросла в признанного производителя премиум кожаных изделий, поставляющего продукцию в более чем 30 стран мира. Мы работаем с лучшими сортами натуральной кожи от проверенных поставщиков из Италии, Франции и Аргентины. Каждое изделие проходит строгий контроль качества на всех этапах производства.',
         'section': 'about', 'content_type': 'text'},
        {'key': 'stats_years', 'title': 'Статистика: годы', 'content': '38+', 'section': 'about', 'content_type': 'text'},
        {'key': 'stats_masters', 'title': 'Статистика: мастера', 'content': '45', 'section': 'about', 'content_type': 'text'},
        {'key': 'stats_countries', 'title': 'Статистика: страны', 'content': '30+', 'section': 'about', 'content_type': 'text'},
        {'key': 'contact_address', 'title': 'Адрес', 'content': 'г. Москва, ул. Кожевническая, д. 14, стр. 2', 'section': 'contact', 'content_type': 'text'},
        {'key': 'contact_phone', 'title': 'Телефон', 'content': '+7 (495) 123-45-67', 'section': 'contact', 'content_type': 'text'},
        {'key': 'contact_email', 'title': 'Email', 'content': 'info@leathercraft.ru', 'section': 'contact', 'content_type': 'text'},
        {'key': 'contact_hours', 'title': 'Режим работы', 'content': 'Пн-Пт: 9:00 - 18:00, Сб-Вс: выходной', 'section': 'contact', 'content_type': 'text'},
        {'key': 'social_instagram', 'title': 'Instagram', 'content': 'https://instagram.com/leathercraft', 'section': 'social', 'content_type': 'url'},
        {'key': 'social_facebook', 'title': 'Facebook', 'content': 'https://facebook.com/leathercraft', 'section': 'social', 'content_type': 'url'},
        {'key': 'social_telegram', 'title': 'Telegram', 'content': 'https://t.me/leathercraft', 'section': 'social', 'content_type': 'url'},
        {'key': 'about_image_1', 'title': 'Изображение 1 страницы about', 'content': 'https://placehold.co/600x400', 'section': 'about', 'content_type': 'image'},
        {'key': 'about_image_2', 'title': 'Изображение 2 страницы about', 'content': 'https://placehold.co/600x400', 'section': 'about', 'content_type': 'image'},
        {'key': 'about_image_3', 'title': 'Изображение 3 страницы about', 'content': 'https://placehold.co/600x400', 'section': 'about', 'content_type': 'image'},
        {'key': 'about_image_4', 'title': 'Изображение 4 страницы about', 'content': 'https://placehold.co/600x400', 'section': 'about', 'content_type': 'image'},
        {'key': 'usp_first', 'title': '100% натуральная кожа', 'content':'Работаем только с премиум материалами от проверенных поставщиков', 'section': 'usp', 'content_type': 'text'},
        {'key': 'usp_second', 'title': 'Ручная работа', 'content':'Каждое изделие создается опытными мастерами с вниманием к деталям', 'section': 'usp', 'content_type': 'text'},
        {'key': 'usp_third', 'title': 'Доставка по всему миру', 'content':'Оптовые поставки с гибкими условиями для B2B клиентов', 'section': 'usp', 'content_type': 'text'}
    ]

    for content_item in content_data:
        content = Content(**content_item)
        content.updated_by_id = admin.id
        db.session.add(content)
        print(f'✓ Создан контент: {content_item["key"]}')

    # Создаем статьи блога (используем ID пользователей после flush)
    blog_posts_data = [
        {
            'title': 'История создания LeatherCraft',
            'slug': 'history-of-leathercraft',
            'excerpt': 'Как небольшое семейное предприятие выросло в признанного производителя премиум кожаных изделий.',
            'content': 'В 1985 году наша история началась с небольшой мастерской, где работали всего несколько мастеров. Мы верили, что качество и внимание к деталям - это основа успеха. С годами наша репутация росла, и сегодня мы поставляем продукцию в более чем 30 стран мира. Каждое изделие создается с любовью и вниманием к деталям, сохраняя традиции ручной работы.',
            'image_url': 'https://placehold.co/600x400',
            'is_published': True,
            'author_id': admin.id
        },
        {
            'title': 'Как выбрать качественную кожу',
            'slug': 'how-to-choose-quality-leather',
            'excerpt': 'Руководство по выбору натуральной кожи для изделий премиум класса.',
            'content': 'Выбор качественной кожи - это основа долговечности изделия. Мы работаем только с проверенными поставщиками из Италии, Франции и Аргентины. Натуральная кожа имеет уникальную текстуру, приятный запах и со временем приобретает благородную патину. Обращайте внимание на равномерность окраски, отсутствие дефектов и качество обработки краев.',
            'image_url': 'https://placehold.co/600x400',
            'is_published': False,
            'author_id': manager.id
        },
        {
            'title': 'Уход за кожаными изделиями',
            'slug': 'leather-care-tips',
            'excerpt': 'Простые советы по уходу за кожаными изделиями, чтобы они служили долгие годы.',
            'content': 'Правильный уход за кожаными изделиями продлевает их срок службы и сохраняет внешний вид. Регулярно очищайте изделия мягкой тканью, используйте специальные средства для ухода за кожей. Избегайте попадания влаги и прямых солнечных лучей. Храните изделия в прохладном сухом месте, используя специальные чехлы или коробки.',
            'image_url': 'https://placehold.co/600x400',
            'is_published': True,
            'author_id': manager.id
        }
    ]

    for post_data in blog_posts_data:
        post = BlogPost(
            published_at=datetime.utcnow(),
            **post_data
        )
        db.session.add(post)
        print(f'✓ Создана статья блога: {post_data["title"]}')

    try:
        db.session.commit()
        print('\n✓ База данных успешно инициализирована!')
        return True
    except Exception as e:
        db.session.rollback()
        print(f'\n✗ Ошибка при инициализации базы данных: {e}')
        return False

