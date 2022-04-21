import util
from init import options_category, options_reg, colorscales, options_scale_map, options_scale_hist
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_auth


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
    util.raise_exceptions(category, region, scale, formula, colorscale)            
    df_in = util.filter_dataframe(region)    
    geojson = util.filter_geojson(df_in, region)
    fig_map = util.create_map(df_in, geojson, category, region, scale, formula, colorscale)
    fig_bar = util.create_histogram(df_in, scale, formula, category, region, colorscale)        
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
    util.raise_exceptions(category, region, scale, formula, colorscale)            
    df_in = util.filter_dataframe(region)    
    geojson = util.filter_geojson(df_in, region)
    fig_map = util.create_map(df_in, geojson, category, region, scale, formula, colorscale)
    fig_bar = util.create_histogram(df_in, scale, formula, category, region, colorscale)        
    return [fig_map, fig_bar]
    

if __name__ == '__main__':
    # app.run_server(debug=True)
    # app.run_server(debug=False)
    app.run_server(host='0.0.0.0', port=8050, debug=True)
    # app.run_server(host='0.0.0.0', port=80, debug=True)


