
import json
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from urllib.request import urlopen
import get_data


app = Dash(__name__)

# Load into dataframe
df = get_data.return_df()

# Load into geojson data as dictionary
comm_areas_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
with urlopen(comm_areas_url) as response:
    comm_areas = json.load(response)
for feature in comm_areas['features']:
    feature['id'] = feature['properties']['area_numbe']

app.layout = html.Div([

    html.H1("Chicago Dash", style={'text-align': 'center'}),

    dcc.Dropdown(
        id="slct_year",
        options=[{'label': str(i), 'value': str(i)} for i in range(2006, 2023)],
        multi=False,
        value='2001',
        style={'width': "40%"}
    ),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='chicago_map', figure={})
])


@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='chicago_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)


def update_graph(slct_year):

    container = "This is the number of homocide in {}".format(slct_year)

    dff = df.copy()
    dff = dff[dff["year"] == slct_year]

    fig = px.choropleth(
        dff,
        locations='community area',
        geojson=comm_areas,
        color='value',
        scope='usa')

    fig.update_geos(fitbounds='locations', visible=False)

    return container, fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8056)






