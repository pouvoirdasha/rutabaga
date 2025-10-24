#Ce code permet de récupérer l'edt des salles pamplemousse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta 
import json

class User:
    def __init__(self,identifiant : str, mdp : str):
        self.id=identifiant
        self.mdp=mdp
        self.session=requests.Session()  #sauv cookies
        self.autent=False
    
    def connexion(self):
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

    #LA METHODE NE FONCTIONNE PAS ENCORE (renvoie une liste vide), IL FAUT TROUVER LE ENDPOINT JSON de "EDT - TOUT" sur PAMPLEMOUSSE 
    def edt(self,duree=1,start : datetime =None):
        if not self.autent:
            print("Tentative de connexion à Rutabaga via Pamplemousse...")
            self.connexion()
        if not self.autent:
            print("Impossible de se connecter. Edt inaccessible")
            return None
        
        url_backend="https://pamplemousse.ensae.fr/index.php?p=4040" #backend
        url_front="https://pamplemousse.ensae.fr/index.php?p=404"
        headers={
        "User-Agent": "Mozilla/5.0",
        #"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": url_front,}

        if start is None:
            start = datetime.now()  #maintenant
        end= start + timedelta(hours=duree)
        start = start.strftime("%Y-%m-%d %H:%M")
        end=end.strftime("%Y-%m-%d %H:%M")

        data= {"start": start, "end": end}

        resp = self.session.post(url_backend, headers=headers, data=data)
        if resp.status_code == 200:
            print("Rutabaga a accédé à l'Edt avec succès !")
            return json.loads(resp.text)
        else:
            print(f"Rutabaga ne parvient pas à récupérer l'Edt : {resp.status_code}")
            return None

