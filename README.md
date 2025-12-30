# rutabaga
Rutabaga est un projet d'extension de Pamplemousse permettant d'identifier facilement les salles inoccupées à l'Ensae. L'accès à Rutabaga se fait via les identifiants de connexion Pamplemousse. L'idée est venue de notre envie de simplifier la vie des étudiantes et étudiants dans la recherche de salles où il est possible de travailler.

Le projet est porté par 4 étudiants : 
* @pouvoirdasha
* @Sacha-N
* @jlechat 
* @xdalp / @mgarbe

## Conteneur docker : 
Le dockerfile est pre-configuré pour avoir une version light du projet qui pèse environ 1 Go. La version dev du dockerfile avec uv donnerait un container de 12 Go : l'écart s'explique par les nombreuses dépendances utilisées pour nos transformations du plan de l'Ensae. Pour utiliser le docker (version light), il est possible d'utiliser la commande suivant pour build le container, depuis la racine du projet : 
```
docker build -t rutabaga-light .
```
Et ensuite, il est possible de le run (et accéder au projet sur l'adresse http://localhost:5000/ : 
```
 docker run -p 5000:5000 rutabaga-light
```

## Déploiment :
L’application est déployée sur une instance fly.io. L’URL est transmise sur demande.

## Guide d'installation de la version dev depuis Git : 
Pour faire tourner rutabaga en local et l'ensemble des scripts mobilisés en amont, il est préférable d'installer `uv` et utiliser `uv sync` avec le uv.lock. Pour installer `uv`, voir [la documentation](https://docs.astral.sh/uv/getting-started/installation/#installation-methods). Le service `VSCode-Python` du SSPCloud permet sinon d'éviter cette installation.

Pour charger l'ensemble des dépendances, faire : 
```
uv sync
```
La manière la plus simple pour lancer l'application est ensuite d'utiliser uv :
```
uv run python main.py
```
A défaut, il est également possible d'activer l'environnement virtuel de manière habituelle, puis utiliser : 
```
uv run python main.py
```
Ou avec votre commande habituelle (python3/python/.. etc). Il faudra alors utiliser les dépendances listées dans `reqs2.txt` (version dev, identique au `uv lock`) ou `requirements.txt` (version light). L'adresse sur laquelle il est possible d'accéder à l'app est indiquée dans les logs du lancement. 