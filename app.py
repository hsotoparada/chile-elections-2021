
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_auth
import plotly.express as px
import json
import pickle
import re

#-------------------------- PREPROCESS DATA -------------------------------------#

# load dataframes of votes in comunas and regions
df1 = pd.read_csv('data/votes_region_geojson.csv')
df1_reg = df1[df1['City'] == 'total']
df1 = df1[df1['City'] != 'total']
df2 = pd.read_csv('data/participacion_region_geojson.csv')
df2_reg = df2[df2['City'] == 'TOTAL']
df2 = df2[df2['City'] != 'TOTAL']
join_cols = {
    "Participa_mesas": "Participacion_mesas",
    "Participa_electors": "Participacion_electores",
    "Participa_votes": "Participacion_votos",
    "Participa_percentage": "Participacion_porcentaje"
}
df = df1.copy()
df = df.join(df2[[k for k, v in join_cols.items()]])
df = df.astype({
    'City_id': 'str',
    'City_with_id': 'str',
    'Region_id': 'str',
    'Region_with_id': 'str',
})
#
# df = df[df['City'] != 'total']
df_reg = df1_reg.copy()
df_reg = df_reg.join(df2_reg[[k for k, v in join_cols.items()]])
df_reg["City"].replace(to_replace={"total": "TODAS"}, inplace=True)
df_reg = df_reg.astype({
    'City_id': 'str',
    'City_with_id': 'str',
    'Region_id': 'str',
    'Region_with_id': 'str',
})

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

# options for category selection
options_category = [
    {'label': "CANDIDAT@ "+x.upper(), 'value':x}
    for x in df1.columns[2:-4].values
    if "_per" not in x and "Votos" not in x
]
options_category.extend([{'label': "CANDIDAT@ FORMULA", 'value': "Formula"}])
options_category.extend([
    {'label': re.sub("_", " ", x.upper()), 'value':x}
    for x in df1.columns[2:-4].values
    if "_per" not in x and "Votos" in x
])
options_category.extend(
    [{'label': re.sub("_", " ", v.upper()), 'value':k} for k, v in join_cols.items()]
)
#
category_candidates = [d['value'] for d in options_category if "CANDIDAT" in d['label']]
category_candidates.extend([d['value']+"_per" for d in options_category if "CANDIDAT" in d['label']])
category_candidates = sorted(category_candidates)
category_report = [d['value'] for d in options_category if "Votos_" in d['value']]
category_report.extend([d['value']+"_per" for d in options_category if "Votos_" in d['value']])
category_report = sorted(category_report)    
category_participation = [d['value'] for d in options_category if "PARTICIPACION" in d['label']]

# options for region selection
options_reg = [{'label': x, 'value':x} for x in df["Region"].unique()]
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
    {'label': "% CATEGORIA REGION", 'value': "PER_1"},
    {'label': "% GLOBAL REGION", 'value': "PER_2"},
    {'label': "% CATEGORIA PAIS", 'value': "PER_3"},
    {'label': "% GLOBAL PAIS", 'value': "PER_4"}    
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

#---------------------------- DASH LAYOUT -------------------------------------#

# Create a dash application (dash)
# app = dash.Dash(__name__)
# app = dash.Dash(external_stylesheets = [dbc.themes.BOOTSTRAP])
# app = dash.Dash(external_stylesheets = [dbc.themes.DARKLY])
app = dash.Dash(external_stylesheets = [dbc.themes.SANDSTONE])
server = app.server

auth = dash_auth.BasicAuth(
    app,
    {"eleccion": "chile"}
)

header_1 = html.Div(
    [   
        html.Div(
            dcc.Markdown('''
                ### **Elección Presidencial Chile 2021**  
                ---  
                **Fuente**: Elaboración propia en base a datos del [servel](https://www.servelelecciones.cl/)
                
                **Author**: Hugo Soto. Data Scientist | PhD Freie Universität Berlin
                
                **Contacto**: hugosotoparada@gmail.com
                
                [*Github*](https://github.com/hsotoparada/Chile-Elections)  
            ''', style={"white-space": "pre"})
        ),                
    ]
)

header_2 = html.Div(
    dbc.Card([
        dcc.Markdown('''
            **Instrucciones**: Seleccionar **CATEGORIA VOTOS**, **REGION**, **ESCALA** y **PALETA** en cada menú desplegable.
            Un mapa y gráfico interactivos se actualizarán en base cada una de las
            dos posibles selecciones.
            **CATEGORIA VOTOS** puede ser votos de un candidato o datos de participación.
            **CATEGORIA VOTOS = FORMULA** permite ingresar una FORMULA 
            como suma (+) o resta (-) entre votos de uno o más candidatos,
            o multiplicación (x) de votos por un factor numérico.
            En **FORMULA**, candidatos deben ser representados por:
            BO, KA, PR, SI, EN, PA, AR (o bo, ka, etc.), correspondiente a las primeras
            letras en los apellidos de los candidatos.
            Por ejemplo, la combinación de votos de Boric más 50% de Parisi puede calcularse ingresando
            la **FORMULA**: bo + 0.5xpa.
            **REGION** es una región en el país o todas las regiones, desagregadas por región o ciudad.
            **ESCALA** es el rango en que los datos se muestran, sin alterar su valor.
            **ESCALA** puede ser absoluta (sin %) o en porcentaje (con %) para distintos niveles.
            En niveles *CATEGORIA* y *GLOBAL* votos de candidatos se muestran en el rango del candidato
            y de todos los candidatos, respectivamente, opcionalmente dentro de la *REGION*
            seleccionada o a nivel *PAIS*.
            Mismos niveles también se aplican entre *VOTOS NULOS*, *BLANCOS*, *EMITIDOS y TOTAL*.
            Para categorías **FORMULA** y **PARTICIPACION** *MESAS*, *ELECTORES*, *VOTOS* y *PORCENTAJE*
            sólo son válidos niveles *CATEGORIA REGION/PAIS*.
            La visualización de los datos puede mejorar cambiando la **PALETA** seleccionada
            por defecto a alguna otra de la lista disponible.
        ''')],        
    body=True,            
    ),     
),

controls_1_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_category_map_1',
                    options=options_category,
                    placeholder='CATEGORIA VOTOS',
                    # placeholder='Candidato/a',                    
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),  
                dbc.Tooltip(
                    'Ingresar categoría a mostrar en primer mapa/gráfico.',
                    target="select_category_map_1",
                ),                      
            ],
        body=True,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_formula_map_1',
                    type="text",
                    placeholder="FORMULA",
                    debounce=True,
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ), 
                dbc.Tooltip(
                    "Ingresar fórmula a aplicar (si CATEGORIA = FORMULA) en primer mapa/gráfico.",
                    target="input_formula_map_1",
                ),                
            ],
        body=True,            
        ),         
    ],
)

controls_1_2 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_region_map_1',
                    options=options_reg,
                    placeholder='REGION',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar región del país en primer mapa/gráfico.",
                    target="select_region_map_1",
                ),                                
            ],
        body=True,            
        ),
    ],
)

controls_1_3 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='colorscale_map_1',
                    options=[{"value": x, "label": x} for x in colorscales],
                    placeholder='PALETA',
                    value="hot_r"
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar paleta de colores en primer mapa/gráfico.",
                    target="colorscale_map_1",
                ),                   
            ],
        body=True,            
        ),      
    ],
)

controls_1_4 = dbc.CardGroup(
    [ 
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_scale_map_1',
                    options=options_scale_map,
                    placeholder='ESCALA',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar escala de datos en primer mapa/gráfico.",
                    target="select_scale_map_1",
                ),                  
            ],
        body=True,            
        )               
    ],
)


controls_2_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_category_map_2',
                    options=options_category,
                    placeholder='CATEGORIA VOTOS',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),          
                dbc.Tooltip(
                    'Ingresar categoría a mostrar en segundo mapa/gráfico.',
                    target="select_category_map_2",
                ),                                 
            ],
        body=True,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_formula_map_2',
                    type="text",
                    placeholder="FORMULA",
                    debounce=True,
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),               
                dbc.Tooltip(
                    "Ingresar fórmula a aplicar (si CATEGORIA = FORMULA) en segundo mapa/gráfico.",
                    target="input_formula_map_2",
                ),                    
            ],
        body=True,            
        ),         
    ],
)

controls_2_2 = dbc.CardGroup(
    [
        dbc.Card(
            [        
                dcc.Dropdown(
                    id='select_region_map_2',
                    options=options_reg,
                    placeholder='REGION',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar región del país en segundo mapa/gráfico.",
                    target="select_region_map_2",
                ),                 
            ],
        body=True,            
        ),
    ],
)

controls_2_3 = dbc.CardGroup(
    [       
        dbc.Card(
            [
                dcc.Dropdown(
                    id='colorscale_map_2',
                    options=[{"value": x, "label": x} for x in colorscales],
                    placeholder='PALETA',
                    value="hot_r"
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar paleta de colores en segundo mapa/gráfico.",
                    target="colorscale_map_2",
                ),                
            ],
        body=True,            
        ),         
    ],
)

controls_2_4 = dbc.CardGroup(
    [       
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_scale_map_2',
                    options=options_scale_map,
                    placeholder='ESCALA',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar escala de datos en segundo mapa/gráfico.",
                    target="select_scale_map_2",
                ),                     
            ],
        body=True,            
        ),         
    ],
)

# TODO: remove
controls_3_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
               dcc.Dropdown(
                   id='select_category_hist_1',
                   options=options_category,
                   placeholder='CATEGORIA VOTOS',
                   # value="Kast"
                   # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
               ),
                dbc.Tooltip(
                    "Ingresar tipo de votos (candidato/a, blancos o nulos, fórmula, etc.) para actualizar figura superior.",
                    target="select_category_hist_1",
                ),                
            ],
        body=True,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_formula_hist_1',
                    type="text",
                    placeholder="FORMULA",
                    debounce=True,
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar fórmula a aplicar (si VOTOS = FORMULA) para actualizar figura superior.",
                    target="input_formula_hist_1",
                ),                
            ],
        body=True,            
        ),         
    ],
)

controls_3_2 = dbc.CardGroup(
    [
        dbc.Card(
            [
               dcc.Dropdown(
                   id='select_category_hist_2',
                   options=options_category,
                   placeholder='VOTOS',
                   # value="Kast"
                   # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
               ),
                dbc.Tooltip(
                    "Ingresar tipo de votos (candidato/a, blancos o nulos, fórmula, etc.) para actualizar figura inferior.",
                    target="select_category_hist_2",
                ),               
            ],
        body=True,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_formula_hist_2',
                    type="text",
                    placeholder="FORMULA",
                    debounce=True,
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar fórmula a aplicar (si VOTOS = FORMULA) para actualizar figura inferior.",
                    target="input_formula_hist_2",
                ),                   
            ],
        body=True,            
        ),         
    ],
)

controls_3_3 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_region_hist',
                    options=options_reg,
                    placeholder='REGION',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar región del país en que los datos serán mostrados.",
                    target="select_region_hist",
                ),                 
            ],
        body=True,            
        ),        
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_scale_hist',
                    options=options_scale_hist,
                    placeholder='ESCALA',
                    # value="ABS"
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar escala en que los datos serán mostrados.",
                    target="select_scale_hist",
                ),                 
            ],
        body=True,            
        ),         
    ],
)

fig_1 = html.Div(
    [
        dcc.Graph(
            id="map_1",
            style={'height': '70vh'}
            # style={'display': 'block', 'width': '60vh', 'height': '80vh'}
        ),
        dbc.Tooltip(
            "Primer mapa",
            target="map_1",
            placement="top-end"            
        ),
    ]    
),

fig_2 = html.Div(
    [
        dcc.Graph(
            id="map_2",
            style={'height': '70vh'}
        ),
        dbc.Tooltip(
            "Segundo mapa",
            target="map_2",
            placement="top-end"
        ),     
    ]
),

fig_hist = html.Div([
    html.Div(
    dcc.Graph(id="hist_1",style={'height': '40vh'})
    ),
    dbc.Tooltip(
        "Primera figura",
        target="hist_1",
        placement="top-end"            
    ),    
    html.Div(
    dcc.Graph(id="hist_2",style={'height': '40vh'})
    ),
    dbc.Tooltip(
        "Segunda figura",
        target="hist_2",
        placement="top-end"            
    ),    
]),


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(header_1, width=3, sm=3, md=3, lg=3, xl=3),
                dbc.Col(header_2, width=9, sm=9, md=9, lg=9, xl=9),
            ],
            align="start",
        ),        
        html.Hr(),        
        dbc.Row(
            [
                dbc.Col(controls_1_1, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(controls_1_2, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(controls_1_3, width=1, sm=1, md=1, lg=1, xl=1),
                dbc.Col(controls_1_4, width=3, sm=3, md=3, lg=3, xl=3)                
                # dbc.Col(controls_3_1, width=4)
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(controls_2_1, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(controls_2_2, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(controls_2_3, width=1, sm=1, md=1, lg=1, xl=1),
                dbc.Col(controls_2_4, width=3, sm=3, md=3, lg=3, xl=3)                
                # dbc.Col(controls_3_2, width=4),               
            ],
            align="start",
        ),        
        # dbc.Row(
        #     [
        #         dbc.Col(controls_1_3, width={"size": 4}),
        #         dbc.Col(controls_2_3, width={"size": 4}),                               
        #         # dbc.Col(controls_3_3, width={"size": 4}),               
        #     ],
        #     align="start",
        # ),        
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(fig_1, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(fig_2, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(fig_hist, width=4, sm=4, md=4, lg=4, xl=4)
            ],
            align="start",
        ),
    ],
    fluid=True,
)



#-------------------------- DASH INTERACTIVITY -------------------------------#

# callback decorator
@app.callback(
    Output("map_1", "figure"),
    Output("hist_1", "figure"),
    Input("select_category_map_1", "value"),
    Input("select_region_map_1", "value"),
    Input("select_scale_map_1", "value"),
    Input("input_formula_map_1", "value"),
    Input("colorscale_map_1", "value")
)
def update_fig_1(category, region, scale, formula, colorscale):
    #
    raise_exceptions(category, region, scale, formula, colorscale)            
    df_in = filter_dataframe(region)    
    geojson = filter_geojson(df_in, region)
    fig_map = create_map(df_in, geojson, category, region, scale, formula, colorscale)
    fig_bar = create_histogram(df_in, scale, formula, category, region, colorscale)        
    return [fig_map, fig_bar]

# callback decorator
@app.callback(
    Output("map_2", "figure"),
    Output("hist_2", "figure"),    
    Input("select_category_map_2", "value"),
    Input("select_region_map_2", "value"),
    Input("select_scale_map_2", "value"),
    Input("input_formula_map_2", "value"),
    Input("colorscale_map_2", "value")
)
def update_fig_2(category, region, scale, formula, colorscale):
    #
    raise_exceptions(category, region, scale, formula, colorscale)            
    df_in = filter_dataframe(region)    
    geojson = filter_geojson(df_in, region)
    fig_map = create_map(df_in, geojson, category, region, scale, formula, colorscale)
    fig_bar = create_histogram(df_in, scale, formula, category, region, colorscale)        
    return [fig_map, fig_bar]
    
def raise_exceptions(category, region, scale, formula, colorscale):
    print(f"input --> {category}, {region}, {scale}, {formula}, {colorscale}")    
    if region is None:
        raise dash.exceptions.PreventUpdate
    if scale is None:
        raise dash.exceptions.PreventUpdate
    if category is None:
        raise dash.exceptions.PreventUpdate
    if category == "Formula":
        if formula is None:
            raise dash.exceptions.PreventUpdate
        # if scale in ["ABS_3","ABS_4","PER_3","PER_4"]:
        if scale in ["ABS_2", "ABS_4","PER_2","PER_4"]:            
            raise dash.exceptions.PreventUpdate        
    if category in category_participation:
        # if scale in ["ABS_2","ABS_4"] or "PER" in scale:
        if "PER" in scale:            
            raise dash.exceptions.PreventUpdate
        if scale in ["ABS_2","ABS_4"]:            
            raise dash.exceptions.PreventUpdate            

def filter_dataframe(region):    
    # filter by region
    if region == "ALL PER REGION":
        df_in = df_reg.copy()
    else:
        df_in = df.copy()
        if region != "ALL PER CITY":
            df_in = df_in[df_in['Region'] == region]
    # df_in = df_in[df_in['City'] != 'total']
    df_in.reset_index(drop=True, inplace=True)
    # df_in = df_in.iloc[:2, :]
    # df_in = df_in.astype({'City_with_id': 'str', 'City_id': 'str'})
    print(df_in.head(10))
    print(df.shape)
    print(df_in.shape)
    # print(df_in.dtypes)
    return df_in    

def filter_geojson(df_in, region):   
    # filter geojson
    if region == "ALL PER REGION":
        geojson_show = geojson_regions.copy()
        geojon_ids = df_in['Region_id'].values
        features_show = [f for f in geojson_regions['features'] if f['id'] in geojon_ids]
        geojson_show['features'] = features_show         
    else:
        geojson_show = geojson_cities.copy()
        geojon_ids = df_in['City_id'].values
        features_show = [f for f in geojson_cities['features'] if f['id'] in geojon_ids]
        geojson_show['features'] = features_show 
    # print(geojson_show)
    # for f in geojson_show['features']:
    #     # print(f)
    #     # print(f['id'], f['properties'])
    #     print(f['id'])     
    return geojson_show

def get_plot_columns(df_in, category, scale, data_column):
    if scale in ["ABS_1", "ABS_3", "PER_1", "PER_3"]: # category scale
        cols = data_column
    elif scale in ["ABS_2", "ABS_4"]: # common category scale
        if category in category_candidates:
            cols = [c for c in df_in.columns if c in category_candidates and"_per" not in c ]                        
        elif category in category_report:
            cols = [c for c in df_in.columns if c in category_report and "_per" not in c] 
        elif category in category_participation:
            cols = data_column
    elif scale in ["PER_2", "PER_4"]: # common category scale
        if category in category_candidates:
            cols = [c for c in df_in.columns if c in category_candidates and"_per" in c ]                                    
        elif category in category_report:
            cols = [c for c in df_in.columns if c in category_report and "_per" in c]
    return cols

def get_plot_range(df_in, category, region, scale, cols):
    if scale in ["ABS_1", "PER_1"]:        
        range_max = df_in[cols].max()
    elif scale in ["ABS_3", "PER_3"]:
        if category in category_participation:
            if region == "ALL PER REGION":
                range_max = df2_reg[cols].max()
            else:
                range_max = df2[cols].max()
        else:
            if region == "ALL PER REGION":
                range_max = df1_reg[cols].max()
            else:            
                range_max = df1[cols].max()        
    elif scale in ["ABS_2", "PER_2"]:
        if category in category_participation:
            range_max = df_in[cols].max()
        else:
            range_max = df_in[cols].max().max()
    elif scale in ["ABS_4", "PER_4"]:
        if category in category_participation:
            if region == "ALL PER REGION":
                range_max = df2_reg[cols].max()
            else:            
                range_max = df2[cols].max()
        else:
            if region == "ALL PER REGION":
                range_max = df1_reg[cols].max().max()
            else:            
                range_max = df1[cols].max().max()   
    return [0, range_max]

def create_map(df_in, geojson, category, region, scale, formula, colorscale):
    """
    Create map...
    """
    # print(category, scale)
    if category == "Formula":
        df_in["Formula"], df_in["Formula_per"], formula_label = evaluate_formula(df_in, formula)
        # df_in.rename({"Formula": data_text, "Formula_per": f"{data_text}_per"}, axis='columns')
        data_column = "Formula"
        # data_text = data_column
        data_label = formula_label
    else:
        data_column = category
        # data_text = category
        if category in category_candidates:
            data_label = [o['label'].split(None)[-1] for o in options_category if o['value'] == category][0]            
        if category in category_report:
            data_label = [o['label'] for o in options_category if o['value'] == category][0]
        if category in category_participation:
            data_label = [o['label'] for o in options_category if o['value'] == category][0]            
    #
    # data_column = category
    if "ABS" in scale:
        pass
    if "PER" in scale:
        data_column += "_per"
    #
    labels={data_column: data_label}    
    #
    cols = get_plot_columns(df_in, category, scale, data_column)
    range_color = get_plot_range(df_in, category, region, scale, cols)
    print(range_color)
    #
    map_center = region_centers[region]
    map_zoom = region_zooms[region]
    if region == "ALL PER REGION":
        locations = "Region_id"
        hover_data = ["Region"]
    else:
        locations="City_id"
        hover_data = ["Region", "City"]
    #
    fig = px.choropleth_mapbox(
        df_in,
        geojson=geojson,
        # color=category,
        color=data_column,
        # color="Boric",
        color_continuous_scale=colorscale,
        range_color=range_color,   
        labels=labels,
        # locations="City",
        locations=locations,
        # locations="City_with_id",
        # featureidkey="properties.comuna",
        # featureidkey="properties.Comuna",
        featureidkey="id",
        mapbox_style="carto-positron",
        # mapbox_style="open-street-map",
        opacity=0.8,
        center=map_center,
        zoom=map_zoom,
        # range_color=[0, df_in["Boric"].max()],
        # range_color=[0, df_in[category].max()],
        hover_data=hover_data,
        # title=data_label
    )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        # coloraxis_showscale=False
        coloraxis_colorbar={'title':""}        
    )
    #
    # add annotation
    fig.add_annotation(
        text=f"<b>{data_label}</b>",
        xref="paper",
        yref="paper",
        x=0.,
        y=1.,
        showarrow=False,
        font=dict(color='black',size=22),
        # bordercolor="#c7c7c7",
        # borderwidth=2,
        # borderpad=4,
        bgcolor="lightgray",        
    )  
    return fig

def create_histogram(df_in, scale, formula, category, region, colorscale):
    """
    Create histogram...
    """
    # print(formula, category)
    #
    if category == "Formula":
        df_in["Formula"], df_in["Formula_per"], formula_label = evaluate_formula(df_in, formula)
        # df_in.rename({"Formula": data_text, "Formula_per": f"{data_text}_per"}, axis='columns')
        df1["Formula"], df1["Formula_per"], formula_label = evaluate_formula(df1, formula)
        df1_reg["Formula"], df1_reg["Formula_per"], formula_label = evaluate_formula(df1_reg, formula)        
        data_column = "Formula"
        data_text = data_column
        # data_column = data_text
        data_label = formula_label
    else:
        data_column = category
        data_text = category
        # data_label = category  
        if category in category_candidates:
            data_label = [o['label'].split(None)[-1] for o in options_category if o['value'] == category][0]            
        if category in category_report:
            data_label = [o['label'] for o in options_category if o['value'] == category][0]
        if category in category_participation:
            data_label = [o['label'] for o in options_category if o['value'] == category][0]          
    #
    if "ABS" in scale:
        pass
    if "PER" in scale:
        data_column += "_per"
        data_text += "_per"
        # data_label += "_per"         
    #
    labels={data_column: data_label}
    # 
    cols = get_plot_columns(df_in, category, scale, data_column)
    range_data = get_plot_range(df_in, category, region, scale, cols)
    #
    # print(df_in)
    # df_in = df.copy() # TODO: needed ??
    print(df_in.columns.values)    
    if region == "ALL PER REGION":
        x = "Region"
        hover_data=["Region"]
    else:
        x = "City"
        hover_data=["Region", "City"]    
    #
    df_in["Region"].replace(to_replace=region_short, inplace=True)  
    fig = px.bar(
        df_in,
        y=data_column,
        x=x,
        text=data_text,
        labels=labels,
        color=data_column,      
        color_continuous_scale=colorscale, 
        range_color=range_data,
        hover_data=hover_data
        )    
    fig.update_layout(
        # margin={"r":0,"t":0,"l":0,"b":0},
        margin={"t":0,"l":0},
        xaxis={'visible': True, 'showticklabels': True, 'title': ""},
        yaxis={'visible': True, 'showticklabels': True, 'title': "", 'range': range_data},
        coloraxis_showscale=False
        # coloraxis_colorbar={'title':"", 'xpad':0, 'thickness':5},
    )    
    #
    # add annotation
    # if category in category_participation or category in category_report:
    #     annotate_label = [o['label'] for o in options_category if o['value'] == category][0]
    # else:
    #     annotate_label = re.sub("_per", "", data_label)
    fig.add_annotation(
        text=f"<b>{data_label}</b>",
        xref="paper",
        yref="paper",
        x=1.05,
        y=0.5,
        textangle=90,
        showarrow=False,
        font=dict(color='black',size=16),
        # bordercolor="#c7c7c7",
        # borderwidth=2,
        # borderpad=4,
        bgcolor="white",        
    )      
    return fig


def evaluate_formula(df, eq):
    """
    Create histogram...
    """
    dct_input = {
        'bo': 'Boric',
        'ka': 'Kast',
        'pr': 'Provoste',
        'si': 'Sichel',
        'ar': 'Artes',
        'en': 'Enriquez',
        'pa': 'Parisi',
        've': 'Votos_Emitidos',
        'vn': 'Votos_Nulos',
        'vb': 'Votos_Blancos',
        'vt': 'Votos_Total',
    }
    #
    # keep only +,- and letters in input equation
    eq = re.sub("[^a-zA-Z+-x]", "", eq)
    #
    # replace candidates
    eq_per = eq
    eq_label = eq
    for k, v in dct_input.items():
        if k in eq:
            eq = eq.replace(k, f"df['{v}']")
            eq_per = eq_per.replace(k, f"df['{v}_per']")
            eq_label = eq_label.replace(k, v)
    #
    # replace multiplication
    eq = eq.replace('x', '*')
    eq_per = eq_per.replace('x', '*')
    # eq_label = eq_label.replace('x', '*')
    print(eq)
    print(eq_label)
    # print(eq_per)
    return eval(eq), eval(eq_per), eq_label


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False)
    # app.run_server(host='0.0.0.0', port=8050, debug=True)
    # app.run_server(host='0.0.0.0', port=80, debug=True)


