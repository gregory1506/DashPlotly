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
ref = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/reference.csv")
df["Population"] = np.NaN
tmp = df[df.Date == df.Date.max()].copy()[["Country/Region","Province/State"]]
data = set()
df2 = df.copy()
df2["UID"] = np.NaN
df2["iso2"] = np.NaN
df2["iso3"] = np.NaN
df2["code3"] = np.NaN
df2["FIPS"] = np.NaN
df2["Combined_Key"] = df2["Province/State"].astype(str) + "," + df2["Country/Region"].astype(str)
for row in tmp.itertuples():
    if row[2] is np.NaN:
        uid,iso2,iso3,code3,fips,pop = ref[(ref["Country_Region"] == row[1])][["UID","iso2","iso3","code3","FIPS","Population"]].values[0]
        df2.loc[df2["Country/Region"] == row[1],["UID","iso2","iso3","code3","FIPS","Population"]] = [uid,iso2,iso3,code3,fips,pop]
    else:
        try:
            uid,iso2,iso3,code3,fips,pop = ref[(ref["Country_Region"] == row[1]) & (ref["Province_State"] == row[2])][["UID","iso2","iso3","code3","FIPS","Population"]].values[0]
            df2.loc[(df2["Country/Region"] == row[1]) & (df2["Province/State"] == row[2]),["UID","iso2","iso3","code3","FIPS","Population"]] = [uid,iso2,iso3,code3,fips,pop]
        except:
            continue
df2[(df2.Population.isnull()) & (df2.Date == df2.Date.max())]
df2.drop(df2[(df2["Country/Region"] == "Diamond Princess") | (df2["Province/State"] == "Diamond Princess") ].index,axis=0,inplace=True)
df2.drop(df2[(df2["Country/Region"] == "MS Zaandam") | (df2["Province/State"] == "Grand Princess") ].index,axis=0,inplace=True)
usc = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/us_confirmed.csv")
usd = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/us_deaths.csv")
usc["Population"] = usd.Population
usc.rename(columns={"Case":"Confirmed"},inplace=True)
usc["Deaths"] = usd.Case
usc["Recovered"] = 0.0
usc.Date = pd.to_datetime(usc.Date, format="%Y-%m-%d")
usc.drop(["Admin2"],axis=1,inplace=True)
df2.rename(columns={"Country/Region":"CountryRegion","Province/State":"ProvinceState"},inplace=True)
usc.rename(columns={"Country/Region":"CountryRegion","Province/State":"ProvinceState"},inplace=True)
del df
del usd
df3 = pd.concat([df2,usc]).copy()
df3.drop(df3[df3.Population == 0.0].index,inplace=True)
df3.drop(df3[(df3.CountryRegion == "US") & (df3.ProvinceState.isnull())].index,inplace=True)
del usc
df2["DP100K"] = round(((100000 / df2.Population) * df2.Deaths),3)
df2["CP100K"] = round(((100000 / df2.Population) * df2.Confirmed),3)
df2["RP100K"] = round(((100000 / df2.Population) * df2.Recovered),3)
df2["Mort"] = df2.Deaths / df2.Confirmed * 100.0
df2["Recov"] = df2.Recovered / df2.Confirmed * 100.0

DATES = sorted(df2.Date.unique())
COUNTRIES = df2["CountryRegion"].unique()
COLORS = {"Confirmed":"blue","Recovered":"green","Deaths":"red"}
TOP10OPTIONS = [
    dict(label="Confirmed cases per 100K",value="CP100K"),
    dict(label="Total Confirmed",value="Confirmed"),
    dict(label="Deaths cases per 100K",value="DP100K"),
    dict(label="Mortality Rate",value="Mort"),
    dict(label="Total Deaths",value="Deaths")
]
##############################################################
#                                                            #
#                   L  A  Y  O  U  T                         #
#                                                            #
##############################################################
app.layout = html.Div(
                [
                        html.Div(html.H6("Covid 19 DASHBOARD : {}".format(str(DATES[-1].astype("datetime64[D]"))),
                                                style={"text-align":"center","background-color":"#7242f5"})),
                        html.Div([
                            html.Div([
                                    html.Div(
                                            [
                                                html.H4(id="Confirmed",style={"text-align":"center"}),
                                                html.H6("Confirmed",style={"text-align":"center"})
                                            ],
                                            className="pretty_container",
                                            style={"flex":1}),
                                    
                                    html.Div(
                                            [
                                                html.H4(id="Recovered",style={"text-align":"center"}),
                                                html.H6("Recovered",style={"text-align":"center"})
                                            ],
                                            className="pretty_container",
                                            style={"flex":1}
                                            ),
                                    html.Div(
                                            [
                                                html.H4(id="Deaths",style={"text-align":"center"}),
                                                html.H6("Deaths",style={"text-align":"center"})
                                            ],
                                            className="pretty_container",
                                            style={"flex":1}
                                            ),
                                    html.Div(
                                            [
                                                html.H4(id="Mortality",style={"text-align":"center"}),
                                                html.H6("Mortality",style={"text-align":"center"})
                                            ],
                                            className="pretty_container",
                                            style={"flex":1}
                                            ),
                                    ],
                                    style={"display":"flex","flex":3}
                                    )
                            ],
                            className="ten columns"                              
                        ),
                        html.Div([
                                html.Div([
                                    html.P('Countries'),
                                    dcc.Dropdown(id="country-select",
                                        options=[{'label': i, 'value': i} for i in COUNTRIES],
                                        multi=True
                                    )
                                    ],
                                    className="dcc_control pretty_container two columns",
                                    style={"flex":1}
                                ),
                                html.Div([
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
                                            )
                                    ],
                                    className="dcc_control pretty_container three columns",
                                    style={"flex":1}
                                )
                                ,
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
                                    className="dcc_control pretty_container three columns",
                                    style={"flex":1}
                                )
                            ],
                            className="ten columns",
                            style={"display":"flex","flex":3}
                            ),
                        html.Hr(),
                        html.Div(children=
                                    [
                                    html.Div([
                                            dcc.Graph(id="filled-line-plot")
                                        ],                                                        
                                        className="five columns"
                                    ),
                                    html.Div([
                                            dcc.Graph(id="map-with-covid")
                                        ],
                                        className="six columns"
                                    )                                                    
                                    ],
                                    className="pretty_container twelve columns"
                        ),
                        html.Div([
                            html.Div([
                                html.P("Choose a metric"),
                                dcc.Dropdown(id="top10Bar",
                                            options=TOP10OPTIONS,
                                            value="Confirmed"
                                            ),
                                dcc.Graph(id="top10BarGraph")
                                ],
                                className="pretty_container four columns"
                            ),
                            html.Div([
                                dcc.Graph(id="statsGraph")
                                ],
                                className="pretty_container four columns"
                            ),
                            html.Div([
                                html.P("Disclaimer : Information and displays presented here are for learning purposes only and not\
                                    intended for official reference. Errors may Exist. Data obtained from JHC derivatives here --> \
                                         https://github.com/datasets/covid-19.")
                                ],
                                className="pretty_container four columns"
                            )
                        ],
                        id="tripleContainer",
                        className="twelve columns"
                        )
                ],
                className="mainContainer"
)
                                    
##############################################################
#                                                            #
#            H E L P E R   F U N C T I O N S                 #
#                                                            #
##############################################################

def mapbox_center(country=None):
    df_tmp = df2[df2["CountryRegion"].isin(country)]
    lat = round(df_tmp.Lat.mean(),3)
    lon = round(df_tmp.Long.mean(),3)
    return dict(lat=lat,lon=lon)

def mapbox_zoom(country=None):
    if set(country) == set(COUNTRIES):
        return 0.8
    else:
        return 3.0
   

##############################################################
#                                                            #
#            I  N  T  E  R  A  C  T  I  O  N  S              #
#                                                            #
##############################################################
@app.callback(
        Output("top10BarGraph","figure"),
        [
            Input("top10Bar", "value")
        ]
)
def returnBarGraph(metric="Confirmed"):
    if metric is None:
        metric="Confirmed"
    tmp = df2[df2.Date == df2.Date.max()]
    tmp = tmp.sort_values(by=[metric],na_position="first")[-10:]
    tmp = tmp.sort_values(by=[metric],ascending=False)

    tmp.Combined_Key = list(map(lambda x:x.replace("nan,",""),tmp.Combined_Key.astype(str)))
    tmp.Combined_Key = list(map(lambda x: x.split(",")[0],tmp.Combined_Key))
    fig = go.Figure([go.Bar(x=tmp.Combined_Key,y=tmp[metric])])
    fig.update_layout(title="Top10 countries by {}".format(metric),title_x=0.5)
    return fig

@app.callback(
        Output("statsGraph","figure"),
        [
            Input("date-picker", "date")
        ]
)
def makestatsGraph(date=None):
    fig=go.Figure()
    tmp = df2[df2.Date == df2.Date.max()].copy()
    fig.add_trace(go.Box(y=np.log(tmp.Mort),name="Mortality"))
    fig.add_trace(go.Box(y=np.log(tmp.DP100K + 1),name="Deaths per 100K"))
    fig.add_trace(go.Box(y=np.log(tmp.CP100K + 1),name="Cases per 100K"))
    fig.update_layout(title="Box Plots",title_x=0.5,yaxis=dict(title="Logarithmic scale"))
    return fig

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
                df_tmp = df3[(df3.Date == date) & (df3[case] > 0) & (df3["CountryRegion"].isin(country))]
                fig.add_trace(go.Scattermapbox(
                                        lat=df_tmp.Lat,
                                        lon=df_tmp.Long,
                                        mode="markers",
                                        marker=go.scattermapbox.Marker(
                                                size=df_tmp[case] ** (1/3),
                                                color=COLORS[case],
                                                opacity=0.7
                                        ),
                                        text=df_tmp["CountryRegion"] + "," +df_tmp["ProvinceState"] + "<br>" "{} : ".format(case) + df_tmp[case].astype(str),
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
        tmp = df2[(df2.Date.isin(DATES[:DATES.index(date)])) & (df2.Confirmed > 0) & (df2["CountryRegion"].isin(country))]
        tmp = tmp.groupby(["Date"]).agg(sum).copy()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Deaths,fill='tozeroy',fillcolor="red",mode='none',name="Deaths"))
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Recovered,fill='tonexty',fillcolor="green",mode='none',name="Recovered"))
        fig.add_trace(go.Scatter(x=tmp.index,y=tmp.Confirmed,fill='tonexty',fillcolor="blue",mode='none',name="Confirmed"))
        fig.update_layout(title="Cumulative Cases over Time",title_x=0.5,showlegend=True,xaxis=dict(title="Progression of Outbreak (Date)")\
                          ,yaxis=dict(title="Number of cases"))
        return fig

@app.callback(
        Output("Mortality","children"),
        [
                Input("country-select","value"),
                Input("date-picker", "date")
        ]
)
def calc_Mortality(country=None,date=None):
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
        tmp = df2[(df2.Date == date) & (df2.Mort > 0) & (df2["CountryRegion"].isin(country))].copy()
        b = tmp.groupby(["Date"]).agg(sum).copy()["Confirmed"][0]
        a = tmp.groupby(["Date"]).agg(sum).copy()["Deaths"][0]
        return str(round(a/b*100.0,3))+"%"

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
        tmp = df2[(df2.Date == date) & (df2.Confirmed > 0) & (df2["CountryRegion"].isin(country))].copy()
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
        tmp = df2[(df2.Date == date) & (df2.Recovered > 0) & (df2["CountryRegion"].isin(country))].copy()
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
        tmp = df2[(df2.Date == date) & (df2.Deaths > 0) & (df2["CountryRegion"].isin(country))].copy()
        return str(tmp.groupby(["Date"]).agg(sum).copy()["Deaths"][0])
##############################################################
#                                                            #
#                      M  A  I  N                            #
#                                                            #
##############################################################

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
