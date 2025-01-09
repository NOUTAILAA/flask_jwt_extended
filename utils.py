import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ton mot de passe d'application Gmail
PASSS = 'brgq esjz adnv tppb'

def send_email(to, subject, body, is_html=False):
    # Création du message multipart
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = "ilgazzkaya599@gmail.com"  # Ton adresse email
    msg['To'] = to

    # Ajout du contenu (texte brut ou HTML)
    if is_html:
        part = MIMEText(body, "html")
    else:
        part = MIMEText(body, "plain")

    msg.attach(part)

    # Utilisation du mot de passe d'application Gmail
    smtp_password = PASSS 

    try:
        # Configuration et envoi de l'email via le serveur SMTP de Gmail
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()  # Démarrer la connexion sécurisée
            smtp.login("ilgazzkaya599@gmail.com", smtp_password)  # Connexion avec email et mot de passe
            smtp.send_message(msg)
        print("Email envoyé avec succès!")
    except Exception as e:
        raise Exception(f"Erreur lors de l'envoi de l'email : {str(e)}")
