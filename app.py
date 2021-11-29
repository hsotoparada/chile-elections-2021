
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

# TODO: add normalization options (by max number of voters, total votes in comuna, etc)...DONE
# TODO: add second map for comparison...DONE
# TODO: add histogram showing votes per candidate and comuna (all entire region)...DONE
# TODO: correct center coords of Valparaiso...DONE
# TODO: add missing city ids...DONE
# TODO: add functionality to accept input formula in dropdown menus...DONE
# TODO: add signature (github) to Dash...DONE
# TODO: maps -> check escala = porcentaje candidato
# TODO: histogs -> if ABS remove total bar, add annotation showing total votes...DONE
# TODO: update histogs with same info as maps...DONE
# TODO: add reverse colorscales...DONE
# TODO: update scale of histogs when FORMULA is selected ??
# TODO: add ABSOLUTO_CANDIDATO a opciones de escala
# TODO: add data of participation
# TODO: deploy to AWS, Heroku, etc

# Load votes dataframe and geojson containing regions
df = pd.read_csv('data/votes_region_geojson.csv')
with open('data/chile_comunas.geojson') as f:
    geojson_chile = json.load(f)

with open('data/comunas_id.pkl', 'rb') as pin:
    comunas_id = pickle.load(pin)

with open('data/region_centers.pkl', 'rb') as pin:
    region_centers = pickle.load(pin)

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
    "ALL": 3.5,
}

# options for candidate selection
options_candidate = [{'label': x.upper(), 'value':x} for x in df.columns[2:-2].values if "_per" not in x]
options_candidate.extend([{'label': "FORMULA", 'value': "FORMULA"}])

# options for region selection
options_reg = [{'label': x, 'value':x} for x in df["Region"].unique()]
options_reg.extend([{'label': "ALL", 'value': "ALL"}])

# options for scaling data in map
options_scale_map = [
    {'label': "ABSOLUTO", 'value': "ABS"},
    {'label': "PORCENTAJE_CANDIDATO", 'value': "PER_1"},
    {'label': "PORCENTAJE_COMUN", 'value': "PER_2"}
]

# options for scaling data in histogram
options_scale_hist = [
    {'label': "ABSOLUTO", 'value': "ABS"},
    {'label': "PORCENTAJE_COMUN", 'value': "PER"}
]

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
    {"chile-elections": "seguimos"}
)

header_1 = html.Div(
    [
        html.Div(
            html.H1("Elecciones Presidenciales Chile 2021")
        ),
        html.Div(
            # html.H5("Repositorio: ")
            html.A("github repo", href='https://github.com/hsotoparada/Chile-Elections', target="_blank")            
        ),        
        # html.A("repository", href='https://github.com/hsotoparada/Chile-Elections', target="_blank"),        
        
    ]
)

header_2 = html.Div(
    dbc.Card([
        html.H5(
            "Instrucciones: Seleccionar CANDIDATO/A, REGION y ESCALA en cada menú desplegable. "
            "Las figuras interactivas (mapa e histograma) se actualizarán en base a la selección "
            "o la FORMULA aplicada, en caso que la opción VOTOS = FORMULA sea seleccionada. "
            "FORMULA puede ser suma o resta entre uno o más candidatos, representados por: "
            "BO, KA, PR, SI, EN, PA, AR (o bo, ka, etc.) "
            "correspondiente a Boric, Kast, Provoste, Sichel, Enriquez, Parisi, and Artés, respectivamente. "
            "Por ejemplo, para restar votos de Boric y Kast ingresar FORMULA: bo - ka. "
        )],
    body=True,            
    ),     
),

controls_1_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_candidate_map_1',
                    options=options_candidate,
                    placeholder='VOTOS',
                    # placeholder='Candidato/a',                    
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),  
                dbc.Tooltip(
                    "Ingresar tipo de votos (candidato/a, blancos o nulos, fórmula, etc.) para actualizar primer mapa/figura.",
                    target="select_candidate_map_1",
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
                    "Ingresar fórmula a aplicar (si VOTOS = FORMULA) para actualizar primer mapa/figura.",
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
                    id='select_scale_map_1',
                    options=options_scale_map,
                    placeholder='ESCALA',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar escala en que los datos serán mostrados en primer mapa/figura.",
                    target="select_scale_map_1",
                ),                  
            ],
        body=True,            
        ),         
        dbc.Card(
            [
                dcc.Dropdown(
                    id='colorscale_map_1',
                    options=[{"value": x, "label": x} for x in colorscales],
                    placeholder='PALETA',
                    value="viridis"
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar paleta de colores en que los datos serán mostrados en primer mapa.",
                    target="colorscale_map_1",
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
                    id='select_region_map_1',
                    options=options_reg,
                    placeholder='REGION',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar región del país en que los datos serán mostrados en primer mapa/figura.",
                    target="select_region_map_1",
                ),                                
            ],
        body=True,            
        ),
    ],
)

controls_2_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_candidate_map_2',
                    options=options_candidate,
                    placeholder='VOTOS',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),          
                dbc.Tooltip(
                    "Ingresar tipo de votos (candidato/a, blancos o nulos, fórmula, etc.) para actualizar segundo mapa/figura.",
                    target="select_candidate_map_2",
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
                    "Ingresar fórmula a aplicar (si VOTOS = FORMULA) para actualizar segundo mapa/figura.",
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
                    id='select_scale_map_2',
                    options=options_scale_map,
                    placeholder='ESCALA',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar escala en que los datos serán mostrados en segundo mapa/figura.",
                    target="select_scale_map_2",
                ),                     
            ],
        body=True,            
        ),        
        dbc.Card(
            [
                dcc.Dropdown(
                    id='colorscale_map_2',
                    options=[{"value": x, "label": x} for x in colorscales],
                    placeholder='PALETA',
                    value="viridis"
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar paleta de colores en que los datos serán mostrados en segundo mapa.",
                    target="colorscale_map_2",
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
                    id='select_region_map_2',
                    options=options_reg,
                    placeholder='REGION',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),
                dbc.Tooltip(
                    "Ingresar región del país en que los datos serán mostrados en segundo mapa/figura.",
                    target="select_region_map_2",
                ),                 
            ],
        body=True,            
        ),
    ],
)

controls_3_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
               dcc.Dropdown(
                   id='select_candidate_hist_1',
                   options=options_candidate,
                   placeholder='VOTOS',
                   # value="Kast"
                   # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
               ),
                dbc.Tooltip(
                    "Ingresar tipo de votos (candidato/a, blancos o nulos, fórmula, etc.) para actualizar figura superior.",
                    target="select_candidate_hist_1",
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
                   id='select_candidate_hist_2',
                   options=options_candidate,
                   placeholder='VOTOS',
                   # value="Kast"
                   # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
               ),
                dbc.Tooltip(
                    "Ingresar tipo de votos (candidato/a, blancos o nulos, fórmula, etc.) para actualizar figura inferior.",
                    target="select_candidate_hist_2",
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
    dcc.Graph(
        id="map_1",
        style={'height': '70vh'}
        # style={'display': 'block', 'width': '60vh', 'height': '80vh'}
    )
),

fig_2 = html.Div(
    dcc.Graph(
        id="map_2",
        style={'height': '70vh'}
    )
),

fig_hist = html.Div([
    html.Div(
    dcc.Graph(id="hist_1",style={'height': '40vh'})
    ),
    html.Div(
    dcc.Graph(id="hist_2",style={'height': '40vh'})
    ),
]),


app.layout = dbc.Container(
    [
        # html.H1("Elecciones Presidenciales Chile 2021"),
        # html.A("repository", href='https://github.com/hsotoparada/Chile-Elections', target="_blank"),        
        # html.Hr(),
        dbc.Row(
            [
                dbc.Col(header_1, width=3),
                dbc.Col(header_2, width=9),
            ],
            align="start",
        ),        
        html.Hr(),        
        dbc.Row(
            [
                dbc.Col(controls_1_1, width=4),
                dbc.Col(controls_1_2, width=4),
                dbc.Col(controls_1_3, width={"size": 4})
                # dbc.Col(controls_3_1, width=4)
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(controls_2_1, width=4),
                dbc.Col(controls_2_2, width=4),
                dbc.Col(controls_2_3, width={"size": 4})
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
                dbc.Col(fig_1, width=4),
                dbc.Col(fig_2, width=4),
                dbc.Col(fig_hist, width=4)
            ],
            align="start",
        ),
    ],
    fluid=True,
)



#-------------------------- DASH INTERACTIVITY -------------------------------#

# add callback decorator
@app.callback(
    Output("map_1", "figure"),
    Output("hist_1", "figure"),
    Input("select_candidate_map_1", "value"),
    Input("select_region_map_1", "value"),
    Input("select_scale_map_1", "value"),
    Input("input_formula_map_1", "value"),
    Input("colorscale_map_1", "value")
)
def update_fig_1(candidate, region, scale, eq, colorscale):
    df_in = df.copy()
    #
    if region is None:
        raise dash.exceptions.PreventUpdate
    if scale is None:
        raise dash.exceptions.PreventUpdate
    if candidate is None:
        raise dash.exceptions.PreventUpdate
    if candidate == "FORMULA" and eq is None:
        raise dash.exceptions.PreventUpdate        
    #
    # filter by region
    # df_in = df_in[df_in['Region'] == 'DE ANTOFAGASTA']
    # df_in = df_in[df_in['Region'] == 'METROPOLITANA DE SANTIAGO']
    if region != "ALL":
        df_in = df_in[df_in['Region'] == region]
    df_in = df_in[df_in['City'] != 'total']
    df_in.reset_index(drop=True, inplace=True)
    # df_in = df_in.iloc[:2, :]
    df_in = df_in.astype({'City_with_id': 'str', 'City_id': 'str'})
    print(df_in.head(20))
    print(df.shape)
    print(df_in.shape)
    # print(df_in.dtypes)
    #
    # filter geojson
    geojson_show = geojson_chile.copy()
    city_ids = df_in['City_id'].values
    features_show = [f for f in geojson_chile['features'] if f['id'] in city_ids]
    geojson_show['features'] = features_show
    #
    # print(geojson_show)
    # for f in geojson_show['features']:
    #     # print(f)
    #     # print(f['id'], f['properties'])
    #     print(f['id']) 
    #
    print(f"input --> {candidate}, {region}, {scale}, {eq}, {colorscale}")
    # print(df_in.dtypes)
    #
    fig_map = create_map(df_in, geojson_show, candidate, region, scale, eq, colorscale)
    fig_bar = create_histogram(df_in, scale, eq, candidate, colorscale)        
    return [fig_map, fig_bar]

# add callback decorator
@app.callback(
    Output("map_2", "figure"),
    Output("hist_2", "figure"),    
    Input("select_candidate_map_2", "value"),
    Input("select_region_map_2", "value"),
    Input("select_scale_map_2", "value"),
    Input("input_formula_map_2", "value"),
    Input("colorscale_map_2", "value")
)
def update_fig_2(candidate, region, scale, eq, colorscale):
    df_in = df.copy()
    #
    if region is None:
        raise dash.exceptions.PreventUpdate
    if scale is None:
        raise dash.exceptions.PreventUpdate
    if candidate is None:
        raise dash.exceptions.PreventUpdate
    if candidate == "FORMULA" and eq is None:
        raise dash.exceptions.PreventUpdate 
    #
    # filter by region
    if region != "ALL":
        df_in = df_in[df_in['Region'] == region]
    df_in = df_in[df_in['City'] != 'total']
    df_in.reset_index(drop=True, inplace=True)
    df_in = df_in.astype({'City_with_id': 'str', 'City_id': 'str'})
    print(df_in.head(20))
    print(df.shape)
    print(df_in.shape)
    # print(df_in.dtypes)
    #
    # filter geojson
    geojson_show = geojson_chile.copy()
    city_ids = df_in['City_id'].values
    features_show = [f for f in geojson_chile['features'] if f['id'] in city_ids]
    geojson_show['features'] = features_show
    #
    # for f in geojson_show['features']:
    #     # print(f)
    #     # print(f['id'], f['properties'])
    #     print(f['id'])        
    #
    fig_map = create_map(df_in, geojson_show, candidate, region, scale, eq, colorscale)
    fig_bar = create_histogram(df_in, scale, eq, candidate, colorscale)            
    return [fig_map, fig_bar]

def create_map(df, geojson, candidate, region, scale, eq, colorscale):
    """
    Create map...
    """
    print(candidate, scale)
    #
    if candidate == "FORMULA":
        df["Formula"], df["Formula_per"], eq_label = evaluate_equation(df, eq)
        # df.rename({"Formula": data_text, "Formula_per": f"{data_text}_per"}, axis='columns')
        data_column = "Formula"
        # data_text = data_column
        data_label = eq_label
    else:
        data_column = candidate
        # data_text = candidate
        data_label = candidate                
    #
    # data_column = candidate
    if scale == "ABS":
        pass
    if scale in ["PER_1", "PER_2"]:
        data_column += "_per"
    #
    # TODO: create two scaling -> 1) per candidate. 2) common values among candidates
    if scale in ["ABS", "PER_1"]:
        range_max = df[data_column].max()
        # range_color = [0, range_max]
    elif scale == "PER_2":
        range_max = df[[c for c in df.columns if "_per" in c and "Votos" not in c]].max().max()
    range_color = [0, range_max]
    print(range_color)
    #
    map_center = region_centers[region]
    map_zoom = region_zooms[region]
    # if region == "ALL":
    #     map_zoom = 3
    #
    # TODO: e.g. still use "Boric" instead of "Boric_per" in colormap when using percentage values
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        # color=candidate,
        color=data_column,
        # color="Boric",
        color_continuous_scale=colorscale,
        range_color=range_color,        
        # locations="City",
        locations="City_id",
        # locations="City_with_id",
        # featureidkey="properties.comuna",
        # featureidkey="properties.Comuna",
        featureidkey="id",
        mapbox_style="carto-positron",
        # mapbox_style="open-street-map",
        opacity=0.7,
        center=map_center,
        zoom=map_zoom,
        # range_color=[0, df["Boric"].max()],
        # range_color=[0, df[candidate].max()],
        hover_data=["Region", "City"],
        # title=data_label
    )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}
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
    # fig.write_html('map.html', auto_open=True)
    # fig.show()
    return fig

def create_histogram(df, scale, eq, candidate, colorscale):
    """
    Create histogram...
    """
    # print(eq, candidate)
    #
    if candidate == "FORMULA":
        df["Formula"], df["Formula_per"], eq_label = evaluate_equation(df, eq)
        # df.rename({"Formula": data_text, "Formula_per": f"{data_text}_per"}, axis='columns')
        data_column = "Formula"
        data_text = data_column
        # data_column = data_text
        data_label = eq_label
    else:
        data_column = candidate
        data_text = candidate
        data_label = candidate        
    #
    if scale == "ABS":
        pass
    # elif scale == "PER":
    #     data_column += "_per"
    #     data_text += "_per"
    #     data_label += "_per"                
    if scale in ["PER_1", "PER_2"]:
        data_column += "_per"
        data_text += "_per"
        data_label += "_per"                
    #
    labels={data_column: data_label}
    #
    if scale in ["ABS", "PER_1"]:
        range_max = df[data_column].max()
    elif scale == "PER_2":
        range_max = df[[c for c in df.columns if "_per" in c and "Votos" not in c]].max().max()
    range_data = [0, range_max]
    #
    # if scale == "ABS":
    #     cols = [x for x in df.columns[1:-2].values if "_per" not in x and "Votos" not in x]
    # elif scale == "PER":
    #     # data_column = "_per"
    #     cols = [df.columns[1]]
    #     cols.extend([x for x in df.columns[1:-2].values if "_per" in x and "Votos" not in x])
    # df_in = df[cols]
    # print(df_in)
    df_in = df.copy()
    print(df_in.columns.values)    
    #
    fig = px.bar(
        df_in,
        y=data_column,
        x='City',
        text=data_text,
        labels=labels,
        color=data_column,      
        color_continuous_scale=colorscale, 
        range_color=range_data              
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


def evaluate_equation(df, eq):
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
        'vt': 'Votos_Total'
    }
    #
    # keep only +,- and letters in input equation
    eq = re.sub("[^a-zA-Z+-]", "", eq)
    eq_per = eq
    eq_label = eq
    for k, v in dct_input.items():
        if k in eq:
            eq = eq.replace(k, f"df['{v}']")
            eq_per = eq_per.replace(k, f"df['{v}_per']")
            eq_label = eq_label.replace(k, v)
    print(eq)
    print(eq_label)
    # print(eq_per)
    return eval(eq), eval(eq_per), eq_label


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False)


