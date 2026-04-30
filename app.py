"""
FoodStat Cameroon - Application statistique complète
Analyse des données alimentaires avec :
- Variance, covariance
- Coefficient de corrélation linéaire
- Coefficient de détermination (R²)
- Droite de régression
- Histogramme, diagramme circulaire (camembert)
- Toutes les grandeurs statistiques
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json, os, math, random
from datetime import datetime, date
from collections import Counter

app = Flask(__name__)
app.secret_key = "foodstat_cameroon_secret"

DATA_FILE = os.path.join(os.path.dirname(__file__), "food_data.json")

# Liste des aliments camerounais
ALIMENTS_CAMEROUNAIS = [
    "Ndolé", "Eru", "OKOK", "Poulet DG", "Koki", "Fufu", "Taro sauce",
    "Plantain frites", "Poisson braisé", "Sanga", "Kwem", "Manioc(bâton)",
    "Miondo", "Saka saka", "Mbongo", "Nnam Mbongo", "Bâton de manioc"
]

REGIONS = [
    "Adamaoua", "Centre", "Est", "Extrême-Nord", "Littoral",
    "Nord", "Nord-Ouest", "Ouest", "Sud", "Sud-Ouest"
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== FONCTIONS STATISTIQUES ====================

def moyenne(valeurs):
    """Calcule la moyenne d'une liste"""
    if not valeurs:
        return 0
    return sum(valeurs) / len(valeurs)

def variance(valeurs):
    """Calcule la variance (population)"""
    if len(valeurs) < 2:
        return 0
    m = moyenne(valeurs)
    return sum((x - m) ** 2 for x in valeurs) / len(valeurs)

def covariance(xs, ys):
    """Calcule la covariance entre deux séries"""
    if len(xs) < 2 or len(ys) < 2:
        return 0
    if len(xs) != len(ys):
        return 0
    mx = moyenne(xs)
    my = moyenne(ys)
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs))) / len(xs)

def ecart_type(valeurs):
    """Calcule l'écart-type"""
    return math.sqrt(variance(valeurs))

def coefficient_correlation(xs, ys):
    """Coefficient de corrélation linéaire de Pearson (r)"""
    if len(xs) < 2 or len(ys) < 2:
        return 0
    cov = covariance(xs, ys)
    sigma_x = ecart_type(xs)
    sigma_y = ecart_type(ys)
    if sigma_x == 0 or sigma_y == 0:
        return 0
    return cov / (sigma_x * sigma_y)

def coefficient_determination(xs, ys):
    """Coefficient de détermination R²"""
    r = coefficient_correlation(xs, ys)
    return r ** 2

def regression_lineaire(xs, ys):
    """Calcule la droite de régression y = ax + b"""
    if len(xs) < 2:
        return {"a": 0, "b": 0, "equation": "y = 0"}
    
    mx = moyenne(xs)
    my = moyenne(ys)
    
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs)))
    den = sum((x - mx) ** 2 for x in xs)
    
    if den == 0:
        return {"a": 0, "b": my, "equation": f"y = {my:.2f}"}
    
    a = num / den  # pente
    b = my - a * mx  # ordonnée à l'origine
    
    signe = "+" if b >= 0 else "-"
    equation = f"y = {a:.4f}x {signe} {abs(b):.4f}"
    
    return {"a": round(a, 4), "b": round(b, 4), "equation": equation}

def calculer_statistiques_completes(data):
    """Calcule toutes les grandeurs statistiques"""
    if not data:
        return {}
    
    # Extraire les variables numériques
    ages = [d["age"] for d in data]
    repas_par_jour = [d.get("nb_repas", 3) for d in data]
    budget = [d.get("budget", 5000) for d in data]
    satisfaction = [d.get("satisfaction", 5) for d in data]
    
    # Variables catégorielles
    regions = [d.get("region", "") for d in data]
    sexes = [d.get("sexe", "") for d in data]
    aliments_principaux = [d.get("aliment_principal", "") for d in data]
    
    # Statistiques univariées (Âge)
    stat_age = {
        "moyenne": round(moyenne(ages), 2),
        "variance": round(variance(ages), 2),
        "ecart_type": round(ecart_type(ages), 2),
        "min": min(ages) if ages else 0,
        "max": max(ages) if ages else 0,
        "effectif": len(ages),
        "somme": sum(ages),
        "quartiles": calculer_quartiles(ages)
    }
    
    # Statistiques univariées (Budget)
    stat_budget = {
        "moyenne": round(moyenne(budget), 2),
        "variance": round(variance(budget), 2),
        "ecart_type": round(ecart_type(budget), 2),
        "min": min(budget) if budget else 0,
        "max": max(budget) if budget else 0,
        "effectif": len(budget),
        "somme": sum(budget)
    }
    
    # Statistiques bivariées
    # Corrélation Âge vs Budget
    corr_age_budget = coefficient_correlation(ages, budget)
    
    # Corrélation Âge vs Nombre de repas
    corr_age_repas = coefficient_correlation(ages, repas_par_jour)
    
    # Corrélation Budget vs Satisfaction
    corr_budget_satisfaction = coefficient_correlation(budget, satisfaction)
    
    # Droites de régression
    reg_age_budget = regression_lineaire(ages, budget)
    reg_age_repas = regression_lineaire(ages, repas_par_jour)
    
    # Diagramme circulaire (camembert) - Répartition par région
    region_counts = Counter([r for r in regions if r])
    camembert_regions = [{"label": k, "value": v} for k, v in region_counts.items()]
    
    # Diagramme circulaire - Répartition par sexe
    sexe_counts = Counter([s for s in sexes if s])
    camembert_sexes = [{"label": k, "value": v} for k, v in sexe_counts.items()]
    
    # Diagramme circulaire - Aliments préférés
    aliment_counts = Counter([a for a in aliments_principaux if a])
    camembert_aliments = [{"label": k[:20], "value": v} for k, v in aliment_counts.most_common(6)]
    
    # Histogramme des âges (tranches)
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 100]
    labels = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "80+"]
    histo_ages = [sum(1 for a in ages if bins[i] < a <= bins[i+1]) for i in range(len(bins)-1)]
    histogramme_ages = [{"label": labels[i], "count": histo_ages[i]} for i in range(len(labels))]
    
    return {
        "effectif_total": len(data),
        "statistiques_age": stat_age,
        "statistiques_budget": stat_budget,
        "correlations": {
            "age_vs_budget": {
                "r": round(corr_age_budget, 4),
                "r2": round(corr_age_budget ** 2, 4),
                "covariance": round(covariance(ages, budget), 2),
                "interpretation": interpretation_correlation(corr_age_budget),
                "regression": reg_age_budget
            },
            "age_vs_nb_repas": {
                "r": round(corr_age_repas, 4),
                "r2": round(corr_age_repas ** 2, 4),
                "covariance": round(covariance(ages, repas_par_jour), 2),
                "interpretation": interpretation_correlation(corr_age_repas),
                "regression": reg_age_repas
            },
            "budget_vs_satisfaction": {
                "r": round(corr_budget_satisfaction, 4),
                "r2": round(corr_budget_satisfaction ** 2, 4),
                "covariance": round(covariance(budget, satisfaction), 2),
                "interpretation": interpretation_correlation(corr_budget_satisfaction),
                "regression": regression_lineaire(budget, satisfaction)
            }
        },
        "diagrammes": {
            "camembert_regions": camembert_regions,
            "camembert_sexes": camembert_sexes,
            "camembert_aliments": camembert_aliments,
            "histogramme_ages": histogramme_ages
        },
        "matrice_correlation": calculer_matrice_correlation(ages, budget, repas_par_jour, satisfaction)
    }

def calculer_quartiles(valeurs):
    """Calcule les quartiles Q1, Q2 (médiane), Q3"""
    if not valeurs:
        return {"Q1": 0, "Q2": 0, "Q3": 0}
    sorted_vals = sorted(valeurs)
    n = len(sorted_vals)
    q2 = sorted_vals[n // 2]
    q1 = sorted_vals[n // 4] if n >= 4 else q2
    q3 = sorted_vals[3 * n // 4] if n >= 4 else q2
    return {"Q1": q1, "Q2": q2, "Q3": q3}

def interpretation_correlation(r):
    """Interprète le coefficient de corrélation"""
    abs_r = abs(r)
    if abs_r >= 0.8:
        return "Très forte corrélation"
    elif abs_r >= 0.6:
        return "Forte corrélation"
    elif abs_r >= 0.4:
        return "Corrélation modérée"
    elif abs_r >= 0.2:
        return "Faible corrélation"
    else:
        return "Corrélation très faible ou nulle"

def calculer_matrice_correlation(ages, budget, repas, satisfaction):
    """Calcule la matrice de corrélation"""
    variables = [
        ("Âge", ages),
        ("Budget", budget),
        ("Nb repas/jour", repas),
        ("Satisfaction", satisfaction)
    ]
    matrice = []
    for i, (nom1, vals1) in enumerate(variables):
        ligne = []
        for j, (nom2, vals2) in enumerate(variables):
            if i == j:
                ligne.append(1.0)
            else:
                corr = coefficient_correlation(vals1, vals2)
                ligne.append(round(corr, 4))
        matrice.append(ligne)
    return {"labels": [v[0] for v in variables], "matrice": matrice}

# ==================== ROUTES ====================

@app.route("/")
def index():
    data = load_data()
    stats = calculer_statistiques_completes(data)
    recent = list(reversed(data))[:5]
    return render_template("index.html", stats=stats, recent=recent, total=len(data))

@app.route("/collecte", methods=["GET", "POST"])
def collecte():
    if request.method == "POST":
        data = load_data()
        
        nouveau = {
            "id": f"F{len(data)+1:04d}",
            "date": str(date.today()),
            "nom": request.form.get("nom", "").strip().upper(),
            "prenom": request.form.get("prenom", "").strip().title(),
            "age": int(request.form.get("age", 0)),
            "sexe": request.form.get("sexe"),
            "region": request.form.get("region"),
            "ville": request.form.get("ville", ""),
            "profession": request.form.get("profession", ""),
            "aliment_principal": request.form.get("aliment_principal"),
            "aliments_secondaires": request.form.get("aliments_secondaires", ""),
            "nb_repas": int(request.form.get("nb_repas", 3)),
            "budget": int(request.form.get("budget", 5000)),
            "satisfaction": int(request.form.get("satisfaction", 3)),
            "commentaire": request.form.get("commentaire", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data.append(nouveau)
        save_data(data)
        flash(f"✅ Donnée enregistrée - ID: {nouveau['id']}", "success")
        return redirect(url_for("index"))
    
    return render_template("collecte.html", regions=REGIONS, aliments=ALIMENTS_CAMEROUNAIS)

@app.route("/donnees")
def donnees():
    data = load_data()
    return render_template("donnees.html", data=data, total=len(data))

@app.route("/donnees/supprimer/<did>", methods=["POST"])
def supprimer(did):
    data = load_data()
    data = [d for d in data if d["id"] != did]
    save_data(data)
    flash(f"🗑️ Donnée {did} supprimée", "warning")
    return redirect(url_for("donnees"))

@app.route("/analyse")
def analyse():
    data = load_data()
    stats = calculer_statistiques_completes(data)
    return render_template("analyse.html", stats=stats, total=len(data))

@app.route("/api/scatter")
def api_scatter():
    data = load_data()
    x_key = request.args.get("x", "age")
    y_key = request.args.get("y", "budget")
    
    x_map = {"age": "age", "budget": "budget", "nb_repas": "nb_repas", "satisfaction": "satisfaction"}
    y_map = {"age": "age", "budget": "budget", "nb_repas": "nb_repas", "satisfaction": "satisfaction"}
    
    x_vals = [d.get(x_map.get(x_key, "age"), 0) for d in data]
    y_vals = [d.get(y_map.get(y_key, "budget"), 0) for d in data]
    
    points = [{"x": x_vals[i], "y": y_vals[i], "name": f"{d['prenom']} {d['nom']}"} 
              for i, d in enumerate(data)]
    
    regression = regression_lineaire(x_vals, y_vals)
    correlation = coefficient_correlation(x_vals, y_vals)
    
    return jsonify({
        "points": points,
        "regression": regression,
        "correlation": round(correlation, 4),
        "r2": round(correlation ** 2, 4)
    })

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year, "regions": REGIONS}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
