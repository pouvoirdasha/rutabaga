"""
Ce code permet de construire le geodataframe des salles du 2e étage de l'ENSAE.
"""

import cv2
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.affinity import affine_transform
import geopandas as gpd
import shapely.affinity
import easyocr
from geopandas import sjoin
import re
import numpy as np
import pandas as pd
from pathlib import Path


path_plan = Path(__file__).parent / "planENSAE2.png"

# 1. A partir d'une image on extrait les salles en gdf

print("Début de la construction de la base de données des salles de Rutabaga...")
print("Lecture du plan...")

# extraction contours
plan = cv2.imread(str(path_plan), cv2.IMREAD_GRAYSCALE)
_, thresh = cv2.threshold(plan, 100, 255, cv2.THRESH_BINARY)  # discrimination N&B
contours, _ = cv2.findContours(
    thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
)  # extraction contours -> on passe l'image en gris puis en noir et blanc
# pour extraire les contours avec findContours

# élimination bruit + création gdf
polys = []
for c in contours:
    if cv2.contourArea(c) > 500:  # supression bruit
        polys.append(Polygon(c[:, 0, :]))
gdf = gpd.GeoDataFrame(geometry=polys)
gdf = gdf.set_crs(None, allow_override=True)
# gdf contient les polygones 

# calcul des aires
gdf["area_px"] = gdf["geometry"].apply(lambda poly: poly.area)  # en pixels

batiment = gdf.loc[gdf["area_px"].idxmax(), "geometry"]
min_x, min_y, max_x, max_y = batiment.bounds
width = max_x - min_x
height = max_y - min_y
ratio = width / height
# on sait que le batiment est un carré : le ratio l/L proche de 1
if not (0.95 <= ratio <= 1.05):
    raise ValueError(
        "Rutabaga ne parvient pas à détecter le batîment à partir du plan fourni et ne peut pas construire le gdf."
    )

scale_factor = 80 / width  # calcul de l'echelle -> batiment de environ 80m

gdf["geometry_m"] = gdf["geometry"].apply(
    lambda poly: shapely.affinity.scale(poly, xfact=scale_factor, yfact=scale_factor, origin=(0, 0))
)  # conversion geom de pxl en m
gdf["area_m2"] = gdf["geometry_m"].apply(lambda poly: poly.area)  # calcul en m2

# filtre : on ne garde que les volumes de moins de 1000m2
# cela permet de ne conserver que les salles (on évite
# les formes comme le couloirs...)
gdf = gdf[gdf["area_m2"] < 1000]


# 2. on extrait les noms des salles

# les salles info sont du type : 2048i -> si on a 20481 on 
# transforme le 1 en i (chaque salle à 4 chiffres)
def correction_i(text: str) -> str:
    return re.sub(r"(?<=\d{4})1", "i", text)  # correction si mauvaise lecture i info


lecteur = easyocr.Reader(["fr"])
noms = lecteur.readtext(plan)
geom = [Polygon(bbox) for bbox, text, _ in noms]
noms_gdf = gpd.GeoDataFrame(
    [
        {"label": correction_i(text), "geometry": poly}
        for (bbox, text, _), poly in zip(noms, geom)
    ],
    geometry="geometry",
    crs="EPSG:4326",
)
noms_gdf = noms_gdf.set_crs(None, allow_override=True)

# appariement salles et noms
gdf = sjoin(gdf, noms_gdf, how="left", predicate="intersects")
print(f'Rutabaga a détecté {gdf.sort_values("label")["label"].tolist()}')
print(f"Rutabaga a détecté {gdf[gdf['area_m2'] < 100].shape[0]} salles de classe.")


# 3. on extrait les fontaines à eau (point bleu)

plan_color = cv2.imread(str(path_plan))
hsv = cv2.cvtColor(
    plan_color, cv2.COLOR_BGR2HSV
)  # conversion hsv pour capter les couleurs
inf_bleu = np.array([100, 50, 50])
sup_bleu = np.array([140, 255, 255])
masque_bleu = cv2.inRange(hsv, inf_bleu, sup_bleu)  # masque bleu pour capter les fontaines
contours_bleus, _ = cv2.findContours(
    masque_bleu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
)

pts_bleus = []
for c in contours_bleus: 
    if cv2.contourArea(c) > 1:
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
            pts_bleus.append(Point(cx, cy))

gdf_fontaines = gpd.GeoDataFrame(
    {"label": ["Fontaine à eau"] * len(pts_bleus), "geometry": pts_bleus},
    geometry="geometry",
    crs="EPSG:4326",
)
gdf_fontaines = gdf_fontaines.set_crs(None, allow_override=True)

# -> transformation des fontaines en petits ronds (polygones) via buffer
rayon_fontaine_px = 3  # rayon en pixels sur le plan, ajustable
gdf_fontaines["geometry"] = gdf_fontaines.geometry.buffer(rayon_fontaine_px)

gdf = pd.concat([gdf, gdf_fontaines], ignore_index=True)  # ajout des fontaines au gdf
gdf["label"] = gdf["label"].fillna("")
gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs="EPSG:4326")  # geodataframe

print(gdf)

# Affichage du plan virtuel pour check visuel 
gdf_polys = gdf[gdf.geometry.type == "Polygon"]
gdf_points = gdf[gdf.geometry.type == "Point"]
gdf_polys.crs = None  # pas de ref geo
gdf_points.crs = None  # pas de ref geo

# séparation salles / fontaines pour l'affichage
gdf_salles = gdf_polys[gdf_polys["label"] != "Fontaine à eau"]
gdf_fontaines_plot = gdf_polys[gdf_polys["label"] == "Fontaine à eau"]

fig, ax = plt.subplots(figsize=(10, 10))

# salles en gris
gdf_salles.plot(ax=ax, color="lightgrey", edgecolor="black", alpha=0.1)

# fontaines en bleu (petits ronds)
gdf_fontaines_plot.plot(ax=ax, color="blue")

for idx, row in gdf_salles.iterrows():
    x, y = row.geometry.centroid.coords[0]
    if row.label is not None:
        ax.text(x, y, row.label, fontsize=8, ha="center", va="center", color="black")

ax.invert_yaxis()
plt.show()
plt.savefig("plan_virtuel_rutabaga.png", dpi=300)

# Inversion axe y pour correspondre au système de coordonnées de Leaflet
# -> on travaille sur une copie dédiée à l'export pour Leaflet
print("Préparation du gdf pour export (flip axe Y pour Leaflet)...")

gdf_export = gdf.copy()

minx, miny, maxx, maxy = gdf_export.total_bounds
sum_y = miny + maxy

def flip_y_geom(geom):
    # affine_transform params: [a, b, d, e, xoff, yoff]
    # x' = 1*x + 0*y + 0
    # y' = 0*x - 1*y + (max_y + min_y)
    if geom is None:
        return geom
    return affine_transform(geom, [1, 0, 0, -1, 0, sum_y])

gdf_export["geometry"] = gdf_export["geometry"].apply(flip_y_geom)

# enregistrement df
print("Ecriture du gdf produit par Rutabaga.")
gdf_export = gdf_export.drop(columns=["area_px", "geometry_m"]).copy()  ## on retire juste area_px, on garde la geometrie flippée

# Détermination des chemins de sortie
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

gpkg_path   = project_root / "rooms" / "plan_virtuel_rutabaga.gpkg"
geojson_path = project_root / "app" / "static" / "data" / "plan_virtuel_rutabaga.geojson"

# Export
gdf_export.to_file(gpkg_path, layer="salles", driver="GPKG")
gdf_export.to_file(geojson_path, driver="GeoJSON")

print("Fichiers écrits :")
print(f"  - {gpkg_path}")
print(f"  - {geojson_path}")
