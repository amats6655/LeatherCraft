# Техническая документация LeatherCraft

Техническое описание архитектуры, структуры проекта и процессов разработки интернет-магазина LeatherCraft.

## Содержание

1. [Архитектура приложения](#архитектура-приложения)
2. [Структура проекта](#структура-проекта)
3. [База данных](#база-данных)
4. [API и маршруты](#api-и-маршруты)
5. [Модели данных](#модели-данных)
6. [Безопасность](#безопасность)
7. [Развертывание](#развертывание)
8. [Разработка](#разработка)

---

## Архитектура приложения

### Технологический стек

- **Backend:**
  - Python 3.8+
  - Flask 3.1.2
  - SQLAlchemy (ORM)
  - Flask-Login (аутентификация)
  - Flask-Bcrypt (хеширование паролей)

- **Frontend:**
  - HTML5, CSS3
  - Tailwind CSS (стилизация)
  - Alpine.js (интерактивность)
  - Swiper.js (слайдшоу)
  - Font Awesome (иконки)

- **База данных:**
  - SQLite (разработка)
  - Поддержка PostgreSQL/MySQL (продакшн)

### Паттерны проектирования

- **MVC (Model-View-Controller):**
  - Models: `app/models.py`
  - Views: `app/templates/`
  - Controllers: `app/routes.py`, `app/admin/routes.py`, etc.

- **Blueprint Pattern:**
  - Разделение функциональности по модулям
  - `app/admin/` - административная панель
  - `app/user/` - функционал пользователя
  - `app/auth.py` - аутентификация

- **Decorator Pattern:**
  - Декораторы для контроля доступа
  - `@admin_required`, `@manager_required`, `@login_required`

---

## Структура проекта

```
LeatherCraft/
├── app/
│   ├── __init__.py              # Инициализация Flask приложения
│   ├── models.py                # SQLAlchemy модели
│   ├── routes.py                # Публичные маршруты
│   ├── auth.py                  # Аутентификация и регистрация
│   ├── utils.py                 # Утилиты и декораторы
│   ├── init_data.py             # Инициализация начальных данных
│   │
│   ├── admin/                   # Административная панель
│   │   ├── __init__.py
│   │   ├── routes.py            # Основные маршруты админки
│   │   ├── messages_routes.py  # Управление обращениями и Hero слайдами
│   │   ├── about_routes.py      # Управление страницей About
│   │   └── contact_routes.py    # Управление страницей Contact
│   │
│   ├── user/                    # Функционал пользователя
│   │   ├── __init__.py
│   │   └── routes.py            # Корзина, заказы, профиль
│   │
│   ├── static/                  # Статические файлы
│   │   ├── css/
│   │   │   ├── main.css         # Основные стили
│   │   │   └── admin.css        # Стили админ-панели
│   │   ├── js/
│   │   │   └── style-switcher.js # Переключатель стилей
│   │   └── uploads/             # Загруженные изображения
│   │
│   └── templates/               # Jinja2 шаблоны
│       ├── base.html            # Базовый шаблон
│       ├── index.html           # Главная страница
│       ├── catalog.html         # Каталог товаров
│       ├── product_detail.html # Страница товара
│       ├── blog.html            # Список статей
│       ├── blog_post.html       # Страница статьи
│       ├── about.html           # О компании
│       ├── contact.html         # Контакты
│       ├── sitemap.html         # Карта сайта
│       ├── 403.html             # Страница ошибки 403
│       ├── 404.html             # Страница ошибки 404
│       ├── 500.html             # Страница ошибки 500
│       ├── auth/                # Шаблоны аутентификации
│       ├── admin/               # Шаблоны админ-панели
│       └── user/                # Шаблоны пользователя
│
├── instance/                    # Экземпляр приложения
│   └── leathercraft.db          # База данных SQLite
│
├── config.py                    # Конфигурация приложения
├── run.py                       # Точка входа приложения
├── migrate_db.py                # Скрипт миграции БД
├── requirements.txt             # Зависимости Python
├── README.md                    # Основная документация
└── docs/                        # Дополнительная документация
    ├── ADMIN_GUIDE.md
    ├── MANAGER_GUIDE.md
    ├── USER_GUIDE.md
    ├── FEATURES.md
    └── TECHNICAL.md
```

---

## База данных

### Схема базы данных

#### Таблица `users`
- `id` (INTEGER, PRIMARY KEY)
- `username` (VARCHAR(80), UNIQUE, NOT NULL)
- `email` (VARCHAR(120), UNIQUE, NOT NULL)
- `password_hash` (VARCHAR(128), NOT NULL)
- `full_name` (VARCHAR(200))
- `phone` (VARCHAR(20))
- `address` (TEXT)
- `role` (ENUM: admin, manager, user, NOT NULL)
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### Таблица `categories`
- `id` (INTEGER, PRIMARY KEY)
- `name` (VARCHAR(100), NOT NULL)
- `slug` (VARCHAR(100), UNIQUE, NOT NULL)
- `description` (TEXT)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### Таблица `products`
- `id` (INTEGER, PRIMARY KEY)
- `name` (VARCHAR(200), NOT NULL)
- `slug` (VARCHAR(200), UNIQUE, NOT NULL)
- `description` (TEXT)
- `short_description` (TEXT)
- `price` (DECIMAL(10, 2), NOT NULL)
- `stock_quantity` (INTEGER, DEFAULT 0)
- `category_id` (INTEGER, FOREIGN KEY -> categories.id)
- `image_url` (VARCHAR(500))
- `image_file` (VARCHAR(500))
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### Таблица `orders`
- `id` (INTEGER, PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY -> users.id)
- `total_amount` (DECIMAL(10, 2), NOT NULL)
- `status` (ENUM: pending, processing, shipped, delivered, cancelled)
- `shipping_address` (TEXT, NOT NULL)
- `phone` (VARCHAR(20))
- `comment` (TEXT)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### Таблица `order_items`
- `id` (INTEGER, PRIMARY KEY)
- `order_id` (INTEGER, FOREIGN KEY -> orders.id)
- `product_id` (INTEGER, FOREIGN KEY -> products.id)
- `quantity` (INTEGER, NOT NULL)
- `price` (DECIMAL(10, 2), NOT NULL)

#### Таблица `blog_posts`
- `id` (INTEGER, PRIMARY KEY)
- `title` (VARCHAR(200), NOT NULL)
- `slug` (VARCHAR(200), UNIQUE, NOT NULL)
- `excerpt` (TEXT)
- `content` (TEXT, NOT NULL)
- `author_id` (INTEGER, FOREIGN KEY -> users.id)
- `image_url` (VARCHAR(500))
- `image_file` (VARCHAR(500))
- `is_published` (BOOLEAN, DEFAULT FALSE)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### Таблица `content`
- `id` (INTEGER, PRIMARY KEY)
- `key` (VARCHAR(100), UNIQUE, NOT NULL)
- `title` (VARCHAR(200))
- `content` (TEXT)
- `section` (VARCHAR(50))
- `content_type` (VARCHAR(20))
- `updated_by_id` (INTEGER, FOREIGN KEY -> users.id)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### Таблица `hero_slides`
- `id` (INTEGER, PRIMARY KEY)
- `title` (VARCHAR(200), NOT NULL)
- `subtitle` (TEXT)
- `image_url` (VARCHAR(500))
- `image_file` (VARCHAR(500))
- `order` (INTEGER, DEFAULT 0)
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `link_url` (VARCHAR(500))
- `link_text` (VARCHAR(100))
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### Таблица `contact_messages`
- `id` (INTEGER, PRIMARY KEY)
- `name` (VARCHAR(200), NOT NULL)
- `email` (VARCHAR(200), NOT NULL)
- `phone` (VARCHAR(20))
- `subject` (VARCHAR(200))
- `message` (TEXT, NOT NULL)
- `is_read` (BOOLEAN, DEFAULT FALSE)
- `created_at` (DATETIME)

### Связи между таблицами

- `users` -> `orders` (один ко многим)
- `users` -> `blog_posts` (один ко многим)
- `categories` -> `products` (один ко многим)
- `orders` -> `order_items` (один ко многим)
- `products` -> `order_items` (один ко многим)

---

## API и маршруты

### Публичные маршруты (`app/routes.py`)

- `GET /` - Главная страница
- `GET /catalog` - Каталог товаров
- `GET /product/<slug>` - Страница товара
- `GET /about` - О компании
- `GET /contact` - Контакты
- `POST /contact` - Отправка формы обратной связи
- `GET /blog` - Список статей блога
- `GET /blog/<slug>` - Страница статьи
- `GET /sitemap` - Карта сайта

### Аутентификация (`app/auth.py`)

- `GET /auth/login` - Страница входа
- `POST /auth/login` - Обработка входа
- `GET /auth/logout` - Выход из системы
- `GET /auth/register` - Страница регистрации
- `POST /auth/register` - Обработка регистрации

### Пользователь (`app/user/routes.py`)

- `GET /user/profile` - Профиль пользователя
- `POST /user/profile` - Обновление профиля
- `GET /user/cart` - Корзина
- `POST /user/cart/add` - Добавление в корзину
- `POST /user/cart/update` - Обновление корзины
- `POST /user/cart/remove` - Удаление из корзины
- `GET /user/checkout` - Оформление заказа
- `POST /user/checkout` - Создание заказа
- `GET /user/orders` - Список заказов
- `GET /user/orders/<id>` - Детали заказа

### Администратор (`app/admin/routes.py`)

- `GET /admin/` - Дашборд
- `GET /admin/users` - Список пользователей
- `GET /admin/users/<id>/edit` - Редактирование пользователя
- `GET /admin/content` - Список контента
- `GET /admin/content/<id>/edit` - Редактирование контента
- `GET /admin/about` - Редактирование страницы About
- `GET /admin/contact` - Редактирование страницы Contact
- `GET /admin/categories` - Список категорий
- `GET /admin/categories/new` - Создание категории
- `GET /admin/categories/<id>/edit` - Редактирование категории
- `GET /admin/products` - Список товаров
- `GET /admin/products/new` - Создание товара
- `GET /admin/products/<id>/edit` - Редактирование товара
- `GET /admin/orders` - Список заказов
- `GET /admin/orders/<id>` - Детали заказа
- `GET /admin/blog` - Список статей
- `GET /admin/blog/new` - Создание статьи
- `GET /admin/blog/<id>/edit` - Редактирование статьи
- `GET /admin/messages` - Список обращений
- `GET /admin/messages/<id>` - Детали обращения
- `GET /admin/hero-slides` - Список слайдов Hero
- `GET /admin/hero-slides/new` - Создание слайда
- `GET /admin/hero-slides/<id>/edit` - Редактирование слайда

---

## Модели данных

### User

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.USER)
    # ... другие поля
    
    def set_password(self, password)
    def check_password(self, password)
    def is_admin(self)
    def is_manager(self)
```

### Product

```python
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_url = db.Column(db.String(500))
    image_file = db.Column(db.String(500))
    # ... другие поля
    
    def get_image(self)
```

### Order

```python
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING)
    # ... другие поля
```

---

## Безопасность

### Хеширование паролей

- Использование Flask-Bcrypt
- Алгоритм: bcrypt
- Автоматическая генерация соли

### Сессии

- Использование Flask-Login
- Безопасные сессии через Flask
- Защита от перехвата сессий

### Контроль доступа

- Ролевая модель (RBAC)
- Декораторы для проверки прав
- Обработка ошибок доступа (403)

### Валидация данных

- Проверка входных данных
- Санитизация файловых имен
- Валидация типов файлов

---

## Развертывание

### Требования

- Python 3.8+
- pip
- Виртуальное окружение (рекомендуется)

### Установка

1. Клонирование репозитория
2. Создание виртуального окружения
3. Установка зависимостей: `pip install -r requirements.txt`
4. Инициализация БД: `python run.py init-db`
5. Запуск: `python run.py`

### Конфигурация

- `SECRET_KEY` - секретный ключ для сессий
- `DATABASE_URL` - URL базы данных
- `UPLOAD_FOLDER` - папка для загрузок

### Продакшн

- Использование PostgreSQL вместо SQLite
- Настройка WSGI сервера (Gunicorn, uWSGI)
- Настройка веб-сервера (Nginx)
- Настройка SSL/TLS
- Резервное копирование БД

---