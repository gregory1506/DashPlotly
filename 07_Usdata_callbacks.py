#basic imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import plotly.graph_objects as go  

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)


##############################################################
#                                                            #
#             D  A  T  A     L  O  A  D  I  N  G             #
#                                                            #
##############################################################
MAPBOX_TOKEN = 'pk.eyJ1IjoiZ3JvbDIwMjAiLCJhIjoiY2s4bnVxeDk0MTI5MDNqbzJ3N212d3JvNSJ9.g2Pe3QhqbcfGOedTchNgCw'
df = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv")
df.Date = pd.to_datetime(df.Date,format="%Y-%m-%d")
DATES = sorted(df.Date.unique())
COUNTRIES = df["Country/Region"].unique()

##############################################################
#                                                            #
#                   L  A  Y  O  U  T                         #
#                                                            #
##############################################################
app.layout = html.Div(children=
                [
                        html.Div(children=html.H2(children="Covid 19 DASHBOARD : {}".format(str(DATES[-1].astype("datetime64[D]"))),
                                                style={"text-align":"center","background-color":"#7242f5"})),
                        html.Div(children=
                                [
                                html.P('Countries'),
                                dcc.Dropdown(id="country-select",
                                        options=[{'label': i, 'value': i} for i in df["Country/Region"].unique()],
                                        multi=True
                                        )
                                ],
                                className="two columns"
                        ),
                        html.Div(children=
                                [
                                dcc.Graph(id="map-with-covid"),
                                dcc.Graph(id="filled-line-plot")
                                ],
                                className="seven columns"
                        ),
                        html.Div(children=
                                [
                                html.Div([html.H4(id="Confirmed"),html.P("Confirmed")],
                                        style={"background-color":"#4269f5","text-align":"center"}),
                                html.Div([html.H4(id="Recovered"),html.P("Recovered")],
                                        style={"background-color":"green","text-align":"center"}),
                                html.Div([html.H4(id="Deaths"),html.P("Deaths")],
                                        style={"background-color":"red","text-align":"center"})
                                ],
                                className="two columns"
                        ),     
                        # html.Div(html.H2("End of page",style={"text-align":"center","background-color":"#7242f5"}))
                ],
                # className="container"
        )
##############################################################
#                                                            #
#            I  N  T  E  R  A  C  T  I  O  N  S              #
#                                                            #
##############################################################
@app.callback(
        Output("map-with-covid","figure"),
        [
                Input("country-select","value")
        ]
)
def make_covid_map(country):
        if country is None or country == []:
                country = COUNTRIES
        date = DATES[-1]
        df_tmp = df[(df.Date == date) & (df.Confirmed > 0)]
        return {"data" : [go.Scattermapbox(
                                lat=df_tmp.Lat,
                                lon=df_tmp.Long,
                                mode="markers",
                                marker=go.scattermapbox.Marker(
                                        size=df_tmp.Confirmed ** (1/3),
                                        color="red",
                                        opacity=0.7
                                ),
                                text=df_tmp["Country/Region"] + " " + "Confirmed : " + df_tmp["Confirmed"].astype(str),
                                hoverinfo="text"
                                )
                        ],
                "layout" : go.Layout(
                                hovermode="closest",
                                autosize=True,
                                mapbox={"accesstoken":MAPBOX_TOKEN,
                                        "center":dict(lat=20,lon=-5),
                                        "zoom":0.75
                                        },
                                margin=dict(r=0,l=0,t=0,b=0,pad=0)
                                )
        }


@app.callback(
        Output("filled-line-plot","figure"),
        [
                Input("country-select","value")
        ]
)
def make_line_plot(country):
        if country is None or country == []:
                country = COUNTRIES
        tmp = df.groupby(["Date"]).agg(sum).copy()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Deaths,fill='tozeroy',fillcolor="red",mode='none',name="Deaths"))
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Recovered,fill='tonexty',fillcolor="green",mode='none',name="Recovered"))
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Confirmed,fill='tonexty',fillcolor="blue",mode='none',name="Confirmed"))
        fig.update_layout(showlegend=True,xaxis=dict(title="Progression of Outbreak (Date)"),yaxis=dict(title="Number of cases"))
        return fig


@app.callback(
        Output("Confirmed","children"),
        [
                Input("country-select","value")
        ]
)
def calc_Confirmed(country):
        tmp = df.groupby(["Date"]).agg(sum).copy()
        return str(tmp.loc[df.Date.max()]["Confirmed"])

@app.callback(
        Output("Recovered","children"),
        [
                Input("country-select","value")
        ]
)
def calc_Confirmed(country):
        tmp = df.groupby(["Date"]).agg(sum).copy()
        return str(tmp.loc[df.Date.max()]["Recovered"])

@app.callback(
        Output("Deaths","children"),
        [
                Input("country-select","value")
        ]
)
def calc_Confirmed(country):
        tmp = df.groupby(["Date"]).agg(sum).copy()
        return str(tmp.loc[df.Date.max()]["Deaths"])
##############################################################
#                                                            #
#                      M  A  I  N                            #
#                                                            #
##############################################################

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
