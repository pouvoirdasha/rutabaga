"""
Ce code permet de récupérer l'edt des salles pamplemousse via la création
de la class User.


Classes :
-------
User :
    Permet de se connecter à Pamplemousse, récupérer l'EDT complet
    et déterminer les salles occupées ou libres sur un créneau donné.


Méthodes de la classe :
-------
    connexion -> permet de se connecter à Pamplemousse
    salles_occupees -> permet d'obtenir les emplois du temps (salles utilisées)
    salles_libres -> permet d'obtenir les emplois du temps (salles inutilisées)

"""

# Librairies
# Connexion à pamplemousse
import requests
from bs4 import BeautifulSoup

# Manipulation des dates
from datetime import datetime, timedelta
import pytz

# Gestion du plan
import geopandas as gpd

# Utilitaires
import json
import re
import os

# ============================================================
# Définition du chemin du plan géospatial
# ============================================================

# Chemins : emplacement du fichier gpkg qui contient le plan
base_dir = os.path.dirname(os.path.abspath(__file__))
gdf_path = os.path.join(base_dir, "plan_virtuel_rutabaga.gpkg")


# ============================================================
# Classe User
# ============================================================

class User:
    """
    La classe User permet de simuler le comportement d'un utilisateur sur
    Pamplemousse afin de récupèrer l'emploi du temps sur une période donnée.

        Paramètres
    ----------
    identifiant : str
        Identifiant de connexion Pamplemousse.
    mdp : str
        Mot de passe de connexion Pamplemousse.
    """

    def __init__(self, identifiant: str, mdp: str):
        """
        Initialisation de la classe User.
        Cette sessions permet de conserver les cookies pour rester
        connecté à Pamplemousse.


        Args:
            identifiant (str) : identifiant sur pamplemousse
            mdp (str) : mot de passe sur pamplemousse
        """
        self.id = identifiant
        self.mdp = mdp
        self.session = requests.Session()  # sauv cookies
        self.autent = False

    def connexion(self) -> bool:
        """
        Connexion sur Pamplemousse.

        Return:
            bool: True si la connexion a pamplemousse fonctionne, False sinon
        """
        url_page = "https://pamplemousse.ensae.fr"

        # requête initiale
        resp_page = self.session.get(url_page)
        soup = BeautifulSoup(resp_page.text, "html.parser")

        # indentification
        sph_org_location = soup.find("input", {"name": "sph_org_location"})[
            "value"
        ]  # scraping sur la page source pamplemousse

        url_connexion = (
            "https://pamplemousse.ensae.fr/site_publishing_helper/login_check/0"
        )
        data = {
            "sph_org_location": sph_org_location,
            "sph_username": self.id,
            "sph_password": self.mdp,
        }
        headers = {"User-Agent": "Mozilla/5.0", "Referer": url_page}

        # tentative de connexion
        response = self.session.post(url_connexion, data=data, headers=headers)

        if response.status_code != 200:
            raise Exception(
                f"Rutabaga ne parvient pas à établir le lien avec Pamplemousse : {response.status_code}"
            )

        # vérification des cookies pour savoir si l'on est bien connecté
        cookies_connexion = self.session.cookies.get_dict()
        if "PHPSESSID" in cookies_connexion:
            print("La connexion à Rutabaga via Pamplemousse est établie.")
            self.autent = True
        else:
            self.autent = False
            print(
                "La connexion à Rutabaga a échoué. Identifiant ou mot de passe incorrect."
            )
        return self.autent


    def salles_occupees(self,
    start: datetime | None = None, 
    end: datetime | None = None) -> list[str] | None:
        """
        Récupération de la liste des salles occupées d'après Pamplemousse sur un créneau donnée.

        Par défaut :
        - `start` = maintenant (fuseau Europe/Paris)
        - `end` = start + 1 heure

        Args:
            start (int): date et heure du début de la recherche des salles occupées (argument optionnel, par défaut vaut la date et heure actuelle)
            end (int): date et heure de la fin de la recherche des salles occupées (argument optionnel, par défaut start +1h)


        Return:
            list[str] | None: renvoie le nom des salles (ou None en cas d'échec)
        """
        if not self.autent:
            print("Tentative de connexion à Rutabaga via Pamplemousse...")
            self.connexion()
        if not self.autent:
            print("Impossible de se connecter. Emploi du temps inaccessible.")
            return None

        url_backend = "https://pamplemousse.ensae.fr/index.php?p=40a0"  # backend
        url_front = "https://pamplemousse.ensae.fr/index.php?p=40a"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": url_front,
        }

        # heure de Paris
        fuseau = pytz.timezone("Europe/Paris")

        # récupération de l'heure actuelle
        if start is None:
            start = datetime.now(fuseau)
        elif start.tzinfo is None:
            start = fuseau.localize(start)

        # heure de fin par défaut = start +1h
        if end is None:
            end = start + timedelta(hours=1)
        elif end.tzinfo is None:
            end = fuseau.localize(end)

        lb = datetime(start.year, start.month, start.day, 0, 0, 0, tzinfo=fuseau)
        ub = datetime(start.year, start.month, start.day, 23, 59, 59, tzinfo=fuseau)

        print(f"Rcherche d'un créneau entre : {start} et {end} ...")

        # on récupère l'emploi du temps de toute la journée
        data = {
            "p": "40a0",
            "start": (lb - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            "end": (ub + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
        }

        resp = self.session.post(url_backend, headers=headers, data=data)
        if resp.status_code == 200:
            print("Rutabaga a accédé à l'emploi du temps avec succès !")
        else:
            print(
                f"Rutabaga ne parvient pas à récupérer l'emploi du temps : {resp.status_code}"
            )
            return None

        extraction_json = json.loads(resp.text)

        # on récupère les salles dispo entre start et end
        edt = []
        for i in extraction_json:
            i_start = fuseau.localize(datetime.fromisoformat(i["start"]))
            i_end = fuseau.localize(datetime.fromisoformat(i["end"]))
            if i_start <= end and i_end >= start:
                temp = re.search(r"salle (.+)", i["title"])
                if temp:
                    temp = temp.group(1).strip()
                    edt.append(temp)
                else:
                    print(
                        f"Extraction de la salle impossible pour l'occurence {i['title']}"
                    )
                del temp
                edt = list(set(edt))
        return edt

    def salles_libres(self, start: datetime = None, end: datetime = None):
        """
        Permet d'obtenir les salles libres sur un intervalle de temps.

        Args:
            start (datetime) : début du créneau
            end (datetime) : fin du créneau

        Return:
            list[str] | None contenant les noms des salles disponibles entre `start` et `end`.
        """

        # lecture du plan virtuel
        gdf = gpd.read_file(gdf_path, layer="salles")

        # on récupère les salles dispo
        salles_occ = self.salles_occupees(start=start, end=end)
        if salles_occ is None or gdf is None:
            return None

        # on récupère les salles du plan du 2e étage
        liste_salles = [
            s for s in gdf["label"].tolist() if s is not None and re.search(r"\d", s)
        ]

        # on en déduit les salles dispo = salles non occupées
        liste_salles_libres = [s for s in liste_salles if s not in salles_occ]
        return liste_salles_libres

