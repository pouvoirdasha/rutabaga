"""
Ce code permet de construire le geodataframe des salles du 2e étage de l'ENSAE. 
"""

import cv2
import matplotlib
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import geopandas as gpd
import shapely.affinity
import easyocr
from geopandas import sjoin
import re

#1. A partir d'une image on extrait les salles en gdf

print("Début de la construction de la base de données des salles de Rutabaga...")
print("Lecture du plan...")
#extraction contours
plan = cv2.imread("rutabaga/planENSAE2.png", cv2.IMREAD_GRAYSCALE)
_, thresh = cv2.threshold(plan, 100, 255, cv2.THRESH_BINARY) #discrimination N&B
contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) #extraction contours

#élimination bruit + création gdf
polys = []
for c in contours:
    if cv2.contourArea(c) > 500:  #supression bruit
        polys.append(Polygon(c[:, 0, :]))
gdf = gpd.GeoDataFrame(geometry=polys)

#calcul des aires 
gdf["area_px"] = gdf["geometry"].apply(lambda poly: poly.area) #en pixels

batiment = gdf.loc[gdf["area_px"].idxmax(), "geometry"]
min_x, min_y, max_x, max_y = batiment.bounds
width = max_x - min_x
height = max_y - min_y
ratio = width / height
if not (0.95 <= ratio <= 1.05):
    raise ValueError("Rutabaga ne parvient pas à détecter le batîment à partir du plan fourni et ne peut pas construire le gdf.")
scale = 80 / width  #calcul de l'echelle

gdf["geometry_m"] = gdf["geometry"].apply(
    lambda poly: shapely.affinity.scale(poly, xfact=scale, yfact=scale, origin=(0,0))) #conversion geom de pxl en m
gdf["area_m2"] = gdf["geometry_m"].apply(lambda poly: poly.area) #calcul en m2

#filtre : on ne garde que les volumes de moins de 1000m2
gdf=gdf[gdf["area_m2"]<1000]



#2. on extrait les noms 

def correction_i(text):
    return re.sub(r'(?<=\d{4})1', 'i', text) #correction si mauvaise lecture i info

lecteur = easyocr.Reader(['fr'])
noms =lecteur.readtext(plan)
geom= [Polygon(bbox) for bbox, text, _ in noms] 
noms_gdf = gpd.GeoDataFrame(
    [{'label': correction_i(text), 'geometry': poly} for (bbox, text,_), poly in zip(noms, geom)],
    geometry='geometry',
    crs="EPSG:4326"
)



#appariement salles et noms
gdf = sjoin(gdf, noms_gdf, how="left", predicate="intersects")
print(f'Rutabaga a détécté {gdf.sort_values("label")["label"].tolist()}')
print(f"Rutabaga a détecté {gdf[gdf["area_m2"]<100].shape[0]} salles de classe.")

print(gdf)
#Affichage du plan virtuel
matplotlib.use('Agg')
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.1)
for idx, row in gdf.iterrows():
    x, y = row['geometry'].centroid.coords[0]
    ax.text(x, y, row['label'], fontsize=8, ha='center', va='center', color='black')
ax.invert_yaxis()
plt.show()
plt.savefig("rutabaga/plan_virtuel_rutabaga.png", dpi=300)