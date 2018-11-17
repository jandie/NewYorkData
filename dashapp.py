import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from plotly import graph_objs as go
from plotly.graph_objs import *
import os
from flask import Flask

app = Flask(__name__)

dashapp = dash.Dash(__name__, server=app)
dashapp.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})
mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'
default_hour = 0
default_zoom = 12

df = pd.read_csv('small_taxi.csv')
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])

dashapp.layout = html.Div([
    html.Div(id='prev-button-value', style={'display': 'none'}),
    html.Div(id='next-button-value', style={'display': 'none'}),

    html.H1(children='New York City - Yellow Cab data 2014',
            style={"text-align": "center"}),

    html.Div(children="By Jandie Hendriks",
             style={"text-align": "center",
                    "margin-bottom": "20px"}),

    html.Div([
        dcc.Graph(id='my-graph')
    ], style={"margin-bottom": "20px"}),

    html.Div(
        dcc.Slider(
            id='time-slider',
            min=0,
            max=23,
            marks={i: 'Time {}'.format(i) if i == 1 else str(i) for i in range(0, 23)},
            value=default_hour,
        ), style={"margin-bottom": "30px"}),

    html.Button('Next',
                id='next-button',
                style={"margin-bottom": "20px"}),
    # html.Button('Previous',
    #             id='prev-button',
    #             style={"margin-bottom": "20px"}),
])


@dashapp.callback(
    Output('my-graph', 'figure'),
    [Input('time-slider', 'value')],
    [State('my-graph', 'relayoutData')]
)
def update_output_div(input_value, prevLayout):
    zoom = default_zoom
    latInitial = 40.7272
    lonInitial = -73.991251
    bearing = 0

    filtered_df = df[(df.pickup_datetime.dt.hour == input_value)]

    if not prevLayout is None and 'mapbox.zoom' in prevLayout.keys():
        zoom = float(prevLayout['mapbox.zoom'])
        latInitial = float(prevLayout['mapbox.center']['lat'])
        lonInitial = float(prevLayout['mapbox.center']['lon'])
        bearing = float(prevLayout['mapbox.bearing'])

    return go.Figure(
        data=Data([
            Scattermapbox(
                lat=filtered_df['pickup_latitude'],
                lon=filtered_df['pickup_longitude'],
                mode='markers',
                hoverinfo="lat+lon+text",
            )
        ]),
        layout=Layout(
            autosize=True,
            height=500,
            margin=layout.Margin(l=0, r=0, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(
                    lat=latInitial,
                    lon=lonInitial
                ),
                zoom=zoom,
                bearing=bearing
            ),
            updatemenus=[
                dict(
                    buttons=([
                        dict(
                            args=[{
                                'mapbox.zoom': default_zoom,
                                'mapbox.center.lon': '-73.991251',
                                'mapbox.center.lat': '40.7272',
                                'mapbox.bearing': 0
                            }],
                            label='Reset Zoom',
                            method='relayout'
                        )
                    ]),
                    direction='left',
                    pad={'r': 0, 't': 0, 'b': 0, 'l': 0},
                    showactive=False,
                    type='buttons',
                    x=0.45,
                    xanchor='left',
                    yanchor='bottom',
                    borderwidth=1,
                    y=0.02
                )]
        )
    )


@dashapp.callback(
    dash.dependencies.Output('time-slider', 'value'),
    [dash.dependencies.Input('next-button', 'n_clicks')],
    [dash.dependencies.State('time-slider', 'value')])
def update_output(next, value):
    new_value = value + 1

    if new_value > 23:
        new_value = 0
    elif new_value < 0:
        new_value = 23

    return new_value


if __name__ == '__main__':
    dashapp.run_server(8080)
