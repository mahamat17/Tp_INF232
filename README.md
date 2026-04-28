# 🩺 SantéData

> **Application de collecte et d'analyse descriptive des données épidémiologiques**  
> INF232 · TP EC2 · Développée avec Python / Flask

---

## 📋 Description

**SantéData** est une plateforme web de surveillance épidémiologique permettant de :

- **Collecter** des dossiers patients via un formulaire guidé en 4 étapes
- **Stocker** les données de manière persistante (JSON)
- **Visualiser** toutes les données dans un tableau filtrable
- **Analyser** les données avec des statistiques descriptives complètes
- **Afficher** des droites de régression linéaire (MCO) sur nuages de points interactifs
- **Exporter** les données au format CSV

---

## 🗂️ Structure du projet

```
santedata/
├── app.py                  # Application Flask principale
├── requirements.txt        # Dépendances Python
├── Procfile                # Commande de démarrage pour Render
├── render.yaml             # Configuration Render
├── .gitignore
├── patients.json           # Base de données (auto-créé au premier lancement)
├── static/
│   └── css/
│       └── style.css       # Feuille de styles CSS complète
└── templates/
    ├── base.html           # Layout commun (header, nav, tooltip)
    ├── index.html          # Tableau de bord
    ├── collecte.html       # Formulaire multi-étapes (4 étapes)
    ├── donnees.html        # Tableau des données + filtres + export CSV
    └── analyse.html        # Analyse descriptive + graphiques + régression
```

---

## ⚙️ Installation locale

### Prérequis
- Python 3.10 ou supérieur
- pip

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/santedata.git
cd santedata

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
# macOS / Linux :
source venv/bin/activate
# Windows :
venv\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python app.py
```

### Ouvrir dans le navigateur

```
http://127.0.0.1:5000
```

Arrêt du serveur : **CTRL + C**

---

## 🚀 Déploiement sur Render

### Méthode 1 — Déploiement automatique via `render.yaml`

1. Créer un compte sur [render.com](https://render.com)
2. Cliquer **New → Blueprint**
3. Connecter votre dépôt GitHub
4. Render détecte `render.yaml` et configure tout automatiquement
5. Cliquer **Apply** → votre application est en ligne en quelques minutes

### Méthode 2 — Déploiement manuel

1. Créer un compte sur [render.com](https://render.com)
2. **New → Web Service**
3. Connecter le dépôt GitHub
4. Renseigner :

| Champ | Valeur |
|---|---|
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

5. Ajouter une variable d'environnement :
   - `SECRET_KEY` → cliquer **Generate** pour une valeur sécurisée
6. Cliquer **Create Web Service**

> ⚠️ **Note sur la persistance** : Render utilise un système de fichiers éphémère. Le fichier `patients.json` sera réinitialisé à chaque redéploiement. Pour une production réelle, il faudrait migrer vers une base de données (PostgreSQL, SQLite sur volume persistant).

---

## 📊 Fonctionnalités

### Collecte (4 étapes guidées)
| Étape | Données collectées |
|---|---|
| 1 · Identité | Nom, prénom, date de naissance, sexe, admission, localité |
| 2 · Clinique | Pathologie, statut, tension, glycémie, température, sévérité, symptômes |
| 3 · Social | Éducation, eau potable, milieu de vie, couverture vaccinale, notes |
| 4 · Validation | Récapitulatif complet avant enregistrement |

### Analyse descriptive
- Moyenne, médiane, écart-type, min, max, étendue
- Histogramme des tranches d'âge
- Graphiques donut (sévérité, sexe)
- Barres de fréquence (pathologies, statut, milieu)
- **Droite de régression MCO** sur 4 paires de variables :
  - Âge → Tension systolique
  - Âge → Glycémie
  - Âge → Température
  - Tension systolique → Tension diastolique
- Équation `ŷ = bx + a` et coefficient de détermination **R²**

### Routes de l'API

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Tableau de bord |
| GET/POST | `/collecte` | Formulaire multi-étapes |
| GET | `/donnees` | Liste filtrée des patients |
| POST | `/donnees/supprimer/<id>` | Suppression d'un dossier |
| GET | `/donnees/export` | Export CSV UTF-8 |
| GET | `/analyse` | Analyse descriptive + régression |
| GET | `/api/scatter?x=age&y=sys` | API JSON pour nuage de points |

---

## 🛠️ Technologies utilisées

| Technologie | Usage |
|---|---|
| **Python 3** | Langage principal |
| **Flask** | Framework web |
| **Jinja2** | Moteur de templates HTML |
| **CSS3** | Styles (variables CSS, grid, animations) |
| **SVG** | Graphiques (donuts, scatter, histogrammes) |
| **JSON** | Stockage des données |
| **Gunicorn** | Serveur WSGI de production |

---

## 📐 Méthode statistique

La régression linéaire est calculée par la méthode des **Moindres Carrés Ordinaires (MCO)** :

```
b = Σ[(xᵢ - x̄)(yᵢ - ȳ)] / Σ[(xᵢ - x̄)²]
a = ȳ - b·x̄
R² = 1 - SS_res / SS_tot
```

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre du **TP EC2 — INF232**

---

*SantéData · INF232 · TP EC2*
