from app import create_app
from app.init_data import init_database_data

app = create_app()

@app.cli.command('init_db')
def init_db():
    """Принудительная инициализация базы данных с начальными данными"""
    with app.app_context():
        from app import db
        db.create_all()
        init_database_data()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)