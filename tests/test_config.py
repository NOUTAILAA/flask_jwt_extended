import pytest
from app import app, db  # Assurez-vous que `app` et `db` sont importés depuis votre fichier principal

def test_config_loading():
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'mysql://root:123456@localhost/ocr_auth_db'
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert app.config['JWT_SECRET_KEY'] == 'super-secret-key'
    assert app.config['DEBUG'] is True


def test_database_connection():
    with app.app_context():
        try:
            # Vérifier la connexion à la base de données
            db.session.execute('SELECT 1')
            assert True
        except Exception as e:
            pytest.fail(f"Erreur de connexion à la base de données : {e}")


def test_jwt_secret_key():
    assert 'JWT_SECRET_KEY' in app.config
    assert app.config['JWT_SECRET_KEY'] == 'super-secret-key'


def test_debug_mode():
    assert app.config['DEBUG'] is True
