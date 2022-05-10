import plotly.express as px
import pandas as pd
import json
import pickle
import re

#-------------------------- PREPROCESS DATA -------------------------------------#

# load dataframes of votes in comunas and regions
dct_votes = {}
for i, r in enumerate(['first','second']):
    
    df1 = pd.read_csv(f"data/votes_{r}_president_region_geojson.csv")
    df1_reg = df1[df1['City'] == 'total']
    df1 = df1[df1['City'] != 'total']
    # df2 = pd.read_csv('data/participacion_region_geojson.csv')
    df2 = pd.read_csv(f"data/votes_{r}_participation_region_geojson.csv")
    df2_reg = df2[df2['City'] == 'TOTAL']
    df2 = df2[df2['City'] != 'TOTAL']
    join_cols = {
        "Participa_mesas": "Participacion_mesas",
        "Participa_electors": "Participacion_electores",
        "Participa_votes": "Participacion_votos",
        "Participa_percentage": "Participacion_votos_%"
    }    
    df3 = df1.copy()
    df3 = df3.join(df2[[k for k, v in join_cols.items()]])
    df3 = df3.astype({
        'City_id': 'str',
        'City_with_id': 'str',
        'Region_id': 'str',
        'Region_with_id': 'str',
    })
    #
    # df = df[df['City'] != 'total']
    df3_reg = df1_reg.copy()
    df3_reg = df3_reg.join(df2_reg[[k for k, v in join_cols.items()]])
    df3_reg["City"].replace(to_replace={"total": "TODAS"}, inplace=True)
    df3_reg = df3_reg.astype({
        'City_id': 'str',
        'City_with_id': 'str',
        'Region_id': 'str',
        'Region_with_id': 'str',
    })
    
    dct_votes[i+1] = {
        'pres': df1,
        'pres_reg': df1_reg,
        'part': df2,
        'part_reg': df2_reg,    
        'all': df3,
        'all_reg': df3_reg,        
    }

# load geojson datasets of comunas and regions
with open('data/chile_comunas.geojson') as f:
    geojson_cities = json.load(f)

with open('data/chile_regions.geojson') as f:
    geojson_regions = json.load(f)

# with open('data/comunas_id.pkl', 'rb') as pin:
#     comunas_id = pickle.load(pin)

# load calculated geographical center of regions
with open('data/region_centers.pkl', 'rb') as pin:
    region_centers = pickle.load(pin)

# predefine zooms applied for region selection
region_zooms = {
    "DE ARICA Y PARINACOTA": 8,
    "DE TARAPACA": 7,
    "DE ANTOFAGASTA": 6,
    "DE ATACAMA": 6.5,
    "DE COQUIMBO": 7,
    "DE VALPARAISO": 7.5,
    "METROPOLITANA DE SANTIAGO": 7.5,
    "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS": 7.5,
    "DEL MAULE": 7,
    "DE ÑUBLE": 7.5,
    "DEL BIOBIO": 7,
    "DE LA ARAUCANIA": 7,
    "DE LOS RIOS": 7.5,
    "DE LOS LAGOS": 6.5,
    "DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO": 6,
    "DE MAGALLANES Y DE LA ANTARTICA CHILENA": 5.5,
    "ALL PER CITY": 3.5,
    "ALL PER REGION": 3.5,    
}

# define shortened names for regions
region_short = {
    "DE ARICA Y PARINACOTA": "ARICA",
    "DE TARAPACA": "TARAPACA",
    "DE ANTOFAGASTA": "ANTOFAGASTA",
    "DE ATACAMA": "ATACAMA",
    "DE COQUIMBO": "COQUIMBO",
    "DE VALPARAISO": "VALPARAISO",
    "METROPOLITANA DE SANTIAGO": "SANTIAGO",
    "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS": "O'HIGGINS",
    "DEL MAULE": "MAULE",
    "DE ÑUBLE": "ÑUBLE",
    "DEL BIOBIO": "BIOBIO",
    "DE LA ARAUCANIA": "LA ARAUCANIA",
    "DE LOS RIOS": "LOS RIOS",
    "DE LOS LAGOS": "LOS LAGOS",
    "DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO": "AYSEN",
    "DE MAGALLANES Y DE LA ANTARTICA CHILENA": "MAGALLANES",
}

dct_regions = {
    'region_centers': region_centers,
    'region_zooms': region_zooms,
    'region_short': region_short,
}

# options for category selection
dct_category = {}

for i in [1, 2]:
    options_category = [
        {'label': "CANDIDAT@ "+x.upper(), 'value':x}
        for x in dct_votes[i]['pres'].columns.values
        if x.find('Region') == -1
        if x.find('City') == -1
        if x.find('Votos') == -1
        if x.find('_per') == -1
    ]  
    options_category.extend([{'label': "CANDIDAT@ FORMULA", 'value': "Formula"}])
    options_category.extend([
        {'label': re.sub("_", " ", x.upper()), 'value':x}
        for x in dct_votes[i]['pres'].columns.values
        if x.find('_per') == -1
        if x.find('Votos') == 0
    ])
    options_category.extend(
        [{'label': re.sub("_", " ", v.upper()), 'value':k} for k, v in join_cols.items()]
    )
    #
    category_candidates = [d['value'] for d in options_category if "CANDIDAT" in d['label']]
    category_candidates.extend([d['value']+"_per" for d in options_category if "CANDIDAT" in d['label']])
    category_candidates = sorted(category_candidates)
    #
    category_report = [d['value'] for d in options_category if "Votos_" in d['value']]
    category_report.extend([d['value']+"_per" for d in options_category if "Votos_" in d['value']])
    category_report = sorted(category_report)
    #    
    category_participation = [d['value'] for d in options_category if "PARTICIPACION" in d['label']]
    #
    dct_category[i] = {
        'options_category': options_category,
        'category_candidates': category_candidates,
        'category_report': category_report,
        'category_participation': category_participation,
    }

# options for region selection
options_reg = [{'label': x, 'value':x} for x in dct_votes[1]['all']["Region"].unique()]
options_reg.extend([
    {'label': "TODAS POR CIUDAD", 'value': "ALL PER CITY"},
    {'label': "TODAS POR REGION", 'value': "ALL PER REGION"}    
])

# options for scaling data in map
options_scale_map = [
    {'label': "CATEGORIA REGION", 'value': "ABS_1"},
    {'label': "GLOBAL REGION", 'value': "ABS_2"},    
    {'label': "CATEGORIA PAIS", 'value': "ABS_3"},    
    {'label': "GLOBAL PAIS", 'value': "ABS_4"},        
    {'label': "CATEGORIA REGION %", 'value': "PER_1"},
    {'label': "GLOBAL REGION %", 'value': "PER_2"},
    {'label': "CATEGORIA PAIS %", 'value': "PER_3"},
    {'label': "GLOBAL PAIS %", 'value': "PER_4"}    
]

# options for scaling data in histogram
options_scale_hist = [
    {'label': "ABSOLUTO", 'value': "ABS"},
    {'label': "PORCENTAJE TODOS CANDIDAT@S", 'value': "PER"}
]

# options for colorscale
colorscales = px.colors.named_colorscales()
colorscales_r = [c+'_r' for c in colorscales]
colorscales.extend(colorscales_r)
colorscales = sorted(colorscales)

dct_options = {
    'options_reg': options_reg,
    'options_scale_map': options_scale_map,
    'options_scale_hist': options_scale_hist,
    'colorscales': colorscales,
}