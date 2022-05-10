from init import geojson_regions, geojson_cities, dct_votes
from init import dct_category, dct_regions
from dash.exceptions import PreventUpdate
import plotly.express as px
import re


#-------------------------- DASH INTERACTIVITY -------------------------------#
   
def raise_exceptions(dct_user):
    """
    Handle exceptions that prevent updating dashboard components when incomplete input information and other special cases.

    Parameters
    ----------
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
    """
    print(f"\n{dct_user}")     
    if dct_user['nround'] is None:
        raise PreventUpdate    
    if dct_user['region'] is None:
        raise PreventUpdate
    if dct_user['scale'] is None:
        raise PreventUpdate      
    if dct_user['category'] is None:
        raise PreventUpdate
    if dct_user['category'] == "Formula":
        if dct_user['formula'] is None:
            raise PreventUpdate
        if dct_user['scale'] in ["ABS_2","ABS_4","PER_2","PER_4"]:            
            raise PreventUpdate        
    if dct_user['category'] in dct_category[dct_user['nround']]['category_participation']:
        if "PER" in dct_user['scale']:            
            raise PreventUpdate
        if dct_user['scale'] in ["ABS_2","ABS_4"]:            
            raise PreventUpdate             

def filter_dataframe(dct_user):  
    """
    Filter votes dataframe based on selected round of voting and geographical region.

    Parameters
    ----------
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.        
    """     
    if dct_user['region'] == "ALL PER REGION":
        df_in = dct_votes[dct_user['nround']]['all_reg'].copy()        
    else:
        df_in = dct_votes[dct_user['nround']]['all'].copy()        
        if dct_user['region'] != "ALL PER CITY":
            df_in = df_in[df_in['Region'] == dct_user['region']]
    #
    df_in.reset_index(drop=True, inplace=True)
    print(df_in.head(10))
    print(df_in.shape)
    print(dct_votes[dct_user['nround']]['all'].shape)    
    return df_in    

def filter_geojson(df_in, dct_user):   
    """
    Filter geospatial data (geographic features) based on selected geographical region.

    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.        
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
    geojson_in: pandas.dataframe
        Dataframe containing geospatial data (geographic features) filtered by region.        
    """       
    if dct_user['region'] == "ALL PER REGION":
        geojson_in = geojson_regions.copy()
        geojon_ids = df_in['Region_id'].values
        features_in = [f for f in geojson_regions['features'] if f['id'] in geojon_ids]
        geojson_in['features'] = features_in         
    else:
        geojson_in = geojson_cities.copy()
        geojon_ids = df_in['City_id'].values
        features_in = [f for f in geojson_cities['features'] if f['id'] in geojon_ids]
        geojson_in['features'] = features_in      
    return geojson_in

def create_figure_map(df_in, geojson, dct_user):    
    """
    Create Mapbox choropleth map showing colored regions representing vote counting from selected category in input dataframe.

    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.  
    geojson: pandas.dataframe
        Dataframe containing geospatial data (geographic features) filtered by region.        
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
    fig: plotly.express.choropleth_mapbox
        Mapbox choropleth map created using vote counting from input dataframe.        
    """   
    data_column, data_label = get_map_data(df_in, dct_user)
    labels = {data_column: data_label}    
    cols = get_plot_columns(df_in, data_column, dct_user)
    range_data = get_plot_range(df_in, cols, dct_user)        
    if dct_user['scale_range'] is not None:
        range_data = parse_user_range(dct_user, range_data)            
        
    map_center = dct_regions['region_centers'][dct_user['region']]
    map_zoom = dct_regions['region_zooms'][dct_user['region']]
    if dct_user['region'] == "ALL PER REGION":
        locations = "Region_id"
        hover_data = ["Region"]
    else:
        locations="City_id"
        hover_data = ["Region", "City"]
    
    fig = px.choropleth_mapbox(
        df_in,
        geojson=geojson,
        color=data_column,
        color_continuous_scale=dct_user['colorscale'],
        range_color=range_data,   
        labels=labels,
        locations=locations,
        featureidkey="id",
        mapbox_style="carto-positron",
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

def create_figure_bar(df_in, dct_user):    
    """
    Create Bar plot showing colored rectangular marks representing vote counting from selected category in input dataframe.

    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.  
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
    fig: plotly.express.bar
        Bar plot created using vote counting from input dataframe.        
    """   
    data_column, data_label, data_text = get_bar_data(df_in, dct_user)
    labels = {data_column: data_label}
    cols = get_plot_columns(df_in, data_column, dct_user)
    range_data = get_plot_range(df_in, cols, dct_user)
    if dct_user['scale_range'] is not None:
        range_data = parse_user_range(dct_user, range_data)    
    
    # print(df_in.columns.values)    
    if dct_user['region'] == "ALL PER REGION":
        x = "Region"
        hover_data=["Region"]
    else:
        x = "City"
        hover_data=["Region", "City"]    
    
    df_in["Region"].replace(to_replace=dct_regions['region_short'], inplace=True)  
    fig = px.bar(
        df_in,
        y=data_column,
        x=x,
        text=data_text,
        labels=labels,
        color=data_column,      
        color_continuous_scale=dct_user['colorscale'], 
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

def get_map_data(df_in, dct_user):    
    """
    Retrieve data column which will be used to create Mapbox choropleth map.

    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.  
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
        Tuple containing the column in input dataframe (and its plotting label), which will as input data for Mapbox choropleth map.
    """   
    if dct_user['category'] == "Formula":
        df_in["Formula"], df_in["Formula_per"], formula_label = evaluate_formula(df_in, dct_user)
        data_column = "Formula"
        data_label = formula_label
    else:
        data_column = dct_user['category']
        if dct_user['category'] in dct_category[dct_user['nround']]['category_candidates']:
            data_label = [
                o['label'].split(None)[-1] for o in dct_category[dct_user['nround']]['options_category'] 
                if o['value'] == dct_user['category']
            ][0]            
        if dct_user['category'] in dct_category[dct_user['nround']]['category_report']:
            data_label = [
                o['label'] for o in dct_category[dct_user['nround']]['options_category'] 
                if o['value'] == dct_user['category']
            ][0]
        if dct_user['category'] in dct_category[dct_user['nround']]['category_participation']:
            data_label = [
                o['label'] for o in dct_category[dct_user['nround']]['options_category'] 
                if o['value'] == dct_user['category']
            ][0]            
    
    # data_column = dct_user['category']
    if "ABS" in dct_user['scale']:
        pass
    if "PER" in dct_user['scale']:
        data_column += "_per"
    
    return data_column, data_label

def get_bar_data(df_in, dct_user):    
    """
    Retrieve data column which will be used to create Bar plot.    
    
    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.  
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
        Tuple containing the column in input dataframe (and its plotting label and text), which will as input data for Bar plot.
    """   
    if dct_user['category'] == "Formula":
        df_in["Formula"], df_in["Formula_per"], formula_label = evaluate_formula(df_in, dct_user)
        dct_votes[dct_user['nround']]['pres']["Formula"], dct_votes[dct_user['nround']]['pres']["Formula_per"], formula_label = evaluate_formula(dct_votes[dct_user['nround']]['pres'], dct_user)
        dct_votes[dct_user['nround']]['pres_reg']["Formula"], dct_votes[dct_user['nround']]['pres_reg']["Formula_per"], formula_label = evaluate_formula(dct_votes[dct_user['nround']]['pres_reg'], dct_user)                        
        data_column = "Formula"
        data_text = data_column
        # data_column = data_text
        data_label = formula_label
    else:
        data_column = dct_user['category']
        data_text = dct_user['category']
        # data_label = category  
        if dct_user['category'] in dct_category[dct_user['nround']]['category_candidates']:
            data_label = [
                o['label'].split(None)[-1] for o in dct_category[dct_user['nround']]['options_category'] 
                if o['value'] == dct_user['category']
            ][0]            
        if dct_user['category'] in dct_category[dct_user['nround']]['category_report']:
            data_label = [
                o['label'] for o in dct_category[dct_user['nround']]['options_category'] 
                if o['value'] == dct_user['category']
            ][0]
        if dct_user['category'] in dct_category[dct_user['nround']]['category_participation']:
            data_label = [
                o['label'] for o in dct_category[dct_user['nround']]['options_category'] 
                if o['value'] == dct_user['category']
            ][0]          
    
    if "ABS" in dct_user['scale']:
        pass
    if "PER" in dct_user['scale']:
        data_column += "_per"
        data_text += "_per"
        # data_label += "_per" 
    
    return data_column, data_label, data_text        

def get_plot_columns(df_in, data_column, dct_user):    
    """
    Retrieve columns which, based on selected category in input dataframe, will be used to calculate the range of values shown in plot.
    
    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.  
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
    cols: list
        List of retrieved columns in input dataframe.        
    """       
    if dct_user['scale'] in ["ABS_1", "ABS_3", "PER_1", "PER_3"]: # category scale
        cols = data_column
    elif dct_user['scale'] in ["ABS_2", "ABS_4"]: # common category scale
        if dct_user['category'] in dct_category[dct_user['nround']]['category_candidates']:
            cols = [
                c for c in df_in.columns 
                if c in dct_category[dct_user['nround']]['category_candidates'] 
                and "_per" not in c
            ]                        
        elif dct_user['category'] in dct_category[dct_user['nround']]['category_report']:
            cols = [
                c for c in df_in.columns 
                if c in dct_category[dct_user['nround']]['category_report'] 
                and "_per" not in c
            ] 
        elif dct_user['category'] in dct_category[dct_user['nround']]['category_participation']:
            cols = data_column
    elif dct_user['scale'] in ["PER_2", "PER_4"]: # common category scale
        if dct_user['category'] in dct_category[dct_user['nround']]['category_candidates']:
            cols = [
                c for c in df_in.columns 
                if c in dct_category[dct_user['nround']]['category_candidates'] 
                and "_per" in c 
            ]                                    
        elif dct_user['category'] in dct_category[dct_user['nround']]['category_report']:
            cols = [
                c for c in df_in.columns 
                if c in dct_category[dct_user['nround']]['category_report'] 
                and "_per" in c
            ]
    return cols

def get_plot_range(df_in, cols, dct_user):    
    """
    Calculate range of values to be shown in plot, based on selected category and columns in input dataframe.
    
    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.  
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
        
    Returns
    -------
        List containing minimum (by default 0) and maximum values in calculated range.        
    """      
    if dct_user['scale'] in ["ABS_1", "PER_1"]:        
        range_max = df_in[cols].max()
    elif dct_user['scale'] in ["ABS_3", "PER_3"]:
        if dct_user['category'] in dct_category[dct_user['nround']]['category_participation']:
            if dct_user['region'] == "ALL PER REGION":
                range_max = dct_votes[dct_user['nround']]['part_reg'][cols].max()                
            else:
                range_max = dct_votes[dct_user['nround']]['part'][cols].max()                
        else:
            if dct_user['region'] == "ALL PER REGION":
                range_max = dct_votes[dct_user['nround']]['pres_reg'][cols].max()                
            else:            
                range_max = dct_votes[dct_user['nround']]['pres'][cols].max()                        
    elif dct_user['scale'] in ["ABS_2", "PER_2"]:
        if dct_user['category'] in dct_category[dct_user['nround']]['category_participation']:
            range_max = df_in[cols].max()
        else:
            range_max = df_in[cols].max().max()
    elif dct_user['scale'] in ["ABS_4", "PER_4"]:
        if dct_user['category'] in dct_category[dct_user['nround']]['category_participation']:
            if dct_user['region'] == "ALL PER REGION":
                range_max = dct_votes[dct_user['nround']]['part_reg'][cols].max()                                
            else:            
                range_max = dct_votes[dct_user['nround']]['part'][cols].max()                                
        else:
            if dct_user['region'] == "ALL PER REGION":
                range_max = dct_votes[dct_user['nround']]['pres_reg'][cols].max().max()                                
            else:            
                range_max = dct_votes[dct_user['nround']]['pres'][cols].max().max()                                        
    return [0, range_max]

def parse_user_range(dct_user, range_data):        
    """
    Parse scale range entered by user. See Instructions markdown in app.py for usage details.
    
    Parameters
    ----------
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.
    range_data: list
        List containing minimum (by default 0) and maximum values in calculated data range.            

    Returns
    -------
        Tuple containing the evaluated user-defined formula and a formula label for plotting purpose.        
    """   
    scale_min, scale_max = range_data
    if dct_user['scale_range'] == '':
        pass
    elif dct_user['scale_range'].find('-') == -1:
        raise ValueError(
            "Format of entered scale range should be 'MIN-MAX'"
        )
    else:
        scale_min, scale_max = dct_user['scale_range'].split('-')
    
    return float(scale_min), float(scale_max)

def evaluate_formula(df, dct_user):        
    """
    Parse and evaluate formula entered by user. See Instructions markdown in app.py for usage details.
    
    Parameters
    ----------
    df_in: pandas.dataframe
        Dataframe containing votes filtered by voting round and region.  
    dct_user: dict
        Dictionary containing selected input options by user, such as: nround, category, region, etc.
        See details in documentation for update_fig_1 in app.py.

    Returns
    -------
        Tuple containing the evaluated user-defined formula and a formula label for plotting purpose.        
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
    
    # keep only +,- and letters in input equation
    eq = re.sub("[^a-zA-Z+-x]", "", dct_user['formula'])
    
    # replace candidates
    eq_per = eq
    eq_label = eq
    for k, v in dct_input.items():
        if k in eq:
            eq = eq.replace(k, f"df['{v}']")
            eq_per = eq_per.replace(k, f"df['{v}_per']")
            eq_label = eq_label.replace(k, v)
    
    # replace multiplication
    eq = eq.replace('x', '*')
    eq_per = eq_per.replace('x', '*')
    print(eq)
    print(eq_label)
    # print(eq_per)
    return eval(eq), eval(eq_per), eq_label