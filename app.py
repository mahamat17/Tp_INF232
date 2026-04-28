"""
╔══════════════════════════════════════════════════════════════╗
║  SantéData — app.py                                          ║
║  Application Flask de collecte & analyse épidémiologique     ║
║  INF232 · TP EC2 · Déployable sur Render.com                 ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, send_file
)
import json, os, csv, io, math
from datetime import datetime, date

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "santedata_inf232_secret_2024")

DATA_FILE = os.path.join(os.path.dirname(__file__), "patients.json")


# ─────────────────────────────────────────────
# PERSISTANCE JSON
# ─────────────────────────────────────────────
def load_patients() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_patients(patients: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(patients, f, ensure_ascii=False, indent=2)


def generate_id(patients: list) -> str:
    return f"SD-{len(patients) + 1:04d}"


def calc_age(ddn_str: str) -> int:
    try:
        ddn   = datetime.strptime(ddn_str, "%Y-%m-%d").date()
        today = date.today()
        return today.year - ddn.year - (
            (today.month, today.day) < (ddn.month, ddn.day)
        )
    except Exception:
        return 0


# ─────────────────────────────────────────────
# STATISTIQUES DESCRIPTIVES
# ─────────────────────────────────────────────
def mean(values: list) -> float:
    return sum(values) / len(values) if values else 0.0

def variance(values: list) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)

def std_dev(values: list) -> float:
    return math.sqrt(variance(values))

def median(values: list) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n, mid = len(s), len(s) // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2

def frequency(values: list) -> dict:
    total  = len(values)
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return {
        k: {"abs": c, "rel": round(c / total * 100, 1)}
        for k, c in sorted(counts.items(), key=lambda x: -x[1])
    }

def linear_regression(xs: list, ys: list):
    n = len(xs)
    if n < 2:
        return None
    mx, my = mean(xs), mean(ys)
    num    = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den    = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    b      = num / den
    a      = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((ys[i] - (a + b * xs[i])) ** 2 for i in range(n))
    r2     = 1 - ss_res / ss_tot if ss_tot != 0 else 1.0
    sign   = "+" if a >= 0 else "-"
    return {
        "a":        round(a, 4),
        "b":        round(b, 4),
        "r2":       round(r2, 4),
        "equation": f"ŷ = {b:.4f}x {sign} {abs(a):.4f}",
    }

def age_histogram(ages: list) -> list:
    bins   = [0, 10, 20, 30, 40, 50, 60, 70, 80, 200]
    labels = [f"{bins[i]}–{bins[i+1]-1}" for i in range(len(bins) - 1)]
    counts = [sum(1 for a in ages if bins[i] <= a < bins[i+1])
              for i in range(len(bins) - 1)]
    return [{"label": labels[i], "count": counts[i]}
            for i in range(len(labels))]

def descriptive_stats(patients: list) -> dict:
    if not patients:
        return {}

    ages  = [p["age"]  for p in patients]
    sys_v = [p["sys"]  for p in patients]
    dia_v = [p["dia"]  for p in patients]
    temp  = [p["temp"] for p in patients]
    glyc  = [p["glyc"] for p in patients]

    def block(vals, label):
        return {
            "label":  label,
            "n":      len(vals),
            "mean":   round(mean(vals), 2),
            "median": round(median(vals), 2),
            "std":    round(std_dev(vals), 2),
            "min":    round(min(vals), 2),
            "max":    round(max(vals), 2),
            "range":  round(max(vals) - min(vals), 2),
        }

    regressions = {}
    if len(patients) >= 2:
        reg_pairs = [
            ("age_sys",  ages,  sys_v, "Âge (ans)", "Tension sys. (mmHg)", "age", "sys",  "#0ea5e9"),
            ("age_glyc", ages,  glyc,  "Âge (ans)", "Glycémie (g/L)",      "age", "glyc", "#00e5a0"),
            ("age_temp", ages,  temp,  "Âge (ans)", "Température (°C)",    "age", "temp", "#f59e0b"),
            ("sys_dia",  sys_v, dia_v, "Tension sys. (mmHg)", "Tension dia. (mmHg)", "sys", "dia", "#ef4444"),
        ]
        for key, xs, ys, xl, yl, xk, yk, col in reg_pairs:
            reg = linear_regression(xs, ys)
            if reg:
                regressions[key] = {**reg, "xlabel": xl, "ylabel": yl,
                                    "xkey": xk, "ykey": yk, "color": col}

    return {
        "stats":       [block(ages, "Âge (ans)"),
                        block(sys_v, "Tension sys. (mmHg)"),
                        block(dia_v, "Tension dia. (mmHg)"),
                        block(glyc,  "Glycémie (g/L)"),
                        block(temp,  "Température (°C)")],
        "pathologies": frequency([p["pathologie"] for p in patients]),
        "severite":    frequency([p["severite"]   for p in patients]),
        "sexe":        frequency([p["sexe"]       for p in patients]),
        "statut":      frequency([p["statut"]     for p in patients]),
        "milieu":      frequency([p.get("milieu", "Non précisé") for p in patients]),
        "education":   frequency([p.get("education", "Non précisé") for p in patients]),
        "regressions": regressions,
        "age_bins":    age_histogram(ages),
        "total":       len(patients),
        "crit":        sum(1 for p in patients if p["severite"] == "Critique"),
        "age_mean":    round(mean(ages), 1),
        "diseases":    len(set(p["pathologie"] for p in patients)),
    }


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    patients = load_patients()
    recent   = list(reversed(patients))[:6]
    stats = {
        "total":    len(patients),
        "age_mean": round(mean([p["age"] for p in patients]), 1) if patients else "—",
        "crit":     sum(1 for p in patients if p["severite"] == "Critique"),
        "diseases": len(set(p["pathologie"] for p in patients)),
    }
    return render_template("index.html", recent=recent, stats=stats)


@app.route("/collecte", methods=["GET", "POST"])
def collecte():
    if request.method == "POST":
        patients = load_patients()
        step     = request.form.get("step", "1")

        if step == "save":
            symptomes = request.form.getlist("symptomes")
            ddn       = request.form.get("ddn", "")
            patient   = {
                "id":         generate_id(patients),
                "date":       request.form.get("admission", str(date.today())),
                "prenom":     request.form.get("prenom", "").strip().title(),
                "nom":        request.form.get("nom",    "").strip().upper(),
                "ddn":        ddn,
                "age":        calc_age(ddn),
                "sexe":       request.form.get("sexe", ""),
                "adresse":    request.form.get("adresse", "").strip(),
                "pathologie": request.form.get("pathologie", ""),
                "statut":     request.form.get("statut", ""),
                "severite":   request.form.get("severite", ""),
                "sys":        int(request.form.get("sys", 120)),
                "dia":        int(request.form.get("dia", 80)),
                "temp":       float(request.form.get("temp", 37.0)),
                "glyc":       float(request.form.get("glyc", 1.0)),
                "symptomes":  symptomes,
                "education":  request.form.get("education", ""),
                "eau":        request.form.get("eau", ""),
                "milieu":     request.form.get("milieu", ""),
                "vaccin":     request.form.get("vaccin", ""),
                "notes":      request.form.get("notes", "").strip(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            patients.append(patient)
            save_patients(patients)
            flash(f"✅ Dossier {patient['id']} enregistré avec succès !", "success")
            return redirect(url_for("index"))

        form_data = dict(request.form)
        return render_template("collecte.html",
                               step=int(step),
                               form_data=form_data,
                               today=str(date.today()))

    return render_template("collecte.html",
                           step=1,
                           form_data={},
                           today=str(date.today()))


@app.route("/donnees")
def donnees():
    patients = load_patients()
    q        = request.args.get("q", "").lower()
    sex      = request.args.get("sexe", "")
    sev      = request.args.get("severite", "")

    filtered = [p for p in patients if (
        (q in p["nom"].lower() or q in p["prenom"].lower()
         or q in p["pathologie"].lower()
         or q in p.get("adresse", "").lower())
        and (not sex or p["sexe"] == sex)
        and (not sev or p["severite"] == sev)
    )]
    return render_template("donnees.html",
                           patients=filtered,
                           total=len(patients),
                           q=q, sexe=sex, severite=sev)


@app.route("/donnees/supprimer/<pid>", methods=["POST"])
def supprimer(pid):
    patients = load_patients()
    patients = [p for p in patients if p["id"] != pid]
    save_patients(patients)
    flash(f"🗑️ Dossier {pid} supprimé.", "warning")
    return redirect(url_for("donnees"))


@app.route("/donnees/export")
def export_csv():
    patients = load_patients()
    output   = io.StringIO()
    fields   = ["id","date","nom","prenom","age","sexe","adresse",
                 "pathologie","statut","severite","sys","dia","temp",
                 "glyc","milieu","education","vaccin","notes","created_at"]
    writer   = csv.DictWriter(output, fieldnames=fields,
                               extrasaction="ignore", delimiter=";")
    writer.writeheader()
    for p in patients:
        writer.writerow(p)

    bom_csv = "\ufeff" + output.getvalue()
    buf = io.BytesIO(bom_csv.encode("utf-8"))
    buf.seek(0)
    return send_file(buf,
                     mimetype="text/csv; charset=utf-8",
                     as_attachment=True,
                     download_name=f"santedata_{date.today()}.csv")


@app.route("/analyse")
def analyse():
    patients = load_patients()
    stats    = descriptive_stats(patients)
    return render_template("analyse.html", stats=stats, patients=patients)


@app.route("/api/scatter")
def api_scatter():
    xkey     = request.args.get("x", "age")
    ykey     = request.args.get("y", "sys")
    patients = load_patients()
    xs  = [p.get(xkey, 0) for p in patients]
    ys  = [p.get(ykey, 0) for p in patients]
    reg = linear_regression(xs, ys) if len(patients) >= 2 else None
    pts = [{"x": xs[i], "y": ys[i],
             "name": f"{patients[i]['prenom']} {patients[i]['nom']}"}
            for i in range(len(patients))]
    return jsonify({"points": pts, "regression": reg})


# ─────────────────────────────────────────────
# FILTRES JINJA2
# ─────────────────────────────────────────────
@app.template_filter("severity_class")
def severity_class(s):
    return {"Légère": "green", "Modérée": "amber",
            "Sévère": "amber", "Critique": "red"}.get(s, "blue")

@app.template_filter("status_class")
def status_class(s):
    return {"Guéri": "green", "En traitement": "blue",
            "Hospitalisé": "amber", "Décédé": "red",
            "Transféré": "blue"}.get(s, "blue")

@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    print("=" * 55)
    print("  🩺  SantéData — Application Épidémiologique")
    print(f"  📡  Serveur : http://0.0.0.0:{port}")
    print("  🛑  Arrêt   : CTRL + C")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port, debug=debug)
