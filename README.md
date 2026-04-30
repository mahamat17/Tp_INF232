# 🍽️ FoodStat Cameroon

[![Deploy on Render](https://img.shields.io/badge/Deploy%20on-Render-46E3B7?logo=render)](https://render.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green?logo=flask)](https://flask.palletsprojects.com)

## 📊 Application d'analyse statistique de l'alimentation au Cameroun

**FoodStat Cameroon** est une application web complète de collecte et d'analyse de données sur les habitudes alimentaires quotidiennes des Camerounais. Elle fournit des outils statistiques avancés pour comprendre les comportements alimentaires à travers le pays.

---

## ✨ Fonctionnalités

### 📝 Collecte de données
- Enregistrement des informations personnelles (nom, prénom, âge, sexe)
- Données géographiques (région, ville, milieu de vie)
- Habitudes alimentaires (aliments consommés, nombre de repas)
- Budget alimentaire journalier
- Niveau de satisfaction alimentaire

### 📊 Analyses statistiques complètes

| Statistique | Description |
|-------------|-------------|
| **Moyenne** | Valeur moyenne d'une série de données |
| **Variance** | Mesure de dispersion des données |
| **Écart-type** | Racine carrée de la variance |
| **Covariance** | Mesure de la relation entre deux variables |
| **Corrélation (r)** | Coefficient de corrélation linéaire de Pearson |
| **Détermination (R²)** | Proportion de variance expliquée |
| **Quartiles** | Q1, Médiane (Q2), Q3 |
| **Régression linéaire** | Droite de régression y = ax + b |

### 📈 Visualisations
- 📊 **Histogramme** des âges
- 🥧 **Diagrammes circulaires** (régions, sexes, aliments préférés)
- 🟢 **Nuage de points** interactif avec droite de régression
- 📋 **Matrice de corrélation** entre variables

### 📋 Gestion des données
- Consultation de toutes les données collectées
- Recherche et filtrage
- Suppression d'enregistrements
- Export CSV

---

## 🗺️ Régions couvertes

- Adamaoua
- Centre
- Est
- Extrême-Nord
- Littoral
- Nord
- Nord-Ouest
- Ouest
- Sud
- Sud-Ouest

---

## 🍛 Aliments typiques étudiés

| Catégorie | Exemples |
|-----------|----------|
| **Plats typiques** | Ndolé, Eru, OKOK, Poulet DG, Koki, Sanga, Mbongo |
| **Féculents** | Plantain, Manioc, Taro, Ignames, Fufu |
| **Protéines** | Poisson braisé, Poulet, Bœuf, Gibier, Escargot |
| **Légumes** | Feuilles de manioc, Gombo, Eru, Okok |

---

## 🛠️ Technologies utilisées

- **Backend** : Python 3.9+ / Flask
- **Frontend** : HTML5, CSS3, JavaScript
- **Visualisation** : Chart.js
- **Serveur** : Gunicorn
- **Déploiement** : Render.com

---

## 📁 Structure du projet

---

## 🚀 Installation et déploiement

### Prérequis

- Python 3.9 ou supérieur
- Compte GitHub
- Compte Render.com (gratuit)

### Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/FoodStat_Cameroon.git
cd FoodStat_Cameroon

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
