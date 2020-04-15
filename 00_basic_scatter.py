#basic imports
import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import plotly.offline as po
import plotly.graph_objects as go  

df = pd.read_csv("https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv")
df.Date = pd.to_datetime(df.Date)

dates = sorted(df.Date.unique())

df_tmp = df[(df.Date == dates[0]) & (df.Confirmed > 0)]
data = [go.Scatter(x=df_tmp.Lat, y=df_tmp.Long, mode="markers",text=df_tmp["Country/Region"]),
        go.Scatter(x=df_tmp.Lat, y=df_tmp.Long-20, mode="markers",text=df_tmp["Country/Region"])]
layout = go.Layout(title="Latitude vs Longtitude",
                    xaxis={"title":"Latitude","range":[-80,80]},
                    yaxis={"title":"Longitude","range":[-170,170]},
                    hovermode="closest")
fig = go.Figure(data=data,layout=layout)
po.plot(fig,filename="Lat_vs_long.html")
