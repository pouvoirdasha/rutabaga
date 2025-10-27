#Ce code permet de récupérer l'edt des salles pamplemousse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import pytz
import re

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

    def edt(self,duree=1,start : datetime =None):
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
            start = datetime.now()

        start = fuseau.localize(start)

        end= start + timedelta(hours=duree)

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
        return edt

