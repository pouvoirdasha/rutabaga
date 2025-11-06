from flask import Flask, render_template, request,redirect, url_for, session, flash
from datetime import datetime, timedelta
from classes import User
import pytz
import secrets

#gestion proxy pour appeler la bonne route (transforme /proxy/500 en /)
class prefix_proxy:
    def __init__(self, app, prefix='/proxy/5000'):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
        return self.app(environ, start_response)

#permet de rester sur le proxy
def get_proxy_prefix():
    return '/proxy/5000' if request.host.endswith('user.lab.sspcloud.fr') else ''


app = Flask(__name__)
app.secret_key = secrets.token_hex(32) #on chiffre les info de session dans un cookie
app.wsgi_app = prefix_proxy(app.wsgi_app, prefix='/proxy/5000')


@app.route('/', methods=['GET', 'POST'])
def connexion():
    login = ''
    proxy_prefix = get_proxy_prefix()
    print(proxy_prefix)
    if request.method == 'POST':
        login = request.form.get('login', '')
        mdp = request.form.get('mot_de_passe', '')
        try:
            user = User(login, mdp)
            if user.connexion():
                session['login'] = login
                session['mdp'] = mdp
                return redirect(url_for('home'))
            else:
                flash("Mot de passe ou login erroné(s). Veuillez essayer à nouveau.")
        except Exception as e:
            message = f"Erreur : {str(e)}"
    return render_template('connexion.html', login=login, proxy_prefix=proxy_prefix)


@app.route('/home',methods=['GET','POST'])
def home():
    proxy_prefix = get_proxy_prefix()

    if 'login' not in session or 'mdp' not in session:
        flash("Votre session a expiré. Veuillez vous reconnecter.")
        return redirect(url_for('connexion'))

    #reconstitution de l'objet utilisateur
    login = session['login']
    mdp = session['mdp']
    user = User(login, mdp)

    #récupération date et heure 
    paris = pytz.timezone("Europe/Paris")
    now = datetime.now(paris)  
    start_default = now
    end_default = start_default + timedelta(hours=1)
    start_time = start_default.strftime("%H:%M")
    end_time = end_default.strftime("%H:%M")
    date = start_default.strftime("%Y-%m-%d")

    #récupération des valeurs envoyées
    salles = None
    if request.method == 'POST':
        date = request.form.get('date', date)
        start_time = request.form.get('start_time', start_time)
        end_time = request.form.get('end_time', start_time)
        
        #conversion datetime
        start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

        #récupération des salles libres
        salles = user.salles_libres(start=start_dt, end=end_dt)

    return render_template('home.html', 
        login=login, 
        proxy_prefix=proxy_prefix,
        start_time=start_time,
        end_time=end_time,
        date=date,
        salles=salles)