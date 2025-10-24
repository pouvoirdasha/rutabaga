#Ce code permet de récupérer l'edt des salles pamplemousse
import requests
from bs4 import BeautifulSoup

class User:
    def __init__(self,identifiant : str, mdp : str):
        self.id=identifiant
        self.mdp=mdp
        self.session=requests.Session()  #sauv cookies
        self.autent=False
    
    def connexion(self):
        url_page ="https://pamplemousse.ensae.fr/index.php?p=400"
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