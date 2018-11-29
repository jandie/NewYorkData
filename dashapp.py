import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask


def get_seconds(time_delta):
    return time_delta.total_seconds()


# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = Flask(__name__)

dashapp = dash.Dash(__name__,
                    server=app,
                    external_stylesheets=external_stylesheets)

mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'
default_hour = 0
default_zoom = 12

df = pd.read_csv('small_taxi.csv')

df = df.loc[df['total_amount'] < 80]
df = df.loc[(df['pickup_latitude'] > 40) &
            (df['pickup_latitude'] < 42) &
            (df['pickup_longitude'] > -80) &
            (df['pickup_longitude'] < -71)]

df = df.loc[(df['dropoff_latitude'] > 40) &
            (df['dropoff_latitude'] < 42) &
            (df['dropoff_longitude'] > -80) &
            (df['dropoff_longitude'] < -71)]

df = df.loc[(df['rate_code'] >= 1) & (df['rate_code'] <= 6)]

df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')

df['duration'] = df['dropoff_datetime'] - df['pickup_datetime']
df['duration'] = df['duration'].apply(get_seconds)

df = df.loc[(df['duration'] > 0) & (df['duration'] <= 10000)]
df = df.loc[(df['trip_distance'] > 0) & (df['trip_distance'] <= 60)]

df['avg_speed'] = df['trip_distance'] / (df['duration'] / 3600)

df = df.loc[(df['avg_speed'] > 0) & (df['avg_speed'] <= 60)]

df['month'] = df['pickup_datetime'].dt.month

dashapp.layout = html.Div([
    html.Div(id='prev-button-value', style={'display': 'none'}),
    html.Div(id='next-button-value', style={'display': 'none'}),

    html.H1(children='New York City - Yellow Cab data 2014',
            style={"text-align": "center"}),

    html.Div(children="By Jandie Hendriks",
             style={"text-align": "center",
                    "margin-bottom": "20px"}),
    html.Div(
        dcc.Dropdown(
            id='color-dropdown',
            options=[
                {'label': 'Total amount', 'value': 'total_amount'},
                {'label': 'Fare amount', 'value': 'fare_amount'},
                {'label': 'Trip distance', 'value': 'trip_distance'},
                {'label': 'Tip amount', 'value': 'tip_amount'},
                {'label': 'Average speed', 'value': 'avg_speed'},
                {'label': 'Duration', 'value': 'duration'},
                {'label': 'Month', 'value': 'month'},
                {'label': 'Passenger count', 'value': 'passenger_count'},
            ],
            value='total_amount'
        ), style={"margin-bottom": "30px"}),

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

    html.Button('Next hour',
                id='next-button',
                style={"margin-bottom": "20px"}),
])


@dashapp.callback(
    Output('my-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('color-dropdown', 'value')],
    [State('my-graph', 'relayoutData')]
)
def update_output_div(input_value, color_value, prevLayout):
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
                text=filtered_df[color_value],
                hoverinfo="lat+lon+text",
                marker=dict(
                    colorscale='YlOrRd',
                    reversescale=True,
                    autocolorscale=False,
                    color=filtered_df[color_value],
                    cmin=filtered_df[color_value].min(),
                    cmax=filtered_df[color_value].max(),
                    colorbar=dict(
                        x=0.935,
                        xpad=0,
                        tick0=0
                    ),
                )
            )
        ]),
        layout=Layout(
            autosize=True,
            height=600,
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
            )
        )
    )


@dashapp.callback(
    dash.dependencies.Output('time-slider', 'value'),
    [Input('next-button', 'n_clicks')],
    [State('time-slider', 'value')])
def update_output(next, value):
    new_value = value + 1

    if new_value > 23:
        new_value = 0
    elif new_value < 0:
        new_value = 23

    return new_value


if __name__ == '__main__':
    dashapp.run_server(8080)
