"""
Конфигурационный файл для Gunicorn.
Используйте: gunicorn -c gunicorn_config.py run:app
"""
import multiprocessing
import os

# Базовые настройки
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Логирование Gunicorn
# Важно: Gunicorn будет логировать в эти файлы, но наше приложение логирует в logs/
accesslog = "-"  # Логи доступа в stdout/stderr (можно указать файл, например "logs/gunicorn_access.log")
errorlog = "-"   # Логи ошибок в stdout/stderr (можно указать файл, например "logs/gunicorn_error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Безопасность
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Производительность
max_requests = 1000  # Перезапуск воркера после N запросов (предотвращение утечек памяти)
max_requests_jitter = 50
preload_app = True  # Загружаем приложение до форка воркеров (экономия памяти)

# Имя приложения
proc_name = "leathercraft"

# PID файл (опционально)
# pidfile = "/var/run/gunicorn.pid"

# Пользователь и группа (для продакшена, раскомментируйте и настройте)
# user = "www-data"
# group = "www-data"

# Умолчания для переменных окружения
# Убедитесь, что эти переменные установлены в вашем окружении
# или установите их здесь:
# os.environ.setdefault('FLASK_ENV', 'production')
# os.environ.setdefault('LOG_FORMAT', 'json')
