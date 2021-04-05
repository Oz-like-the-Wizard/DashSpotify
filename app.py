import pandas as pd 
#import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_table
import time


df = pd.read_csv("dashboard/data/data.csv")
df = df.loc[df["Position"]<11]
df['Date'] = df['Date'].astype('datetime64[ns]')
df_ready = df.groupby(["Date","Region","Track Name","Artist","Position"])[['danceability', 'energy', 'instrumentalness', 'valence','acousticness', 'liveness', 'speechiness',"tempo","duration_ms","Streams"]].agg("mean").reset_index()

# GRAPH 1
#df_1 = df_ready.groupby(["Region","Date"]).agg("mean").reset_index().set_index("Date")
#df_1_w = df_1.reset_index().resample('W-Wed', label='right', closed = 'right', on='Date').mean().reset_index().sort_values(by='Date').set_index("Date")
#
#fig = px.line(df_1_w, x=df_1_w.index,y=df_1_w.columns)
#
#fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
#    plot_bgcolor='rgba(0,0,0,0)',
#    title_font_color="#1DB954",
#    font_color="white")
# GRAPH 2

#df_3 = df_ready.loc[df_ready["Track Name"].isin(input) | df_ready["Artist"].isin(input)].groupby("Date").mean().iloc[0,:7]
#
#fig_2 = px.line_polar(
#                    r=df_3.values,
#                    theta=df_3.index,
#                    line_close=True,
#                    range_r = [0,1.0],
#                    title="Average attributes of - %s"%input[0],
#                    direction="counterclockwise", start_angle=45
#                    )
#
#fig_2.update_traces(fill='toself',fillcolor="#1DB954", opacity=0.6, line=dict(color="#1DB954"))
#
#fig_2.update_layout(paper_bgcolor='rgba(0,0,0,0)',
#    plot_bgcolor='rgba(0,0,0,0)',
#    title_font_color="#1DB954",
#    font_color="white")

def get_options(options):
    dict_list = []
    for i in options:
        dict_list.append({'label': i, 'value': i})

    return dict_list


# TABLE 1

#df_2 = df_ready.groupby(["Date","Region","Track Name","Artist"]).sum()["Streams"].reset_index().set_index("Date")
#df_2 = df_2.loc[df_2["Region"].isin(country)].iloc[:,1:].head(20)

# Initialize the app
app = dash.Dash(__name__)



dropdown_1 = dcc.Dropdown(id='dropdown1', options=get_options(df['Region'].unique()),multi=True, value=[df['Region'].sort_values()[0]],style={'backgroundColor': '#1E1E1E',"fontColor":"#1DB954"})
slider_1 = dcc.RangeSlider(
                id='slider1',
                min = 1,
                max = 10,
                value = [1,
                         10]
            )


app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='five columns div-user-controls',
                             children=[
                                 html.H2('Spotify Streams'),
                                 html.P('What kinds of songs did Europe listen? Were they energetic or lowkey? What kind of music people tend to listen on special occasions?'),
                                 html.P('To learn about all this and more, please select a country!'),
                                 html.Div(children=[
                                     dropdown_1,
                                     slider_1
                                 ])
                                 #dash_table.DataTable(id='table', columns=[{"name": i, "id": i} for i in df_2.columns],data=df_2.to_dict('records'),
        #style_data={
         #   'backgroundColor': 'transparent'
      #  })

                                ]
                             ),
                    html.Div(className='seven columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='graph-output', figure={})                            ])
                              ])
        ]

)

@app.callback(Output('graph-output', 'figure'),
                [Input('slider1', 'value'),
                Input('dropdown1', 'value')]
              )

def update_graph(selected_range,selected_dropdown):
    dff = df_ready
    dff = dff.loc[dff["Region"].isin(selected_dropdown)]
    dff = dff.loc[(dff["Position"] >= selected_range[0]) & (dff["Position"] <= selected_range[1])]

    df_1 = dff.groupby(["Region","Date"]).agg("mean").reset_index()
    df_1_w = df_1.reset_index().resample('W-Wed', label='right', closed = 'right', on='Date').mean().reset_index().sort_values(by='Date').set_index("Date").drop(["tempo","duration_ms","Streams","index","Position"],axis=1)
    fig = px.line(df_1_w, x=df_1_w.index,y=df_1_w.columns,title="Song attributes over time")

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font_color="#1DB954",
            font_color="white")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


