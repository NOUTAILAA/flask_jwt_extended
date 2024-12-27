import pytest
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User
import uuid


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        # Nettoyage après chaque test
        with app.app_context():
            db.session.remove()
            db.drop_all()


def test_register(client):
    unique_email = f'test_{uuid.uuid4()}@example.com'
    response = client.post('/register', json={
        'email': unique_email,
        'password': 'password123'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'Utilisateur enregistré' in data['message']

    

def test_protected_route_without_token(client):
    response = client.get('/protected')
    assert response.status_code == 401  # Non autorisé
    assert b"Missing Authorization Header" in response.data
def test_protected_route_with_invalid_token(client):
    headers = {'Authorization': 'Bearer invalidtoken123'}
    response = client.get('/protected', headers=headers)
    assert response.status_code == 422  # Token non valide

def test_register_existing_email(client):
    email = 'duplicate@example.com'
    password = 'password123'
    
    # Premier enregistrement
    client.post('/register', json={'email': email, 'password': password})
    
    # Tentative d'enregistrement avec le même email
    response = client.post('/register', json={'email': email, 'password': password})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "L'email existe déjà" in data['error']

def test_login_unverified_user(client):
    unique_email = f'test_{uuid.uuid4()}@example.com'
    client.post('/register', json={
        'email': unique_email,
        'password': 'password123'
    })
    response = client.post('/login', json={
        'email': unique_email,
        'password': 'password123'
    })
    assert response.status_code == 400
    
    # Utilisation de get_json pour récupérer la réponse JSON sans encodage
    data = response.get_json()
    
    assert "Votre compte n'est pas vérifié!" in data['error']

def test_login_success_after_verification(client):
    unique_email = f'test_{uuid.uuid4()}@example.com'
    client.post('/register', json={
        'email': unique_email,
        'password': 'password123'
    })

    # Vérification de l'email
    user = User.query.filter_by(email=unique_email).first()
    user.is_verified = True
    db.session.commit()

    response = client.post('/login', json={
        'email': unique_email,
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b"access_token" in response.data

def test_verify_email_success(client):
    unique_email = f'test_{uuid.uuid4()}@example.com'
    register_response = client.post('/register', json={
        'email': unique_email,
        'password': 'password123'
    })
    assert register_response.status_code == 201

    # Simuler la récupération du token
    user = User.query.filter_by(email=unique_email).first()
    token = user.verification_token

    verify_response = client.get(f'/verify_email/{token}')
    assert verify_response.status_code == 200

    # Décoder la réponse JSON
    data = verify_response.get_json()
    assert "Votre compte a été vérifié avec succès!" in data['message']

PASSS='123'
def test_register_short_password(client):
    unique_email = f'test_{uuid.uuid4()}@example.com'
    response = client.post('/register', json={
        'email': unique_email,
        'password': PASSS # Mot de passe court pour tester la validation (ceci est intentionnel)
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert "Mot de passe trop court" in data['error']
