import json
import pandas as pd
from urllib.request import urlopen
from dash import Dash, dcc, html, Input, Output
import plotly.express as px


# -------------------------- DATA LOADING --------------------------

# This is the processed datframe from Sasha and Anthony:
df = pd.read_csv('../data/merged_data.csv')

# This gets geojson for Chicago city
comm_areas_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"

with urlopen(comm_areas_url) as response:
    comm_areas = json.load(response)

for feature in comm_areas['features']:
    feature['id'] = feature['properties']['area_numbe']


# -------------------------- APPLICATION --------------------------

app = Dash(__name__)

# -------------------------- APP LAYOUT --------------------------

app.layout = html.Div([

    html.H1("Chicago Urban Development Explorer", style={'text-align': 'center'}),

    # ------------- Dropdown Layout -------------

    # Main Dropdown: Selecting type of data
    dcc.Dropdown(
        id = 'choose_data',
        options=[
            {'label': 'Demography', 'value': 'demography'},
            {'label': 'Building Permits', 'value': 'building_permits'},
            {'label': 'Crime: Homicide', 'value': 'crime'},
            {'label': 'Local Commerce', 'value': 'local_commerce'}]
    ),

    # Chain Dropdown 1: Selecting race
    html.Div([
        dcc.Dropdown(
        id = "slct_race",
        options = [
            {"label": 'Asian', "value": 'asian_per'},
            {"label": 'Black', "value": 'black_per'},
            {"label": 'Hispanic', "value": 'hisp_per'},
            {"label": 'White', "value": 'white_per'}],
        multi = False,
        placeholder = 'Showing racial distribution of ...',
        style = {})
]),

    # Chain Dropdown 2: Selecting year
    html.Div([
        dcc.Dropdown(
        id = "slct_year",
        options=[{'label': str(i), 'value': i} for i in range(2006, 2022)],
        multi = False,
        placeholder = 'Select a year ...',
        style = {})
]),

    # Chain Dropdown 3: Selecting building permits
    html.Div([
        dcc.Dropdown(
        id = "slct_permits",
        options=[
            {'label': '# Newly built buildings per 10,000 People',
             'value': 'Number built per 10,000 people'},
            {'label': ' # Demolished buildings per 10,000 People',
             'value': 'Number demolished per 10,000 people'}],
        multi = False,
        placeholder = 'Select a type of building permits ...',
        style = {})
]),

    # Chain Dropdown 4: Selecting local commerce
    html.Div([
        dcc.Dropdown(
        id = "slct_commerce",
        options=[
            {'label': 'Grocery Stores', 'value': 'grocery stores count'},
            {'label': 'Liquor Stores', 'value': 'liquor stores count'},
            {'label': 'Liquor Store / Grocery Store (Ratio)', 'value': 'liquor stores percent'}],
        multi = False,
        placeholder = 'Select a type of local commerce ...',
        style = {})
]),

    # ------------- Map Layout -------------

    html.Br(),
    dcc.Graph(id='chicago_demo_map', figure={}, style = {'display': 'none'}),
    dcc.Graph(id='chicago_permit_map', figure={}, style = {'display': 'none'}),
    dcc.Graph(id='chicago_crime_map', figure={}, style = {'display': 'none'}),
    dcc.Graph(id='chicago_commerce_map', figure={}, style = {'display': 'none'}),

])

# -------------------------- APP INTERACTION --------------------------

# ------------- Chain Dropdown -------------

# Callback 1: Selecting race
@app.callback(
   [Output(component_id='slct_race', component_property='style')],
   [Input(component_id='choose_data', component_property='value')])

def update_race_dpdn(property):
    if property == 'demography':
        return [{'display': 'block'}]
    else:
        return [{'display': 'none'}]

# Callback 2: Selecting year
@app.callback(
   [Output(component_id='slct_year', component_property='style')],
   [Input(component_id='choose_data', component_property='value')])

def update_year_dpdn(property):
    if property == 'building_permits' or property == 'crime':
        return [{'display': 'block'}]
    else:
        return [{'display': 'none'}]

# Callback 3: Selecting building permits
@app.callback(
   [Output(component_id='slct_permits', component_property='style')],
   [Input(component_id='choose_data', component_property='value')])

def update_permit_dpdn(property):
    if property == 'building_permits':
        return [{'display': 'block'}]
    else:
        return [{'display': 'none'}]

# Callback 4: Selecting local commerce
@app.callback(
   [Output(component_id='slct_commerce', component_property='style')],
   [Input(component_id='choose_data', component_property='value')])

def update_commerce_dpdn(property):
    if property == 'local_commerce':
        return [{'display': 'block'}]
    else:
        return [{'display': 'none'}]

# ------------- Interactive Graph -------------

@app.callback(
    [Output(component_id='chicago_demo_map', component_property='style'),
     Output(component_id='chicago_permit_map', component_property='style'),
     Output(component_id='chicago_crime_map', component_property='style'),
     Output(component_id='chicago_commerce_map', component_property='style')],
     Input(component_id='choose_data', component_property='value'))

def enable_graph(chosen_data):
    if chosen_data == 'demography':
        return [{'display': 'block'}, {'display': 'none'},
        {'display': 'none'}, {'display': 'none'}]
    elif chosen_data == 'building_permits':
        return [{'display': 'none'}, {'display': 'block'},
        {'display': 'none'}, {'display': 'none'}]
    elif chosen_data == 'crime':
        return [{'display': 'none'}, {'display': 'none'},
        {'display': 'block'}, {'display': 'none'}]
    else:
        return [{'display': 'none'}, {'display': 'none'},
        {'display': 'none'}, {'display': 'block'}]


# ------------- Visualization -------------

# Demography map
@app.callback(
    Output(component_id='chicago_demo_map', component_property='figure'),
    Input(component_id='slct_race', component_property='value')
)

def update_demo(slct_race):

    dff = df.copy()
    dff = dff[dff['year'] == 2010]

    fig = px.choropleth(
        dff,
        locations = 'area_num',
        geojson = comm_areas,
        color = slct_race,
        color_continuous_scale="Greens",
        hover_name = 'community',
        hover_data = {'year': True, 'area_num': False,
            slct_race: True},
        scope = 'usa',
        width = 1000,
        height = 500)

    fig.update_geos(fitbounds='locations', visible=False)

    return fig


# Building permit map
@app.callback(
     Output(component_id='chicago_permit_map', component_property='figure'),
    [Input(component_id='slct_year', component_property='value'),
     Input(component_id='slct_permits', component_property='value')]
)

def update_building(slct_year, slct_permits):

    dff = df.copy()
    dff = dff[dff["year"] == slct_year]

    fig = px.choropleth(
        dff,
        locations = 'area_num',
        geojson = comm_areas,
        color = slct_permits,
        color_continuous_scale="YlOrRd",
        hover_name = 'community',
        hover_data = {'year': True, 'area_num': False,
            slct_permits: True},
        scope = 'usa',
        width = 1000,
        height = 500)

    fig.update_geos(fitbounds='locations', visible=False)
    
    return fig


# Crime map
@app.callback(
    Output(component_id='chicago_crime_map', component_property='figure'),
    Input(component_id='slct_year', component_property='value')
)

def update_crime(slct_year):

    dff = df.copy()
    dff = dff[dff["year"] == slct_year]

    fig = px.choropleth(
        dff,
        locations = 'area_num',
        geojson = comm_areas,
        color = 'Number of Homicides',
        color_continuous_scale="OrRd",
        hover_name = 'community',
        hover_data = {'year': True, 'area_num': False,
            'Number of Homicides': True},
        scope = 'usa',
        width = 1000,
        height = 500)

    fig.update_geos(fitbounds='locations', visible=False)

    return fig


# Local commerce map
@app.callback(
     Output(component_id='chicago_commerce_map', component_property='figure'),
     Input(component_id='slct_commerce', component_property='value')
)

def update_local_commerce(slct_commerce):

    dff = df.copy()
    dff = dff[dff["year"] == 2011]

    fig = px.choropleth(
        dff,
        locations = 'area_num',
        geojson = comm_areas,
        color = slct_commerce,
        color_continuous_scale="BuPu",
        hover_name = 'community',
        hover_data = {'year': True, 'area_num': False,
            slct_commerce: True},
        scope = 'usa',
        width = 1000,
        height = 500)

    fig.update_geos(fitbounds='locations', visible=False)
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8092)
