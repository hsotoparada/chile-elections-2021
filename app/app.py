import util
from init import dct_category, dct_options
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

#---------------------------- DASH LAYOUT -------------------------------------#

# create a dash application (dash)
app = dash.Dash(external_stylesheets = [dbc.themes.SANDSTONE])

# expose Flask instance
server = app.server

header_1 = html.Div(
    [   
        html.Div(
            dcc.Markdown('''
                ### **Elección Presidencial Chile 2021**  
                ---  
                **Fuente**: Elaboración propia en base a datos del [servel](https://www.servelelecciones.cl/)
                
                **Author**: Hugo Soto. Data Scientist | PhD Freie Universität Berlin
                
                **Contacto**: hugosotoparada@gmail.com
                
                [*Github*](https://github.com/hsotoparada/chile-elections-2021)  
            ''', style={"white-space": "pre"})
        ),                
    ]
)

header_2 = html.Div(
    dbc.Card([
        dcc.Markdown('''                     
            **Instrucciones**: Seleccionar **RONDA**, **CATEGORIA**, **REGION**, **ESCALA** y **PALETA** 
            en cada grupo de menús desplegables, para actualizar dos figuras interactivas, compuestas
            de un mapa y un gráfico de barras.
            **RONDA** puede ser 1 o 2, correspondiente a la primera o segunda vuelta de votación, 
            respectivamente.
            **CATEGORIA** puede ser votos obtenidos por un candidat@ o datos de participación.
            **CATEGORIA = ** *CANDIDAT@ FORMULA* permite al usuario ingresar una FORMULA 
            como suma (+) o resta (-) entre votos de un@ o más candidat@s,
            o multiplicación (x) de votos por un factor numérico.
            En **FORMULA**, candidat@s deben ser representad@s por:
            BO, KA, PR, SI, EN, PA, AR (o bo, ka, etc.), correspondiente a las primeras
            letras en los apellidos de los candidat@s.
            Por ejemplo, la combinación de votos de Boric más 50% de Parisi puede calcularse ingresando
            la **FORMULA**: bo + 0.5xpa.
            **REGION** es una región en el país o todas las regiones, desagregadas por región o ciudad.
            **ESCALA** es el rango en que los datos se muestran.
            **ESCALA** puede ser absoluta (sin '%') o en porcentaje (con '%') en varios niveles.
            En niveles *CATEGORIA* y *GLOBAL* votos de candidat@s se muestran en el rango del candidat@
            y de todos l@s candidat@s, respectivamente, opcionalmente dentro de la *REGION*
            seleccionada o a nivel *PAIS*.
            Mismos niveles también se aplican entre las categorías *VOTOS NULOS*, *BLANCOS*, *EMITIDOS* y 
            *TOTAL*.
            Para categorías *CANDIDAT@ FORMULA* y *PARTICIPACION* las figuras se actualizarán sólo si
            los niveles *CATEGORIA REGION/PAIS* son seleccionados.
            Para casos no incluidos en los niveles disponibles o para tener mayor control al definir la 
            escala de datos, el usuario puede ingresar un rango personalizado en la forma MIN-MAX 
            (ejemplo: 10-25. El guión '-' debe incluirse). 
            Esto facilita la comparación de datos, por ejemplo, entre las dos rondas de votaciones.
            La visibilidad de los datos puede mejorar seleccionando una **PALETA** alternativa a la 
            seleccionada por defecto, dentro de la lista disponible.
        ''')],        
    body=True,            
    ),     
),

controls_round_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_round_1',
                    options=[1, 2],
                    placeholder='RONDA',
                ),  
                dbc.Tooltip(
                    'Ingresar ronda de votaciones a mostrar en primer mapa/gráfico.',
                    target="select_round_1",
                ),                      
            ],
        body=False,            
        ),     
    ],
)            

controls_round_2 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_round_2',
                    options=[1, 2],
                    placeholder='RONDA',
                ),  
                dbc.Tooltip(
                    'Ingresar ronda de votaciones a mostrar en segundo mapa/gráfico.',
                    target="select_round_2",
                ),                      
            ],
        body=False,            
        ),     
    ],
)    
            
controls_category_1 = dbc.CardGroup(
    [    
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_category_1',
                    options=dct_category[1]['options_category'],
                    placeholder='CATEGORIA',
                    # style={'width':'40%', 'padding':'3px', 'font-size':'14px', 'text-align-last':'center'}
                ),  
                dbc.Tooltip(
                    'Ingresar categoría a mostrar en primer mapa/gráfico.',
                    target="select_category_1",
                ),                      
            ],
        body=False,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_formula_1',
                    type="text",
                    placeholder="FORMULA",
                    debounce=True,
                ), 
                dbc.Tooltip(
                    "Ingresar fórmula a aplicar (si CATEGORIA = CANDIDAT@ FORMULA) en primer mapa/gráfico.",
                    target="input_formula_1",
                ),                
            ],
        body=False,            
        ),         
    ],
)

controls_category_2 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_category_2',
                    options=dct_category[1]['options_category'],
                    placeholder='CATEGORIA',
                ),          
                dbc.Tooltip(
                    'Ingresar categoría a mostrar en segundo mapa/gráfico.',
                    target="select_category_2",
                ),                                 
            ],
        body=False,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_formula_2',
                    type="text",
                    placeholder="FORMULA",
                    debounce=True,
                ),               
                dbc.Tooltip(
                    "Ingresar fórmula a aplicar (si CATEGORIA = CANDIDAT@ FORMULA) en segundo mapa/gráfico.",
                    target="input_formula_2",
                ),                    
            ],
        body=False,            
        ),         
    ],
)

controls_region_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_region_1',
                    options=dct_options['options_reg'],
                    placeholder='REGION',
                ),
                dbc.Tooltip(
                    "Ingresar región del país en primer mapa/gráfico.",
                    target="select_region_1",
                ),                                
            ],
        body=False,            
        ),
    ],
)

controls_region_2 = dbc.CardGroup(
    [
        dbc.Card(
            [        
                dcc.Dropdown(
                    id='select_region_2',
                    options=dct_options['options_reg'],
                    placeholder='REGION',
                ),
                dbc.Tooltip(
                    "Ingresar región del país en segundo mapa/gráfico.",
                    target="select_region_2",
                ),                 
            ],
        body=False,            
        ),
    ],
)

controls_colorscale_1 = dbc.CardGroup(
    [
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_colorscale_1',
                    options=[{"value": x, "label": x} for x in dct_options['colorscales']],
                    placeholder='PALETA',
                    value="hot_r"
                ),
                dbc.Tooltip(
                    "Ingresar paleta de colores en primer mapa/gráfico.",
                    target="select_colorscale_1",
                ),                   
            ],
        body=False,            
        ),      
    ],
)

controls_colorscale_2 = dbc.CardGroup(
    [       
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_colorscale_2',
                    options=[{"value": x, "label": x} for x in dct_options['colorscales']],
                    placeholder='PALETA',
                    value="hot_r"
                ),
                dbc.Tooltip(
                    "Ingresar paleta de colores en segundo mapa/gráfico.",
                    target="select_colorscale_2",
                ),                
            ],
        body=False,            
        ),         
    ],
)

controls_datascale_1 = dbc.CardGroup(
    [ 
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_datascale_1',
                    options=dct_options['options_scale_map'],
                    placeholder='ESCALA',
                ),
                dbc.Tooltip(
                    "Ingresar escala de datos en primer mapa/gráfico.",
                    target="select_datascale_1",
                ),                  
            ],
        body=False,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_datascale_1',
                    type="text",
                    placeholder="MIN - MAX",
                    debounce=True,
                ), 
                dbc.Tooltip(
                    "Ingresar rango personalizado en primer mapa/gráfico.",
                    target="input_datascale_1",
                ),                
            ],
        body=False,            
        ),               
    ],
)

controls_datascale_2 = dbc.CardGroup(
    [       
        dbc.Card(
            [
                dcc.Dropdown(
                    id='select_datascale_2',
                    options=dct_options['options_scale_map'],
                    placeholder='ESCALA',
                ),
                dbc.Tooltip(
                    "Ingresar escala de datos en segundo mapa/gráfico.",
                    target="select_datascale_2",
                ),                     
            ],
        body=False,            
        ),        
        dbc.Card(
            [
                dcc.Input(
                    id='input_datascale_2',
                    type="text",
                    placeholder="MIN - MAX",
                    debounce=True,
                ), 
                dbc.Tooltip(
                    "Ingresar rango personalizado en segundo mapa/gráfico.",
                    target="input_datascale_2",
                ),                
            ],
        body=False,            
        ),         
    ],
)

fig_1 = html.Div(
    [
        dcc.Graph(
            id="map_1",
            style={'height': '70vh'}
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
                dbc.Col(controls_round_1, width=1, sm=1, md=1, lg=1, xl=1),                
                dbc.Col(controls_category_1, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(controls_region_1, width=3, sm=3, md=3, lg=3, xl=3),
                dbc.Col(controls_datascale_1, width=3, sm=3, md=3, lg=3, xl=3),
                dbc.Col(controls_colorscale_1, width=1, sm=1, md=1, lg=1, xl=1)               
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(controls_round_2, width=1, sm=1, md=1, lg=1, xl=1),                                
                dbc.Col(controls_category_2, width=4, sm=4, md=4, lg=4, xl=4),
                dbc.Col(controls_region_2, width=3, sm=3, md=3, lg=3, xl=3),
                dbc.Col(controls_datascale_2, width=3, sm=3, md=3, lg=3, xl=3),
                dbc.Col(controls_colorscale_2, width=1, sm=1, md=1, lg=1, xl=1)                
            ],
            align="start",
        ),              
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
    Output("select_category_1", "options"),
    Input("select_round_1", "value")
)
def update_category_options_1(nround):
    """
    Update category options for first figure (map and plot), based on selected voting round.

    Parameters
    ----------
    nround: int
        Voting round number. It can be 1 or 2, for the first or second round respectively.

    Returns
    -------
    dct: dict
        Dictionary containing selected category options.
    """    
    if nround is None:
        raise PreventUpdate
    return dct_category[nround]['options_category']

# callback decorator
@app.callback(
    Output("select_category_2", "options"),
    Input("select_round_2", "value")
)
def update_category_options_2(nround):
    """
    Update category options for second figure (map and plot), based on selected voting round.

    Parameters
    ----------
    nround: int
        Voting round number. It can be 1 or 2, for the first or second round respectively.

    Returns
    -------
    dct: dict
        Dictionary containing selected category options.
    """     
    if nround is None:
        raise PreventUpdate
    return dct_category[nround]['options_category']

# callback decorator
@app.callback(
    Output("map_1", "figure"),
    Output("hist_1", "figure"),
    Input("select_round_1", "value"),    
    Input("select_category_1", "value"),
    Input("select_region_1", "value"),
    Input("select_datascale_1", "value"),
    Input("input_datascale_1", "value"),        
    Input("input_formula_1", "value"),
    Input("select_colorscale_1", "value")
)
def update_fig_1(nround, category, region, scale, scale_range, formula, colorscale):
    """
    Update first figure (map and plot), based on several selected input options.

    Parameters
    ----------
    nround: int
        Voting round number. It can be 1 or 2, for the first or second round respectively.
    category: str
        Category of vote counting. It can be one of the labels defined in the list dct_category[nround]['options_category'].        
    region: str
        Geographical region of vote counting. It can be one of the labels defined in the list dct_options['options_reg'].
    scale: str
        Categorical scale in which values are plotted. It can be one of the labels defined in the list dct_options['options_scale_map']. 
        See the Instructions markdown for more details.
    scale_range: str (optional)
        User-defined scale range in which values are plotted. See the Instructions markdown for more details.        
    formula: str (optional)
        User-defined formula to calculate votes. See explanation for CATEGORIA = FORMULA in Instructions markdown.
    colorscale: str
        One of the built-in continuous color scale names in plotly. See https://plotly.com/python/builtin-colorscales/
        
    Returns
    -------
    dct: list
        List containing updated map and plot of first figure.
    """     
    dct_user = {
        'nround': nround,
        'category': category,
        'region': region,
        'scale': scale,
        'scale_range': scale_range,        
        'formula': formula,
        'colorscale': colorscale,
    }
    util.raise_exceptions(dct_user)            
    df_in = util.filter_dataframe(dct_user)    
    geojson = util.filter_geojson(df_in, dct_user)
    fig_map = util.create_figure_map(df_in, geojson, dct_user)
    fig_bar = util.create_figure_bar(df_in, dct_user)        
    return [fig_map, fig_bar]

# callback decorator
@app.callback(
    Output("map_2", "figure"),
    Output("hist_2", "figure"),  
    Input("select_round_2", "value"),        
    Input("select_category_2", "value"),
    Input("select_region_2", "value"),
    Input("select_datascale_2", "value"),
    Input("input_datascale_2", "value"),    
    Input("input_formula_2", "value"),
    Input("select_colorscale_2", "value")
)
def update_fig_2(nround, category, region, scale, scale_range, formula, colorscale):
    """
    Update second figure (map and plot), based on several selected input options.

    Parameters
    ----------
    nround: int
        Voting round number. It can be 1 or 2, for the first or second round respectively.
    category: str
        Category of vote counting. It can be one of the labels defined in the list dct_category[nround]['options_category'].        
    region: str
        Geographical region of vote counting. It can be one of the labels defined in the list dct_options['options_reg'].
    scale: str
        Categorical scale in which values are plotted. It can be one of the labels defined in the list dct_options['options_scale_map']. 
        See the Instructions markdown for more details.
    scale_range: str (optional)
        User-defined scale range in which values are plotted. See the Instructions markdown for more details.                
    formula: str (optional)
        User-defined formula to calculate votes. See explanation for CATEGORIA = FORMULA in Instructions markdown.
    colorscale: str
        One of the built-in continuous color scale names in plotly. See https://plotly.com/python/builtin-colorscales/
        
    Returns
    -------
    dct: list
        List containing updated map and plot of second figure.
    """      
    dct_user = {
        'nround': nround,
        'category': category,
        'region': region,
        'scale': scale,
        'scale_range': scale_range,        
        'formula': formula,
        'colorscale': colorscale,
    }    
    util.raise_exceptions(dct_user)            
    df_in = util.filter_dataframe(dct_user)    
    geojson = util.filter_geojson(df_in, dct_user)
    fig_map = util.create_figure_map(df_in, geojson, dct_user)
    fig_bar = util.create_figure_bar(df_in, dct_user)        
    return [fig_map, fig_bar]
    

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)