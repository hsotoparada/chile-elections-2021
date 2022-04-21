from init import options_category, category_participation, category_candidates, category_report
from init import region_centers, region_zooms, region_short
from init import geojson_regions, geojson_cities, df, df_reg, df1, df1_reg, df2, df2_reg
from dash.exceptions import PreventUpdate
import plotly.express as px
import re


#-------------------------- DASH INTERACTIVITY -------------------------------#
   
def raise_exceptions(category, region, scale, formula, colorscale):
    print(f"input --> {category}, {region}, {scale}, {formula}, {colorscale}")    
    if region is None:
        raise PreventUpdate
    if scale is None:
        raise PreventUpdate
    if category is None:
        raise PreventUpdate
    if category == "Formula":
        if formula is None:
            raise PreventUpdate
        # if scale in ["ABS_3","ABS_4","PER_3","PER_4"]:
        if scale in ["ABS_2", "ABS_4","PER_2","PER_4"]:            
            raise PreventUpdate        
    if category in category_participation:
        # if scale in ["ABS_2","ABS_4"] or "PER" in scale:
        if "PER" in scale:            
            raise PreventUpdate
        if scale in ["ABS_2","ABS_4"]:            
            raise PreventUpdate            

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
