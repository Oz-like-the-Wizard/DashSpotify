import pandas as pd 
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_table
#import time


df = pd.read_csv("data.csv")
df = df.loc[df["Position"]<11]
df['Date'] = df['Date'].astype('datetime64[ns]')
df_ready = df.groupby(["Date","Region","Track Name","Artist","Position"])[['danceability', 'energy', 'instrumentalness', 'valence','acousticness', 'liveness', 'speechiness',"tempo","duration_ms","Streams"]].agg("mean").reset_index()


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


# Initialize the app
app = dash.Dash(__name__)

marks_1 = {}
for i in range(1,11):
    marks_1[i] = str(i)

dropdown_1 = dcc.Dropdown(id='dropdown1', options=get_options(df['Region'].unique()),multi=True, value=[df['Region'].sort_values()[0]],style={'backgroundColor': '#1E1E1E',"fontColor":"#1DB954"})
slider_1 = dcc.RangeSlider(
                id='slider1',
                min = 1,
                max = 10,
                value = [1,10],
                marks = marks_1
            )

text_inp_1 = dcc.Input(id="input1", type="text", value="" ,placeholder="Please input musician name",debounce=True)
text_inp_2 = dcc.Input(id="input2", type="text", value="" ,placeholder="Please input track name",debounce=True)


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
                                     dropdown_1
                                 ]),
                                 html.P('Do song attributes change with the ranking? Top ranks are all about the hype, what about the lower ranks, do they tell you anything about your country?'),
                                 html.Div(children=[
                                     slider_1
                                 ]),
                                 html.P('Want to see the attributes of your favorite musician? Just type in the name below and hit Enter!'),
                                 html.Div(children=[
                                     text_inp_1,
                                     text_inp_2
                                 ])

                                ]
                             ),
                    html.Div(className='seven columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='graph-output-2', figure={}),
                                 dcc.Graph(id='graph-output', figure={}),
                                 
                                 ])
        ]

)
    ]
)
@app.callback(Output('graph-output', 'figure'),
                [Input('dropdown1', 'value'),
                Input('slider1', 'value'),
                ]
              )

def update_graph(selected_dropdown,selected_range):
    dff = df_ready
    # Country name input filter

    if len(selected_dropdown) > 0:
        dff = df_ready
        dff = dff.loc[dff["Region"].isin(selected_dropdown)]

    else:
        dff = df_ready

# Range slider filter
    dff = dff.loc[(dff["Position"] >= int(selected_range[0])) & (dff["Position"] <= int(selected_range[1]))]

    dff = dff.groupby(["Region","Date"]).agg("mean").reset_index()
    dff_weekly = dff.reset_index().resample('W-Wed', label='right', closed = 'right', on='Date').mean().reset_index().sort_values(by='Date').set_index("Date").drop(["tempo","duration_ms","index","Position","Streams"],axis=1)
    
    fig = px.bar(dff_weekly, x=dff_weekly.index,y=dff_weekly.columns,title="Song attributes over time")

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_color="#1DB954",
                font_color="white",
                xaxis_showgrid=False, 
                yaxis_showgrid=False)
    return fig


@app.callback(Output('graph-output-2', 'figure'),
                [Input('dropdown1', 'value'),
                Input('slider1', 'value'),
                Input('input1', 'value'),
                Input('input2', 'value'),
                ]
              )

def update_graph2(selected_dropdown,selected_range,musician_name,track_name):
    dff = df_ready
    if len(selected_dropdown) == 0:
        dff = df_ready
# Country name input filter
    else:
        dff = df_ready
        dff = dff.loc[dff["Region"].isin(selected_dropdown)]
# Artist name input filter
    if musician_name != "":
        dff = dff.loc[dff["Artist"].str.lower()== str.lower(musician_name)]
# Track name input filter
    if track_name != "":
        dff = dff.loc[dff["Track Name"].str.lower() == str.lower(track_name)]
# Range slider filter
    dff = dff.loc[(dff["Position"] >= int(selected_range[0])) & (dff["Position"] <= int(selected_range[1]))]

    dff = dff.groupby(["Region","Date"]).agg("sum").reset_index()
    dff_weekly = dff.reset_index().resample('W-Wed', label='right', closed = 'right', on='Date').sum().reset_index().sort_values(by='Date').set_index("Date").drop(["tempo","duration_ms","index","Position"],axis=1)
    
    fig2 = px.line(dff_weekly, x=dff_weekly.index,y=dff_weekly["Streams"], title="Total streams over time")

    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_color="#1DB954",
                font_color="white",
                xaxis_showgrid=False, 
                yaxis_showgrid=False
               )

    fig2.update_traces(line_color="#1DB954")            
    return fig2

if __name__ == '__main__':
    app.run_server(debug=True)

