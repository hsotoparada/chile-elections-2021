# This script...

import pandas as pd
import numpy as np
import os
from glob import glob
import time
import json
import pickle
import unidecode

# fs = glob("../geo/region*/*.geojson")
# print(fs)
#
# geojson_features = []
# for f in fs:
#     with open(f) as j:
#         if f == '../geo/region_de_valparaiso/all.geojson':
#             pass
#         geojson = json.load(j)
#         for i in range(len(geojson['features'])):
#             city = geojson['features'][i]['properties']['NOM_COM']
#             city = unidecode.unidecode(city).upper()
#             print(f, city, geojson['type'])
#             geojson['features'][i]['properties']['NOM_COM'] = city
#         geojson_features.extend(geojson['features'])
#
# geojson_out = {
#     'features': geojson_features,
#     'type': 'FeatureCollection'
# }

# create geojson from shape files of comunas
# Comunas shape file taken from: http://siit2.bcn.cl/mapas_vectoriales/index_html/
cmd = "ogr2ogr -f 'GeoJSON' -t_srs crs:84 data/chile_comunas_tmp.geojson data/comunas/comunas.shp -simplify 2000"
os.system(cmd)

with open('data/chile_comunas_tmp.geojson') as f:
    geojson = json.load(f)

comunas_id = {}
for i in range(len(geojson['features'])):
    city = geojson['features'][i]['properties']['Comuna']
    city = unidecode.unidecode(city).upper()
    obj_id = str(geojson['features'][i]['properties']['objectid'])
    print(city, geojson['type'])
    geojson['features'][i]['properties']['Comuna'] = f"{obj_id}-{city}"
    # geojson['features'][i]['properties'] = {'comuna': f"{obj_id}-{city}"}
    geojson['features'][i]['id'] = obj_id
    comunas_id[city] = obj_id

with open('data/chile_comunas.geojson', 'w') as f:
    json.dump(geojson, f)

with open('data/comunas_id.pkl', 'wb') as pout:
    pickle.dump(comunas_id, pout)

# with open('data/chile_regions.geojson') as f:
#     geojson_ch = json.load(f)

# TODO: handle missing ids (e.g. NIQUEN)
# include ids of comunas in votes dataframe
df = pd.read_csv('data/votes_region.csv')
cities = df["City"].values
print(len(cities))
cities_new, ids = [],[]
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
    ids.append(city_id)
#
print(len(cities_new))
df["City_with_id"] = cities_new
df["City_id"] = ids
print(df.head())
df.to_csv("data/votes_region_geojson.csv", index=False)

# extract centers of each region
dct_centers = {}
regions = df["Region"].unique()
for region in regions:
    df_in = df[df["Region"] == region]
    # geojson_show = geojson.copy()
    city_ids = df_in['City_id'].values
    features_in = [f for f in geojson['features'] if int(f['id']) in city_ids]
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
dct_centers["ALL"] = {'lon': lon_center, 'lat': lat_center}
#
with open('data/region_centers.pkl', 'wb') as pout:
    pickle.dump(dct_centers, pout)

# remove files
cmd = "rm data/chile_comunas_tmp.geojson"
os.system(cmd)




