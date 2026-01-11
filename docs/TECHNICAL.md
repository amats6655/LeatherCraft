# Техническая документация LeatherCraft

Техническое описание архитектуры, структуры проекта и процессов разработки интернет-магазина LeatherCraft.

## Содержание

1. [Архитектура приложения](#архитектура-приложения)
2. [Структура проекта](#структура-проекта)
3. [База данных](#база-данных)
4. [API и маршруты](#api-и-маршруты)
5. [Модели данных](#модели-данных)
6. [Безопасность](#безопасность)
7. [Логирование](#логирование)
8. [Развертывание](#развертывание)
9. [Разработка](#разработка)

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
│   ├── logging_config.py        # Конфигурация системы логирования
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
├── logs/                        # Логи приложения
│   ├── app.log                 # Общие логи
│   ├── requests.log            # Логи HTTP запросов
│   ├── actions.log             # Логи действий пользователей
│   ├── auth.log                # Логи аутентификации
│   └── errors.log              # Логи ошибок
│
├── config.py                    # Конфигурация приложения
├── run.py                       # Точка входа приложения
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

## Логирование

### Архитектура системы логирования

Система логирования реализована в модуле `app/logging_config.py` и обеспечивает production-ready логирование всех событий приложения.

**Основные компоненты:**

- **Модуль конфигурации:** `app/logging_config.py`
- **Поддержка форматов:** JSON для продакшена, текстовый для разработки
- **Ротация файлов:** автоматическая ротация при достижении лимита размера
- **Отдельные логгеры:** для разных типов событий
- **Маскирование данных:** автоматическое скрытие чувствительной информации

### Настройки логирования

Настройки логирования находятся в `config.py`:

- **LOG_LEVEL** - уровень логирования (DEBUG, INFO, WARNING, ERROR)
- **LOG_DIR** - директория для хранения логов (по умолчанию `logs/`)
- **LOG_MAX_BYTES** - максимальный размер файла лога перед ротацией (по умолчанию 10MB)
- **LOG_BACKUP_COUNT** - количество резервных файлов при ротации (по умолчанию 5)
- **LOG_FORMAT** - формат логов: `json`, `text`, или `auto` (auto = json для продакшена, text для разработки)

**Пример настройки через переменные окружения:**

```bash
export LOG_LEVEL=INFO
export LOG_DIR=logs
export LOG_MAX_BYTES=10485760  # 10MB
export LOG_BACKUP_COUNT=5
export LOG_FORMAT=json
```

### Типы логгеров

Система использует отдельные логгеры для разных типов событий:

1. **app.requests** - HTTP запросы
   - Логирует все HTTP запросы с методом, путем, IP адресом
   - Время выполнения запроса
   - Статус код ответа
   - Информация о пользователе (если авторизован)
   - Медленные запросы (>1 сек) логируются как WARNING

2. **app.actions** - Действия пользователей и администраторов
   - CRUD операции с товарами, категориями, пользователями
   - Операции с заказами (создание, изменение статуса)
   - Операции с корзиной
   - Редактирование контента и статей блога

3. **app.auth** - События аутентификации
   - Успешные входы и выходы
   - Регистрация новых пользователей
   - Неудачные попытки входа
   - Попытки входа в деактивированные аккаунты

4. **app.errors** - Ошибки приложения
   - Все ошибки уровня ERROR и выше
   - Полный стектрейс для исключений
   - Контекстная информация (IP, пользователь, путь)

### Форматы логов

#### JSON формат (продакшен)

Используется когда `LOG_FORMAT=json` или `LOG_FORMAT=auto` и приложение не в режиме debug.

**Пример записи:**

```json
{
  "timestamp": "2024-12-10T12:00:00Z",
  "level": "INFO",
  "logger": "app.actions",
  "action": "user_login",
  "user_id": 123,
  "username": "user@example.com",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "status": "success",
  "message": "User logged in successfully"
}
```

#### Текстовый формат (разработка)

Используется когда `LOG_FORMAT=text` или в режиме debug.

**Пример записи:**

```
2024-12-10 12:00:00 - app.actions - INFO - [IP: 192.168.1.1] - User: user@example.com (ID: 123) - Action: user_login - Status: success - User logged in successfully
```

### Структура файлов логов

Все логи сохраняются в директории `logs/`:

- **app.log** - общие логи приложения (уровень DEBUG и выше)
- **requests.log** - все HTTP запросы (уровень INFO)
- **actions.log** - действия пользователей и администраторов (уровень INFO)
- **auth.log** - события аутентификации (уровень INFO)
- **errors.log** - ошибки приложения (уровень ERROR и выше)

**Ротация файлов:**

- При достижении `LOG_MAX_BYTES` файл переименовывается в `.log.1`
- Старые файлы сдвигаются: `.log.1` → `.log.2`, `.log.2` → `.log.3`, и т.д.
- Хранится максимум `LOG_BACKUP_COUNT` резервных файлов
- Старые файлы автоматически удаляются

### Маскирование чувствительных данных

Система автоматически маскирует чувствительные данные в логах:

- Пароли (`password`, `password_hash`)
- Токены (`token`, `secret`, `api_key`, `authorization`)

Все значения этих полей заменяются на `***MASKED***` перед записью в лог.

### Логирование запросов

Все HTTP запросы логируются через middleware в `app/__init__.py`:

- **Исключения:** статические файлы (`/static/`) не логируются детально
- **Метрики:** время выполнения запроса в миллисекундах
- **Контекст:** IP адрес, User-Agent, метод, путь, статус код
- **Пользователь:** ID и username (если авторизован)

### Логирование действий

Действия пользователей и администраторов логируются через декораторы в `app/utils.py`:

- `@log_action` - универсальный декоратор
- `@log_admin_action` - для админских действий
- `@log_user_action` - для пользовательских действий

**Логируемые действия:**

- Аутентификация: вход, выход, регистрация
- Товары: создание, редактирование, удаление
- Категории: создание, редактирование, удаление
- Заказы: создание, изменение статуса
- Пользователи: редактирование, удаление
- Контент: создание, редактирование, удаление
- Блог: создание, редактирование, удаление статей
- Корзина: добавление, удаление товаров
- Профиль: обновление данных пользователя

---
