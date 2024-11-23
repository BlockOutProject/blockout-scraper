# Utiliser une image Python minimale basée sur Alpine
FROM python:3.12-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Définir la commande par défaut pour exécuter le scraper
CMD ["python", "main.py"]