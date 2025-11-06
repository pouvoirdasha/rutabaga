from flask import Flask, render_template, request
from classes import User

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
app.wsgi_app = prefix_proxy(app.wsgi_app, prefix='/proxy/5000')


@app.route('/', methods=['GET', 'POST'])
def connexion():
    login = ''
    message = ''
    proxy_prefix = get_proxy_prefix()
    print(proxy_prefix)
    if request.method == 'POST':
        login = request.form.get('login', '')
        mdp = request.form.get('mot_de_passe', '')
        try:
            user = User(login, mdp)
            if user.connexion():
                return f"Bonjour {login} !"
            else:
                message = "Mauvais mot de passe"
        except Exception as e:
            message = f"Erreur : {str(e)}"
    return render_template('connexion.html', login=login, message=message, proxy_prefix=proxy_prefix)