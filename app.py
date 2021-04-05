import pandas as pd 
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_table as dt
from datetime import date



df = pd.read_csv("data.csv")
df = df.loc[df["Position"]<11]
df['Date'] = df['Date'].astype('datetime64[ns]')
df_ready = df.groupby(["Date","Region","Track Name","Artist","Position"])[['danceability', 'energy', 'instrumentalness', 'valence','acousticness', 'liveness', 'speechiness',"tempo","duration_ms","Streams"]].agg("mean").reset_index()


def get_options(options):
    dict_list = []
    for i in options:
        dict_list.append({'label': i, 'value': i})

    return dict_list


# Initialize the app
app = dash.Dash(__name__)
server = app.server

# Create dash components so the layout will be less crowded
marks_1 = {}
for i in range(1,11):
    marks_1[i] = str(i)

dropdown_1 = dcc.Dropdown(id='dropdown1', options=get_options(df_ready['Region'].unique()),multi=True, value=list(),style={'backgroundColor': '#1E1E1E',"fontColor":"#1DB954"})
slider_1 = dcc.RangeSlider(
                id='slider1',
                min = 1,
                max = 10,
                value = [1,10],
                marks = marks_1
            )
dropdown_2 = dcc.Dropdown(id='dropdown2', options=get_options(df_ready['Artist'].unique()),multi=True, value=list(),style={'backgroundColor': '#1E1E1E',"fontColor":"#1DB954"})
dropdown_3 = dcc.Dropdown(id='dropdown3', options=get_options(df_ready['Track Name'].unique()),multi=True, value=list(),style={'backgroundColor': '#1E1E1E',"fontColor":"#1DB954"})


date_picker = dcc.DatePickerRange(id='date',start_date=date(2017,1,1),end_date=date(2018,1,1),calendar_orientation='horizontal',clearable=True,with_portal=True, min_date_allowed=date(2017, 1, 1),
        max_date_allowed=date(2018, 6, 6),style={'background-color': '#000000'})


# App layout

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='five columns div-user-controls',
                             children=[
                                 html.Div(date_picker,style={'background-color': 'transparent',"fontColor":"#1DB954","margin-left" : "5px"}),
                                 html.Br(),
                                 html.Br(),
                                 html.H1('Spotify Streams', style={"color":"1DB954"}),
                                 html.Br(),
                                 html.P('What type of songs did Europe listen in 2017? Were they energetic, danceable or lowkey? Does seasonality affect our song preferences?'),
                                 html.P('This dashboard contains data from Daily Top 10 charts for European countries in 2017. You can view the total streams across the year, their average attributes accoring to Spotify and how these attributes changed throughout the year!'),
                                 html.Br(),
                                 html.P("Select a country code from the list to filter their streams:"),
                                 html.Br(),
                                 html.Div(children=[
                                     dropdown_1
                                 ],style={"margin-left": "15px"}),
                                 html.Br(),
                                 html.P("Country Top 10 Charts"),
                                 html.Br(),
                                 html.P("Is there a difference in attributes between the top and bottom songs of a country's Top 10 chart? Or do different countries have a different taste when it comes to their Number 1 song?"),
                                 html.Br(),
                                 html.P("Use the slider below to select between the rankings of the Top 10 charts and filter down to a position in the chart."),
                                 html.Div(children=[
                                     slider_1
                                 ],style={"margin-left": "15px"}),
                                 html.Br(),
                                 html.P("Artists"),
                                 html.Br(),
                                 html.P("How about your favorite artist, how would Spotify describe their songs? The dropdown lists below contains all the artists and songs that have made it to a European country's Daily Top 10 list."),                                 
                                 html.Br(),
                                 html.P("Search and select a name or song from the list to view their performance across the year as well as what Spotify thinks of their songs!"),
                                 html.Div(children=[
                                     dropdown_2,
                                 ],style={"margin-left": "15px"}),
                                 html.Br(),
                                 html.Div(children=[
                                     dropdown_3
                                 ],style={"margin-left": "15px"}),
                                 html.Br(),
                                 html.Br(),
                                 html.P("For data sources and additional information, please refer to: https://github.com/Spidey0023/DashSpotify")
                                                                    



                                ]
                             ),
                    html.Div(className='seven columns div-for-charts bg-grey',
                             children=[
                                 html.Div(id = "total-str",children=["init"],style={"font-size": "15px"}),
                                 html.Div(id = "total-artists",children=["init"],style={"font-size": "15px"}),
                                 html.Div(id = "total-songs",children=["init"],style={"font-size": "15px"}),
                                 dcc.Graph(id='graph-output-2', figure={}),
                                 html.Div(children=[
                                     dcc.Graph(id='graph-output-3', figure={}),                                     
                                     dcc.Graph(id='graph-output', figure={})



                                 ])
                                 
                                 ])
        ]

)
,html.Div(children=[html.Div(className='five columns div-user-controls'),
html.Div(className='seven columns div-for-charts bg-grey')])

    ])

@app.callback(Output('graph-output', 'figure'),
                [Input('dropdown1', 'value'),
                Input('slider1', 'value'),
                Input('date', 'start_date'),
                Input('date', 'end_date')
                ]
              )

def update_graph(selected_dropdown,selected_range,start_date,end_date):
    
    dff = df_ready

# Date filter
    if (start_date is not None):
        if (end_date is not None):
            dff = dff.loc[(dff["Date"]>start_date) & (dff["Date"]<end_date)]
        else:
            dff = dff.loc[(dff["Date"]>start_date)]
    elif (end_date is not None):
        dff = dff.loc[(dff["Date"]<end_date)]


# Country name input filter
    if len(selected_dropdown) != 0:
        dff = dff.loc[dff["Region"].isin(selected_dropdown)]
    else:
        dff = dff

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
                Input('dropdown2', 'value'),
                Input('dropdown3', 'value'),
                Input('date', 'start_date'),
                Input('date', 'end_date')
                ]
              )

def update_graph2(selected_dropdown,selected_range,musician_name,track_name,start_date,end_date):

    dff = df_ready

# Date filter
    if (start_date is not None):
        if (end_date is not None):
            dff = dff.loc[(dff["Date"]>start_date) & (dff["Date"]<end_date)]
        else:
            dff = dff.loc[(dff["Date"]>start_date)]
    elif (end_date is not None):
        dff = dff.loc[(dff["Date"]<end_date)]

# Country name input filter
    if len(selected_dropdown) != 0:
        dff = dff.loc[dff["Region"].isin(selected_dropdown)]
    else:
        dff = dff

# Artist name input filter
    if len(musician_name) > 0:
        dff = dff.loc[dff["Artist"].isin(musician_name)]
    
# Track name input filter
    if len(track_name) > 0:
        dff = dff.loc[dff["Track Name"].isin(track_name)]

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


@app.callback(Output('graph-output-3', 'figure'),
                [Input('dropdown1', 'value'),
                Input('slider1', 'value'),
                Input('dropdown2', 'value'),
                Input('dropdown3', 'value'),
                Input('date', 'start_date'),
                Input('date', 'end_date')
                ]
              )



def update_graph3(selected_dropdown,selected_range,musician_name,track_name,start_date,end_date):

    dff = df_ready

# Date filter
    if (start_date is not None):
        if (end_date is not None):
            dff = dff.loc[(dff["Date"]>start_date) & (dff["Date"]<end_date)]
        else:
            dff = dff.loc[(dff["Date"]>start_date)]
    elif (end_date is not None):
        dff = dff.loc[(dff["Date"]<end_date)]

# Country name input filter
    if len(selected_dropdown) > 0:
        dff = dff.loc[dff["Region"].isin(selected_dropdown)]

# Artist name input filter
    if len(musician_name) > 0:
        dff = dff.loc[dff["Artist"].isin(musician_name)]
    
# Track name input filter
    if len(track_name) > 0:
        dff = dff.loc[dff["Track Name"].isin(track_name)]

# Range slider filter
    if int(selected_range[0]>0):
        dff = dff.loc[(dff["Position"] >= int(selected_range[0])) & (dff["Position"] <= int(selected_range[1]))]

    dff = dff[['danceability', 'energy', 'instrumentalness', 'valence','acousticness', 'liveness', 'speechiness']].mean()



    fig_3 = px.line_polar(r=dff,theta=dff.index,line_close=True,range_r = [0,1.0],title="Average attributes of all songs in your selection",direction="counterclockwise", start_angle=45)

    fig_3.update_traces(fill='toself',fillcolor="#1DB954", opacity=0.6, line=dict(color="#1DB954"))

    fig_3.update_layout(paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_color="#1DB954",
        font_color="white",
        xaxis_showgrid=False, 
        yaxis_showgrid=False)

    fig_3.update_traces(line_color="#1DB954")   

    return fig_3

@app.callback(
    [Output('total-str', 'children'),
    Output('total-artists', 'children'),
    Output('total-songs', 'children')],
    [Input('dropdown1', 'value'),
    Input('slider1', 'value'),
    Input('dropdown2', 'value'),
    Input('dropdown3', 'value'),
    Input('date', 'start_date'),
    Input('date', 'end_date')
    ]
              )

def update_text(selected_dropdown,selected_range,musician_name,track_name,start_date,end_date):

    dff = df_ready

# Date filter
    if (start_date is not None):
        if (end_date is not None):
            dff = dff.loc[(dff["Date"]>start_date) & (dff["Date"]<end_date)]
        else:
            dff = dff.loc[(dff["Date"]>start_date)]
    elif (end_date is not None):
        dff = dff.loc[(dff["Date"]<end_date)]

# Country name input filter
    if len(selected_dropdown) > 0:
        dff = dff.loc[dff["Region"].isin(selected_dropdown)]

# Artist name input filter
    if len(musician_name) > 0:
        dff = dff.loc[dff["Artist"].isin(musician_name)]
    
# Track name input filter
    if len(track_name) > 0:
        dff = dff.loc[dff["Track Name"].isin(track_name)]

# Range slider filter
    dff = dff.loc[(dff["Position"] >= int(selected_range[0])) & (dff["Position"] <= int(selected_range[1]))]
    
    stream = f"Total number of streams: {dff.Streams.sum()}"
    artists = f"Total number of artists: {len(set(dff.Artist))}"
    tracks = f"Total number of tracks: {len(set(dff['Track Name']))}"

    return stream, artists, tracks

if __name__ == '__main__':
    app.run_server(debug=True)


