"""
Ce fichier servira de point d'entrée dans l'appli web rutabaga. Il suffira d'utiliser la commande py main.py pour faire fonctionner le code. 

"""

"""
main.py - Lanceur de l'application Rutabaga
"""
import sys
import os

# Ajouter le dossier courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer l'application Flask
from app.app import app

if __name__ == '__main__':
    print("""
    ...................
    RUTABAGA DEMARRAGE 
    ...................
    Serveur démarré !
    URL : http://127.0.0.1:5000
    
    Ouvrez cette adresse dans votre navigateur
    Appuyez sur Ctrl+C pour arrêter
    """)
    
    app.run(debug=True, host='127.0.0.1', port=5000)