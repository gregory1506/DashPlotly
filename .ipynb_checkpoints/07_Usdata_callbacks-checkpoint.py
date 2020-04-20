#basic imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import plotly.graph_objects as go  
import requests as rq
import json

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True

##############################################################
#                                                            #
#             D  A  T  A     L  O  A  D  I  N  G             #
#                                                            #
##############################################################
MAPBOX_TOKEN = 'pk.eyJ1IjoiZ3JvbDIwMjAiLCJhIjoiY2s4bnVxeDk0MTI5MDNqbzJ3N212d3JvNSJ9.g2Pe3QhqbcfGOedTchNgCw'
df = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv")
df.Date = pd.to_datetime(df.Date,format="%Y-%m-%d")
df["Population"] = np.NaN
# df4 = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/us_confirmed.csv")
# df5 = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/us_deaths.csv")
# df4.rename(columns={"Case":"Confirmed"},inplace=True)
# df4["Deaths"] =df5.Case
# df4["Population"] = df5.Population
# df4["Recovered"] = 0.0
# df6 = df4[["Date","Lat","Long","Confirmed","Recovered","Deaths","Country/Region","Province/State","Population"]].copy()
# df6.Date = pd.to_datetime(df6.Date, format="%Y-%m-%d")
# df7 = pd.concat([df,df6]).copy()
cinfo = rq.get("https://raw.githubusercontent.com/gregory1506/DashPlotly/master/test.json").json()
df2 = df.copy()
df2["Region"] = np.nan
df2["Sub-Region"] = np.nan
df2["ISO3"] = np.nan
countries = df["Country/Region"].unique()
for country in countries:
    if country in cinfo:
        df2.loc[df2["Country/Region"] == country,["Population","Region","Sub-Region","ISO3"]] = cinfo[country][:]
# df8.drop(df8[(df8["Country/Region"] == "US") & (df8["Province/State"].isnull())].index,inplace=True)
DATES = sorted(df2.Date.unique())
COUNTRIES = df2["Country/Region"].unique()
COLORS = {"Confirmed":"red","Recovered":"green","Deaths":"blue"}
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
                                        ),
                                html.P('Case Type'),
                                dcc.RadioItems(
                                        id = "case-select",
                                        options=[
                                        {'label': 'Confirmed', 'value': 'Confirmed'},
                                        {'label': 'Recovered', 'value': 'Recovered'},
                                        {'label': 'Deaths', 'value': 'Deaths'},
                                        {'label': 'All', 'value': 'All'}
                                        ],
                                        value='Confirmed',
                                        labelStyle={'display': 'inline-block'},
                                        ),
                                html.Div(children=[
                                         html.P("Choose Date : Default is Latest date"),
                                        dcc.DatePickerSingle(
                                        id="date-picker",
                                        min_date_allowed=str(df2.Date.min())[:10],
                                        max_date_allowed=str(df2.Date.max())[:10],
                                        initial_visible_month=str(df2.Date.max())[:10],
                                        date=str(df2.Date.max())[:10],
                                        display_format="D MMMM, YYYY",
                                        style={"border": "0px solid black"},
                                                ),
                                        ],
                                        className="dcc_control"
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
#            H E L P E R   F U N C T I O N S                 #
#                                                            #
##############################################################

def mapbox_center(country=None):
    df_tmp = df2[df2["Country/Region"].isin(country)]
    lat = round(df_tmp.Lat.mean(),3)
    lon = round(df_tmp.Long.mean(),3)
    return dict(lat=lat,lon=lon)

def mapbox_zoom(country=None):
    if set(country) == set(COUNTRIES):
        return 1.07
    else:
        return 3.0

##############################################################
#                                                            #
#            I  N  T  E  R  A  C  T  I  O  N  S              #
#                                                            #
##############################################################
@app.callback(
        Output("map-with-covid","figure"),
        [
                Input("country-select","value"),
                Input("date-picker", "date"),
                Input("case-select","value")
        ]
)
def make_covid_map(country=None,date=None,cases=None):
        if cases is None:
            cases = list(("Confirmed",))
        elif type(cases) == str:
            if cases == "All":
                cases = ["Confirmed","Recovered","Deaths"]
            else:
                cases = list((cases,))
        else:
            pass
        if country is None or country == []:
            country = COUNTRIES
        elif type(country) == str:
            country = list((country,))
        elif type(country) == list:
            pass
        else:
            print("Only lists or single string accepted for country")
        if date is None:
            date = DATES[-1]
        else:
            date = np.datetime64(date)
        fig = go.Figure()
        for case in cases:
                df_tmp = df2[(df2.Date == date) & (df2[case] > 0) & (df2["Country/Region"].isin(country))]
                fig.add_trace(go.Scattermapbox(
                                        lat=df_tmp.Lat,
                                        lon=df_tmp.Long,
                                        mode="markers",
                                        marker=go.scattermapbox.Marker(
                                                size=df_tmp[case] ** (1/3),
                                                color=COLORS[case],
                                                opacity=0.7
                                        ),
                                        text=df_tmp["Country/Region"] + "," +df_tmp["Province/State"] + f"<br>" "{case} : " + df_tmp[case].astype(str),
                                        hoverinfo="text",
                                        name=case
                                        )
                                )
        fig.update_layout(hovermode="closest",
                autosize=True,
                mapbox={"accesstoken":MAPBOX_TOKEN,
                        "center":mapbox_center(country),
                        "zoom":mapbox_zoom(country)
                        },
                legend={"y":0.5},
                showlegend=True,
                margin=dict(r=0,l=0,t=0,b=0,pad=0)
                )
        return fig


@app.callback(
        Output("filled-line-plot","figure"),
        [
                Input("country-select","value"),
                Input("date-picker", "date")
        ]
)
def make_line_plot(country=None,date=None):
        if country is None or country == []:
            country = COUNTRIES
        elif type(country) == str:
            country = list((country,))
        elif type(country) == list:
            pass
        else:
            print("Only lists or single string accepted for country")
        if date is None:
            date = DATES[-1]
        else:
            date = np.datetime64(date)
        tmp = df2[(df2.Date.isin(DATES[:DATES.index(date)])) & (df2.Confirmed > 0) & (df2["Country/Region"].isin(country))]
        tmp = tmp.groupby(["Date"]).agg(sum).copy()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Deaths,fill='tozeroy',fillcolor="red",mode='none',name="Deaths"))
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Recovered,fill='tonexty',fillcolor="green",mode='none',name="Recovered"))
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Confirmed,fill='tonexty',fillcolor="blue",mode='none',name="Confirmed"))
        fig.update_layout(showlegend=True,xaxis=dict(title="Progression of Outbreak (Date)"),yaxis=dict(title="Number of cases"))
        return fig


@app.callback(
        Output("Confirmed","children"),
        [
                Input("country-select","value"),
                Input("date-picker", "date")
        ]
)
def calc_Confirmed(country=None,date=None):
        if country is None or country == []:
            country = COUNTRIES
        elif type(country) == str:
            country = list((country,))
        elif type(country) == list:
            pass
        else:
            print("Only lists or single string accepted for country")
        if date is None:
            date = DATES[-1]
        else:
            date = np.datetime64(date)
        tmp = df2[(df2.Date == date) & (df2.Confirmed > 0) & (df2["Country/Region"].isin(country))].copy()
        return str(tmp.groupby(["Date"]).agg(sum).copy()["Confirmed"][0])

@app.callback(
        Output("Recovered","children"),
        [
                Input("country-select","value"),
                Input("date-picker", "date")
        ]
)
def calc_Recovered(country=None,date=None):
        if country is None or country == []:
            country = COUNTRIES
        elif type(country) == str:
            country = list((country,))
        elif type(country) == list:
            pass
        else:
            print("Only lists or single string accepted for country")
        if date is None:
            date = DATES[-1]
        else:
            date = np.datetime64(date)
        tmp = df2[(df2.Date == date) & (df2.Recovered > 0) & (df2["Country/Region"].isin(country))].copy()
        return str(tmp.groupby(["Date"]).agg(sum).copy()["Recovered"][0])

@app.callback(
        Output("Deaths","children"),
        [
                Input("country-select","value"),
                Input("date-picker", "date")
        ]
)
def calc_Deaths(country=None,date=None):
        if country is None or country == []:
            country = COUNTRIES
        elif type(country) == str:
            country = list((country,))
        elif type(country) == list:
            pass
        else:
            print("Only lists or single string accepted for country")
        if date is None:
            date = DATES[-1]
        else:
            date = np.datetime64(date)
        tmp = df2[(df2.Date == date) & (df2.Deaths > 0) & (df2["Country/Region"].isin(country))].copy()
        return str(tmp.groupby(["Date"]).agg(sum).copy()["Deaths"][0])
##############################################################
#                                                            #
#                      M  A  I  N                            #
#                                                            #
##############################################################

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
