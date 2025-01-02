# Utiliser l'image de Python 3.13
FROM python:3.13.1-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source dans le conteneur
COPY . .

# Exposer le port 5001
EXPOSE 5001

# Commande pour lancer l'application
CMD ["python", "app.py"]
