"""
Ce fichier servira de point d'entrée dans l'appli web rutabaga. Il suffira d'utiliser la commande py main.py pour faire fonctionner le code. 
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
    URL : http://localhost:5000/

    Ctrl + C pour arrêter
    """)
    
    app.run(debug=True, host='0.0.0.0', port=5000)