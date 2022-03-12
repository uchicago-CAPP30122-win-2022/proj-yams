import pandas as pd
import geojson
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import get_data

app = Dash(__name__)

#### This part may be wrong?
df = get_data.return_df()
with open("data/permits.geojson") as f:
    gj = geojson.load(f)

app.layout = html.Div([
    html.H1("Chicago Crime: Updated Dash", style={'text-align': 'center'}),
    dcc.Dropdown(
        id="slct_year",
        options=[
            {"label": '2001', "value": 2001},
            {"label": '2002', "value": 2002},
            {"label": '2003', "value": 2003},
            {"label": '2003', "value": 2004},
            {"label": '2005', "value": 2005},
            {"label": '2006', "value": 2006},
            {"label": '2007', "value": 2007},
            {"label": '2008', "value": 2008},
            {"label": '2009', "value": 2009},
            {"label": '2010', "value": 2010},
            {"label": '2011', "value": 2011},
            {"label": '2012', "value": 2012},
            {"label": '2013', "value": 2013},
            {"label": '2014', "value": 2014},
            {"label": "2015", "value": 2015},
            {"label": "2016", "value": 2016},
            {"label": "2017", "value": 2017},
            {"label": "2018", "value": 2018},
            {"label": '2019', "value": 2019},
            {"label": '2020', "value": 2020},
            {"label": '2021', "value": 2021},
            {"label": '2022', "value": 2022}
            ],
        multi=False,
        value=2001,
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

def update_graph(slct_reason, slct_year):

    container = "This is the percentage of bee colonies died of {} in {}".format(slct_reason, slct_year)

    dff = df.copy()
    dff = dff[dff["Year"] == slct_year]

    fig = px.choropleth_mapbox(
        data_frame=dff,
        geojson=gj,
        locations='area',
        color=df['value'],
        color_continuous_scale="YlOrRd",
        range_color=(0, df['value'].max()),
        hover_name='area',
        hover_data={'community area': True, 'year': False, 'value': True},
        mapbox_style='open-street-map',
        zoom=1,
        # center={'lat': 19, 'lon': 11},
        opacity=0.8
        )
    
    return container, fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8055)
