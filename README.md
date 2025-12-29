# rutabaga

Rutabaga est un projet d'extension de Pamplemousse permettant aux étudiants d'identifier facilement les salles inoccupées. 
L'accès à Rutabaga se fait via les identifiants de connexion Pamplemousse. 
L'idée est venue de notre envie de simplifier la vie des étudiants et étudiantes de l'école dans la recherche de salles où il est possible de travailler. 


Le projet est porté par 4 étudiants : 
* @pouvoirdasha
* @Sacha-N
* @jlechat 
* @xdalp / @mgarbe

## Guide d'installation depuis Git : 
Pour faire tourner le code depuis votre ordinateur, il est préférable d'installer uv et utiliser uv sync avec le uv.lock (pour la version dev). Pour installer uv, voir [la documentation](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).
Pour synchroniser, faire : 
```
uv sync
```
Activer l'environnement virtuel de manière habituelle. 
L'appli peut-être lancée avec 
```
py main.py
```
Ou avec votre commande habituelle (python3/python/.. etc). L'adresse sur laquelle il est possible d'accéder à l'app est indiquée dans les logs du lancement. 

## Conteneur docker : 


#### Disclaimer sur l'usage de l'IA 

A titre personnel, @pouvoirdasha certifie ne pas avoir utilisé l'IA pour les tâches en python. Pour la mise en page, et en particulier pour la partie javascript de leaflet pour gérer la carte, le modèle Gemini a été utilisé. Le reste en grande partie a été inspiré des threads stack overflow, des tutoriels en ligne, et des sites design (palette, polices, direction artistique du projet).
