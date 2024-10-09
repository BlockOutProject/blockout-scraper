# Projet de Scraper de Données de Volleyball

## Description

Ce projet est un **scraper** conçu pour extraire des informations sur les championnats nationaux, régionaux et professionnels de volleyball en France. Il collecte les données des pools, des équipes et des matchs depuis le site de la Fédération Française de Volley-Ball et les stocke dans une base de données pour une analyse ultérieure.

## Fonctionnalités

- **Scraping des pools nationaux, régionaux et professionnels**
- **Téléchargement et parsing des fichiers CSV des matchs**
- **Stockage des données dans une base de données SQLite via SQLAlchemy**
- **Gestion asynchrone des tâches pour une meilleure performance**
- **Système de logging paramétrable pour le suivi et le débogage**

## Prérequis

- **Python 3.7** ou supérieur
- **virtualenv** ou **venv** pour créer un environnement virtuel (recommandé)

## Installation

1. **Cloner le dépôt**

   ```bash
   git clone https://github.com/votre-utilisateur/votre-projet.git
   cd votre-projet
   ```

2. **Créer un environnement virtuel**

   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**

   - Sur **macOS/Linux**:

     ```bash
     source venv/bin/activate
     ```

   - Sur **Windows**:

     ```bash
     venv\Scripts\activate
     ```

4. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Fichier de Configuration du Logging

Le système de logging est configuré via le fichier `logging.yaml`. Vous pouvez ajuster les niveaux de logging, les formatters et les handlers selon vos besoins.

- **Niveaux de logging**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Handlers**: Console, Fichier (avec rotation automatique)

Pour modifier le niveau de logging, éditez le fichier `logging.yaml` et changez la valeur du niveau dans la section appropriée.

Exemple pour ajuster le niveau de logging à `INFO`:

```yaml
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    ...
```

### Arguments en Ligne de Commande (Optionnel)

Vous pouvez spécifier le niveau de logging lors de l'exécution du script en utilisant l'argument `--log-level`. *(Note: Cette fonctionnalité doit être implémentée si elle ne l'est pas déjà.)*

Exemple:

```bash
python main.py --log-level DEBUG
```

## Utilisation

Pour exécuter le scraper, assurez-vous que vous êtes dans l'environnement virtuel et lancez le script principal:

```bash
python main.py
```

Le script lancera le scraping des pools nationaux, régionaux et professionnels en parallèle, téléchargera les fichiers CSV correspondants, parsera les données et les stockera dans la base de données.

## Structure du Projet

- `main.py`: Script principal qui lance les tâches de scraping.
- `scrapers/`: Contient les modules de scraping pour chaque niveau de championnat.
  - `national_scraper.py`
  - `regional_scraper.py`
  - `pro_scraper.py`
- `services/`: Contient les services pour interagir avec la base de données.
  - `pools_service.py`
  - `teams_service.py`
  - `matchs_service.py`
- `utils.py`: Fonctions utilitaires communes.
- `downloader.py`: Gère le téléchargement des fichiers CSV.
- `errors_handler.py`: Gestionnaire d'erreurs avec un décorateur pour logger les exceptions.
- `logger_config.py`: Configuration du système de logging.
- `logging.yaml`: Fichier de configuration YAML pour le logging.
- `db.py`: Modèles de données SQLAlchemy pour la base de données.
- `session_manager.py`: Gestionnaire de sessions de base de données.
- `requirements.txt`: Liste des dépendances Python du projet.

## Base de Données

Le projet utilise **SQLAlchemy** pour interagir avec une base de données SQLite. La base de données est stockée dans un fichier `database.db`. Les modèles de données sont définis dans `db.py`.

## Logging

Les logs sont gérés via le module `logging` de Python, configuré dans `logger_config.py` et `logging.yaml`. Les messages de log sont écrits à la fois dans la console et dans un fichier `logs/app.log`. Les logs incluent des informations telles que l'horodatage, le niveau de sévérité, le nom du module et le message, ce qui facilite le suivi et le débogage.

### Emplacement des Logs

- **Console**: Les messages de log sont affichés en temps réel dans la console.
- **Fichier**: Les logs sont enregistrés dans le fichier `logs/app.log`. Une rotation automatique des fichiers est mise en place pour éviter que les logs ne deviennent trop volumineux.

### Modifier le Niveau de Logging

Pour modifier le niveau de logging sans changer le code source, vous pouvez:

1. **Modifier le fichier de configuration `logging.yaml`**:

   - Changez les niveaux de logging dans les sections `handlers` ou `loggers`.

2. **Utiliser une variable d'environnement**:

   - Vous pouvez spécifier un fichier de configuration alternatif en définissant la variable d'environnement `LOG_CFG`.

     ```bash
     export LOG_CFG=path/to/votre_logging.yaml
     ```

3. **Utiliser des arguments en ligne de commande** *(si implémenté)*:

   - Spécifiez le niveau de logging lors de l'exécution du script.

     ```bash
     python main.py --log-level DEBUG
     ```

## Dépendances

Les principales bibliothèques utilisées dans ce projet sont:

- **aiohttp**: Pour les requêtes HTTP asynchrones.
- **asyncio**: Pour la gestion des tâches asynchrones.
- **BeautifulSoup**: Pour le parsing du contenu HTML.
- **SQLAlchemy**: Pour l'interaction avec la base de données.
- **PyYAML**: Pour le chargement de la configuration du logging.

Toutes les dépendances sont listées dans le fichier `requirements.txt`.

## Arborescence des Répertoires

```
votre-projet/
├── scrapers/
│   ├── national_scraper.py
│   ├── regional_scraper.py
│   └── pro_scraper.py
├── services/
│   ├── pools_service.py
│   ├── teams_service.py
│   └── matchs_service.py
├── utils.py
├── downloader.py
├── errors_handler.py
├── logger_config.py
├── logging.yaml
├── db.py
├── session_manager.py
├── main.py
├── requirements.txt
└── README.md
```

## Exécution des Tests *(à implémenter)*

Des tests unitaires peuvent être ajoutés pour vérifier le bon fonctionnement du code. Il est recommandé d'utiliser **pytest** ou **unittest** pour écrire et exécuter les tests.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez contribuer:

1. **Fork** le dépôt.
2. **Créez** une branche pour votre fonctionnalité ou correction (`git checkout -b feature/ma-fonctionnalite`).
3. **Commitez** vos modifications (`git commit -m 'Ajouter ma fonctionnalité'`).
4. **Poussez** vers la branche (`git push origin feature/ma-fonctionnalite`).
5. **Ouvrez** une Pull Request.

## Licence

Ce projet est sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

## Remerciements

Merci à toutes les personnes qui ont contribué à ce projet.

---

**Note**: Assurez-vous de mettre à jour les sections avec les informations spécifiques à votre projet, telles que l'URL du dépôt GitHub, les instructions d'installation précises, et toute autre information pertinente.

Si vous souhaitez ajouter ou modifier des sections, ou si vous avez besoin d'informations supplémentaires sur un aspect particulier, n'hésitez pas à me le faire savoir.