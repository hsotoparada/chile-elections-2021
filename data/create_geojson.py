# This script...

import pandas as pd
import numpy as np
import os
from glob import glob
import time
import json
import pickle
import unidecode
import re

# -----------------------------------------------------------------------------
# create geojson from shape files of comunas
# Comunas shape file taken from: http://siit2.bcn.cl/mapas_vectoriales/index_html/
cmd = "ogr2ogr -f 'GeoJSON' -t_srs crs:84 data/chile_comunas_tmp.geojson data/comunas/comunas.shp -simplify 1000"
os.system(cmd)

# create geojson from shape files of regions
cmd = "ogr2ogr -f 'GeoJSON' -t_srs crs:84 data/chile_regions_tmp.geojson data/regiones/Regional.shp -simplify 1000"
os.system(cmd)

# preprocess geojson for comunas
with open('data/chile_comunas_tmp.geojson') as f:
    geojson_comunas = json.load(f)

comunas_id = {}
for i in range(len(geojson_comunas['features'])):
    city = geojson_comunas['features'][i]['properties']['Comuna']
    city = unidecode.unidecode(city).upper()
    if city == "TREGUACO":
        city = "TREHUACO"
    obj_id = str(geojson_comunas['features'][i]['properties']['objectid'])
    print(city, geojson_comunas['type'])
    geojson_comunas['features'][i]['properties']['Comuna'] = f"{obj_id}-{city}"
    # geojson['features'][i]['properties'] = {'comuna': f"{obj_id}-{city}"}
    geojson_comunas['features'][i]['id'] = obj_id
    comunas_id[city] = obj_id

with open('data/chile_comunas.geojson', 'w') as f:
    json.dump(geojson_comunas, f)

with open('data/comunas_id.pkl', 'wb') as pout:
    pickle.dump(comunas_id, pout)

# preprocess geojson for regions
with open('data/chile_regions_tmp.geojson') as f:
    geojson_regions = json.load(f)

regions_id = {}
for i in range(len(geojson_regions['features'])):
    region = geojson_regions['features'][i]['properties']['Region']
    region = unidecode.unidecode(region).upper()
    obj_id = str(geojson_regions['features'][i]['properties']['objectid'])
    print(region, geojson_regions['type'])
    geojson_regions['features'][i]['properties']['Region'] = f"{obj_id}-{region}"
    geojson_regions['features'][i]['id'] = obj_id
    region = re.sub("REGION ", "", region)
    if "NUBLE" in region:
        region = re.sub("NUBLE", "ÑUBLE", region)
    if "BIO-BIO" in region:           
        region = re.sub("BIO-BIO", "BIOBIO", region)
    if "BERNARDO" in region:
        region = re.sub("BERNARDO", "GENERAL BERNARDO", region)
    if "GRAL.IBANEZ" in region:
        region = re.sub("GRAL.IBANEZ", "GENERAL CARLOS IBAÑEZ", region)
    if "Y ANTARTICA" in region:
        region = re.sub("Y ANTARTICA", "Y DE LA ANTARTICA", region)        
    if region == "ZONA SIN DEMARCAR":
        continue
    regions_id[region] = obj_id

with open('data/chile_regions.geojson', 'w') as f:
    json.dump(geojson_regions, f)

with open('data/regions_id.pkl', 'wb') as pout:
    pickle.dump(regions_id, pout)

# -----------------------------------------------------------------------------
# reopen saved data
# with open('data/comunas_id.pkl', 'rb') as pin:
#     comunas_id = pickle.load(pin)

# with open('data/regions_id.pkl', 'rb') as pin:
#     regions_id = pickle.load(pin)

# with open('data/chile_comunas.geojson') as f:
#     geojson_comunas = json.load(f)

# with open('data/chile_regions.geojson') as f:
#     geojson_regions = json.load(f)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# TODO: handle missing ids (e.g. NIQUEN)
#
# read dataframes of votes
df_votes = pd.read_csv('data/votes_region.csv')
df_participa = pd.read_csv('data/participacion_region.csv')

# correct missspelling cities
df_votes["City"].replace(
    to_replace={"CABO DE HORNOS(EX-NAVARINO)": "CABO DE HORNOS"},
    inplace=True
    )
df_participa["City"].replace(
    to_replace={"CABO DE HORNOS(EX-NAVARINO)": "CABO DE HORNOS"},
    inplace=True
    )

# include ids of comunas in dataframes of votes 
cities = df_votes["City"].values
print(len(cities))
cities_new, cities_new_ids = [],[]
for city in cities:
    try:
        city_with_id = f"{comunas_id[unidecode.unidecode(city).upper()]}-{city}"
        # city_id = str(comunas_id[city])
        city_id = str(comunas_id[unidecode.unidecode(city).upper()])
        # city = unidecode.unidecode(city).upper()
    except KeyError:
        city_with_id = city
        city_id = str(-99)
    cities_new.append(city_with_id)
    cities_new_ids.append(city_id)
print(len(cities_new))
#
# include ids of regions in dataframes of votes 
# regions = df_votes["Region"].unique()
# print(len(regions))
# regions_new, regions_new_ids = [],[]
# for region in regions:
#     try:
#         region_with_id = f"{regions_id[region]}-{region}"
#         region_id = str(regions_id[region])
#     except KeyError:
#         region_with_id = region
#         region_id = str(-99)
#     regions_new.append(region_with_id)
#     regions_new_ids.append(region_id)
# print(len(regions_new))
#
df_votes["City_id"] = cities_new_ids
df_votes["City_with_id"] = cities_new
df_votes["Region_id"] = df_votes.apply(
    lambda x: regions_id[x["Region"]]
    if x["Region"] in regions_id else -99,
    axis=1
)
df_votes["Region_with_id"] = df_votes.apply(
    lambda x: f"{regions_id[x['Region']]}-{x['Region']}"
    if x["Region"] in regions_id else -99,
    axis=1
)
#
df_participa["City_id"] = cities_new_ids
df_participa["City_with_id"] = cities_new
df_participa["Region_id"] = df_participa.apply(
    lambda x: regions_id[x["Region"]]
    if x["Region"] in regions_id else -99,
    axis=1
)
df_participa["Region_with_id"] = df_participa.apply(
    lambda x: f"{regions_id[x['Region']]}-{x['Region']}"
    if x["Region"] in regions_id else -99,
    axis=1
)
print(df_votes.head())
df_votes.to_csv("data/votes_region_geojson.csv", index=False)
df_participa.to_csv("data/participacion_region_geojson.csv", index=False)

# -----------------------------------------------------------------------------
# extract centers of each region and save them
dct_centers = {}
regions = df_votes["Region"].unique()
for region in regions:
    df_in = df_votes[df_votes["Region"] == region]
    # geojson_show = geojson.copy()
    city_ids = df_in['City_id'].values
    features_in = [f for f in geojson_comunas['features'] if f['id'] in city_ids]
    # geojson_show['features'] = features_show
    coords = np.array([])
    for feature in features_in:
        coords_in = np.array(feature['geometry']['coordinates'][0])
        if coords_in.ndim in [1,3]:
            coords_in = np.array(feature['geometry']['coordinates'][0][0])
        try:
            coords = np.vstack((coords, coords_in))
        except ValueError:
            coords = coords_in
        print(feature['properties']['Comuna'], coords_in.shape)
        # if feature['properties']['Comuna'] == "163-IQUIQUE":
        # if feature['properties']['Comuna'] == "195-CASABLANCA":
        #     break
    if region == "DE VALPARAISO":
        coords = np.array([x for x in coords[:] if x[0] > -72.]) # center is onshore
    # lon_mean, lat_mean = coords.mean(axis=0)
    lon_min, lat_min = coords.min(axis=0)
    lon_max, lat_max = coords.max(axis=0)
    lon_mean = (lon_min + lon_max)*.5
    lat_mean = (lat_min + lat_max)*.5
    print(region, lon_mean, lat_mean, coords.shape)
    dct_centers[region] = {'lon': lon_mean, 'lat': lat_mean}
#
lons_center = np.array([x['lon'] for x in list(dct_centers.values())])
lats_center = np.array([x['lat'] for x in list(dct_centers.values())])
lon_center = (lons_center.min() + lons_center.max()) * .5
lat_center = (lats_center.min() + lats_center.max()) * .5
dct_centers["ALL PER CITY"] = {'lon': lon_center, 'lat': lat_center}
dct_centers["ALL PER REGION"] = {'lon': lon_center, 'lat': lat_center}
#
with open('data/region_centers.pkl', 'wb') as pout:
    pickle.dump(dct_centers, pout)
    
# -----------------------------------------------------------------------------
# remove temporary files
cmd = "rm data/chile_comunas_tmp.geojson"
os.system(cmd)




