#basic imports
import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import plotly.offline as po
import plotly.graph_objects as go  

MAPBOX_TOKEN = 'pk.eyJ1IjoiZ3JvbDIwMjAiLCJhIjoiY2s4bnVxeDk0MTI5MDNqbzJ3N212d3JvNSJ9.g2Pe3QhqbcfGOedTchNgCw'

df = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv")
df.Date = pd.to_datetime(df.Date)
dates = sorted(df.Date.unique())

df_tmp = df[(df.Date == dates[-1]) & (df.Confirmed > 0)]
data = [go.Scattermapbox(lat=df_tmp.Lat,
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
        ]
layout = go.Layout(title="COVID 19 Confirmed cases as of {}"\
                        .format(str(dates[-1].astype("datetime64[D]"))),
                hovermode="closest",
                autosize=True,
                mapbox={"accesstoken":MAPBOX_TOKEN,
                        "center":dict(lat=10,lon=-5),
                        "zoom":1.05
                        },
                # margin=dict(r=0,l=0,t=0,b=0,pad=100)
                )


fig = go.Figure(data=data,layout=layout)
po.plot(fig,filename="mapbox1.html")