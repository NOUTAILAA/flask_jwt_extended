import smtplib
from email.message import EmailMessage
PASSS='brgq esjz adnv tppb'
def send_email(to, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "ilgazzkaya599@gmail.com"  # Ton adresse email
    msg['To'] = to
    
    # Utilise le mot de passe d'application ici
    smtp_password = PASSS 

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()  # Démarrer la connexion sécurisée
        smtp.login("ilgazzkaya599@gmail.com", smtp_password)  # Utiliser l'email et le mot de passe d'application
        smtp.send_message(msg)
