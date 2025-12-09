###########################
# IMPORTATION DES MODULES #
###########################
import os 
import sys

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from datetime import datetime, timedelta
from pathlib import Path
import geopandas as gpd
import json
#from rutabaga.rooms.users import User #gestion utilisateur et connexion
#from rutabaga.rooms.salles import Salle #gestion utilisateur et connexion
import pytz  # gestion des fuseaux horaire
import secrets  # système de clé secrètes

# fixing path ? 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rooms.users import User
from rooms.salles import Salle

###########################
##  GESTION PROXY ONYXIA ##
###########################


# gestion proxy pour appeler la bonne route (transforme /proxy/500 en /)
# Cette classe permet d'adapter Flask au proxy utilisé
# sur SSPCloud /proxy/5000/home -> /proxy/5000
class prefix_proxy:
    def __init__(self, app, prefix="/proxy/5000"):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ["PATH_INFO"].startswith(self.prefix):
            environ["PATH_INFO"] = environ["PATH_INFO"][len(self.prefix) :]
        return self.app(environ, start_response)


# permet de rester sur le proxy Onyxia lorsqu'on y est (SSP CLOUD)
def get_proxy_prefix():
    return "/proxy/5000" if request.host.endswith("user.lab.sspcloud.fr") else ""


###########################
# CREATION DE L'APP FLASK #
###########################

app = Flask(__name__)  # création de l'application

# création d'une clé aléatoire pour chiffrer les sessions
app.secret_key = secrets.token_hex(32)  # on chiffre les info de session dans un cookie
app.wsgi_app = prefix_proxy(app.wsgi_app, prefix="/proxy/5000")


##### PAGE DE CONNEXION #####


@app.route("/", methods=["GET", "POST"])
def connexion():
    login = ""
    proxy_prefix = get_proxy_prefix()

    print(proxy_prefix)  # pour débug

    # lorsque la méthode est GET on affiche la
    # page de connexion (cf. fin du code)

    # lorsque le formulaire de connexion soumis = on récupère
    # le login et le mot de passe fourni par l'utilisation
    if request.method == "POST":
        login = request.form.get("login", "")
        mdp = request.form.get("mot_de_passe", "")

        # On utilise la classe User pour définir un utilisateur
        try:
            user = User(login, mdp)
            if user.connexion():  # lorsque la connexion et valide
                # -> enregistrement login, mdp + redirection vers la page hom
                session["login"] = login
                session["mdp"] = mdp
                return redirect(url_for("home"))

            else:  # message d'erreur lorsque ID ou MDP incorrects
                flash("Mot de passe ou login erroné(s). Veuillez essayer à nouveau.")

        # lorsqu'il y a une erreur on l'affiche dans le terminal
        except Exception as e:
            message = f"Erreur : {e}"

    # Lorsque la méthode est GET : on affiche la page de connexion
    return render_template("connexion.html", login=login, proxy_prefix=proxy_prefix)


##### PAGE D'ACCUEIL #####


@app.route("/home", methods=["GET", "POST"])
def home():
    proxy_prefix = get_proxy_prefix()

    # lorsqu'il n'y a pas (ou plus) de session
    # on demande à l'utilisateur de se reconnecter
    if "login" not in session or "mdp" not in session:
        flash("Votre session a expiré. Veuillez vous reconnecter.")
        return redirect(url_for("connexion"))

    # reconstitution de l'objet utilisateur
    login = session["login"]
    mdp = session["mdp"]
    user = User(login, mdp)

    # récupération date et heure sur le fuseau de Paris
    paris = pytz.timezone("Europe/Paris")
    now = datetime.now(paris)

    # définition de la plage horaire par défaut
    start_default = now
    end_default = start_default + timedelta(hours=1)  # +1h

    # affichage des heures au bon format
    start_time = start_default.strftime("%H:%M")
    end_time = end_default.strftime("%H:%M")
    date = start_default.strftime("%Y-%m-%d")

    # récupération des valeurs envoyées = salles libres
    # lorsque l'utilisateur envoie sa demande (POST)
    salles = None

    if request.method == "POST":
        # récupération de la demande
        date = request.form.get("date", date)
        start_time = request.form.get("start_time", start_time)
        end_time = request.form.get("end_time", start_time)

        # conversion datetime pour la classe User
        start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

        # récupération des salles libres
        # avec salles_libres de la classe User
        salles = user.salles_libres(start=start_dt, end=end_dt)

        #On stocke les salles dans la session pour les récupérer dans la page map
        session["salles_libres"] = salles
    
    else:
        # si GET, on récupère  les dernières salles calculées
        salles = session.get("salles_libres")

    # affichage du résultat
    return render_template(
        "home.html",
        login=login,
        proxy_prefix=proxy_prefix,
        start_time=start_time,
        end_time=end_time,
        date=date,
        salles=salles,
    )

@app.route("/map")
def map_view():
    proxy_prefix = get_proxy_prefix()
    salles_libres = session.get("salles_libres", [])

    return render_template(
        "map_improved.html",
        proxy_prefix=proxy_prefix,
        salles_libres=salles_libres,
    )

# Recupération des salles : 

@app.route("/rooms/geojson")
def get_rooms_geojson():
    """
   Recuperer les géometrie de gpkg des salles - utilisé pour afficher un plan interactif
    """
    if "login" not in session or "mdp" not in session:
        return jsonify({"error": "Vous n'êtes pas identifié"}), 401
    
    try:
        # Recup salles libres
        salles_libres = session.get("salles_libres", [])
        # lire le fichier avec le plan
        gdf_path = os.path.join("rooms", "plan_virtuel_rutabaga.gpkg")
        gdf = gpd.read_file(gdf_path, layer="salles")
        # Filtrer
        if salles_libres:
            gdf = gdf[gdf['label'].isin(salles_libres)]
        # characteristiques pour rajouter des icones plus tard.
        # Les trois premières ça reste à faire encore ! TODO
        gdf['characteristics'] = gdf.apply(lambda row: {
            'has_coffee_nearby': False, 
            'has_projector': False,      
            'capacity': None,             
            'is_computer_room': 'i' in str(row['label']).lower()
        }, axis=1)
        # Convertir en geojson pour pouvoir l'utiliser sur l'app web
        geojson_data = json.loads(gdf.to_json())
        
        return jsonify(geojson_data)
    # Jsp si c'est le code erreur approprié ? je me demande si 404 c'est pas mieux ?
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route("/rooms/background")
def get_background_image():
    """
    Utiliser le plan comme image de fond pour la montrer sur le site
    """
    path = Path(__file__).parent.parent / "rooms" / "planENSAE2.png"
    return send_file(path, mimetype='image/png')

