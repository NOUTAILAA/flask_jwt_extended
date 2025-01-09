import os
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import string
import secrets
import re
from flask_cors import CORS
from utils import send_email  # Assurez-vous que cette fonction est définie correctement
from pytz import timezone

# Initialisation de Flask et CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration de la base de données et JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/ocr_auth_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'votre_secret_key'  # Remplacez par une clé secrète
app.secret_key = 'une_cle_secrete'  # Pour la gestion des sessions

# Initialisation de la base de données et JWT
db = SQLAlchemy(app)
jwt = JWTManager(app)


# Modèle de la table User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(64), nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiration = db.Column(db.DateTime, nullable=True)


# Validation de l'email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


# Route d'inscription
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not is_valid_email(email):
        return jsonify({"error": "Adresse email invalide!"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "L'email existe déjà!"}), 400

    if len(password) < 6:
        return jsonify({"error": "Mot de passe trop court!"}), 400

    password_hash = generate_password_hash(password)
    token = secrets.token_urlsafe(24)
    token_expiration = datetime.utcnow() + timedelta(hours=1)

    new_user = User(email=email, password_hash=password_hash, verification_token=token, token_expiration=token_expiration)
    db.session.add(new_user)
    db.session.commit()

    verification_url = f"http://127.0.0.1:5001/verify_email/{token}"
    send_email(email, "Vérification de compte", f"Cliquez sur ce lien pour vérifier votre compte : {verification_url}")

    return jsonify({"message": "Utilisateur enregistré. Veuillez vérifier votre email."}), 201


# Route de vérification d'email
@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user and datetime.utcnow() < user.token_expiration:
        user.is_verified = True
        user.verification_token = None  # Effacer le token après vérification
        db.session.commit()
        return jsonify({"message": "Votre compte a été vérifié avec succès!"})

    return jsonify({"error": "Token invalide ou expiré!"}), 400



@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        if not user.is_verified:
            return jsonify({"error": "Votre compte n'est pas vérifié!"}), 400

        # Générer et envoyer l'OTP
        otp = ''.join(random.choices(string.digits, k=6))

        # Utiliser un fuseau horaire correct
        local_tz = timezone('Europe/Paris')  # Adapter au fuseau local
        now = datetime.now(local_tz)
        otp_expiration = now + timedelta(minutes=1)

        user.otp_code = otp
        user.otp_expiration = otp_expiration

        db.session.commit()

        # Contenu stylisé de l'email
        email_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #333;">Bonjour,</h2>
            <p>Votre code OTP est :</p>
            <p style="font-size: 24px; color: #007BFF; font-weight: bold; text-align: center;">{otp}</p>
            <p>Ce code est valable pour une durée de 5 minute.</p>
            <p style="margin-top: 20px;">Merci de l'utiliser pour compléter votre connexion.</p>
            <br>
            <p style="font-size: 14px; color: #555;">Cordialement,<br>L'équipe Support</p>
        </body>
        </html>
        """

        # Envoi de l'email stylisé
        send_email(email, "Votre code OTP", email_content, is_html=True)

        session['email'] = email
        return jsonify({"message": "OTP envoyé à votre email."})

    return jsonify({"error": "Identifiants incorrects!"}), 401



# Vérification de l'OTP
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    local_tz = timezone('Europe/Paris') 
    now = datetime.now(local_tz)

    user = User.query.filter_by(email=email).first()
    if user and user.otp_code == otp:
        # Convertir otp_expiration en offset-aware datetime
        otp_expiration_local = user.otp_expiration.replace(tzinfo=timezone('UTC')).astimezone(local_tz)

        if now < otp_expiration_local:
            access_token = create_access_token(identity=email)
            user.otp_code = None
            user.otp_expiration = None
            db.session.commit()
            return jsonify({"access_token": access_token})

    return jsonify({"error": "OTP invalide ou expiré!"}), 400



# Route protégée
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)


def generate_random_password(length=8):
    """Génère un mot de passe aléatoire."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    # Vérifier si l'utilisateur existe
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Aucun utilisateur trouvé avec cet email!"}), 404

    # Générer un nouveau mot de passe
    new_password = generate_random_password()
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    # Envoyer un email avec le nouveau mot de passe
    subject = "Réinitialisation de votre mot de passe"
    message = f"Bonjour,\n\nVotre mot de passe a été réinitialisé avec succès. Voici votre nouveau mot de passe :\n\n{new_password}\n\nVeuillez vous connecter et changer ce mot de passe si nécessaire.\n\nCordialement,\nVotre équipe."
    send_email(email, subject, message)

    return jsonify({"message": "Un email avec le nouveau mot de passe a été envoyé."}), 200

# Créer toutes les tables dans la base de données MySQL
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
