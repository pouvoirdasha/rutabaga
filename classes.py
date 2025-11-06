"""
Ce code permet de récupérer l'edt des salles pamplemousse via la création de la class User.

Méthodes de la classe :
    connexion -> permet de se connecter à Pamplemousse
    edt -> permet d'obtenir les emplois du temps (salles utilisées)


"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import geopandas as gpd
import json
import pytz
import re
import os


#chemins
base_dir = os.path.dirname(os.path.abspath(__file__))
gdf_path = os.path.join(base_dir, "plan_virtuel_rutabaga.gpkg")


class User:
    """
    La classe User permet de simuler le comportement d'un utilisateur sur Pamplemousse 
    afin de récupèrer l'emploi du temps sur une période données.
    """
    
    def __init__(self,identifiant : str, mdp : str):
        """
        Initialisation de la classe User.

        
        Args:
            identifiant (str) : identifiant sur pamplemousse
            mdp (str) : mot de passe sur pamplemousse
        """
        self.id=identifiant
        self.mdp=mdp
        self.session=requests.Session()  #sauv cookies
        self.autent=False
    
    def connexion(self) -> bool:
        """
        Connexion sur Pamplemousse.

        Return:
            bool: True si la connexion a pamplemousse fonctionne, False sinon
        """
        url_page ="https://pamplemousse.ensae.fr"
        resp_page =self.session.get(url_page)
        soup = BeautifulSoup(resp_page.text, 'html.parser')
        sph_org_location =soup.find('input', {'name': 'sph_org_location'})['value']  #scraping sur la page source pamplemousse

        url_connexion="https://pamplemousse.ensae.fr/site_publishing_helper/login_check/0"
        data={
            "sph_org_location": sph_org_location,
            "sph_username": self.id, 
            "sph_password": self.mdp,}
        headers = {"User-Agent": "Mozilla/5.0","Referer": url_page}
        response = self.session.post(url_connexion, data=data,headers=headers)
    
        if response.status_code != 200:
            raise Exception(f"Rutabaga ne parvient pas à établir le lien avec Pamplemousse : {response.status_code}")

        cookies_connexion=self.session.cookies.get_dict()
        if "PHPSESSID" in cookies_connexion:
            print("Vous êtes connecté à Rutabaga via Pamplemousse")
            self.autent=True
        else:
            self.autent=False
            print("Echec de la connexion à Rutabaga. Identifiant ou mot de passe incorrect.")
        return self.autent

    
    def salles_occupees(self,start : datetime =None, end : datetime=None):
        """
        Récupération de la liste des salles occupées d'après Pamplemousse sur un créneau donnée.

        Args:
            duree (int): durée du créneau pour obtenir les salles occupées (argument optionnel, par défaut vaut 1)
            start (int): date et heure du début de la recherche des salles occupées (argument optionnel, par défaut vaut la date et heure actuelle)

        Return:
            list de str: renvoie le nom des salles (ou None en cas d'échec)
        """
        if not self.autent:
            print("Tentative de connexion à Rutabaga via Pamplemousse...")
            self.connexion()
        if not self.autent:
            print("Impossible de se connecter. Edt inaccessible")
            return None
        
        url_backend="https://pamplemousse.ensae.fr/index.php?p=40a0" #backend
        url_front="https://pamplemousse.ensae.fr/index.php?p=40a"
        headers={
        "User-Agent": "Mozilla/5.0",
        #"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": url_front,}

        fuseau=pytz.timezone("Europe/Paris")

        if start is None:
            start = datetime.now(fuseau)
        elif start.tzinfo is None:
            start = fuseau.localize(start)

        if end is None:
            end = start + timedelta(hours=1)
        elif end.tzinfo is None:
            end = fuseau.localize(end)

        lb = datetime(start.year, start.month, start.day, 0, 0, 0, tzinfo=fuseau)
        ub = datetime(start.year, start.month, start.day, 23, 59, 59, tzinfo=fuseau)

        print(f"Rcherche d'un créneau entre : {start} et {end} ...")

        data= {
            "p": "40a0",
            "start": (lb - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), 
            "end": (ub+ timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),}

        resp = self.session.post(url_backend, headers=headers, data=data)
        if resp.status_code == 200:
            print("Rutabaga a accédé à l'Edt avec succès !")
        else:
            print(f"Rutabaga ne parvient pas à récupérer l'Edt : {resp.status_code}")
            return None

        extraction_json=json.loads(resp.text)

        edt=[]
        for i in extraction_json:
            i_start=fuseau.localize(datetime.fromisoformat(i["start"])) 
            i_end= fuseau.localize(datetime.fromisoformat(i["end"]))
            if i_start <= end and i_end >= start:
                temp =re.search(r"salle (.+)", i['title'])
                if temp:  
                    temp = temp.group(1).strip()
                    edt.append(temp)
                else:
                    print(f"Extraction de la salle impossible pour l'occurence {i['title']}")
                del temp 
                edt = list(set(edt))
        return edt

    def salles_libres(self,start : datetime =None, end : datetime =None):
        gdf = gpd.read_file(gdf_path, layer="salles")
        salles_occ=self.salles_occupees(start=start, end =end)
        if salles_occ is None or gdf is None:
            return None
        liste_salles = [s for s in gdf['label'].tolist() if s is not None and re.search(r'\d', s)]
        liste_salles_libres = [s for s in liste_salles if s not in salles_occ]
        return liste_salles_libres



class Salle:
    """
    La classe Salle permet de calculer des informations sur les salles
    """

    def __init__(self,label : str):
        """
        Initialisation de la classe User.
        Args:
            label (str) : nom de la salle
        """
        self.label=label
        self.geometry=None
        #ajouter la géométrie !
    
    def distance(self, objet : str):
        """
        Idée : pour un objet donné on calcul la distance de la salle à l'objet 
        cf. Isssues
        """
    
    def projection_couloir(self):
        """
        Projection dans le couloir pour calcul des déplacements
        """

    def capacite(self):
        """
        Estimation capacité avec l'aire (trouver un ratio nb places / m2)
        """

    def info(self):
        """
        detection si salle info : teste la présence d'un i dans le label
        """
    

    
