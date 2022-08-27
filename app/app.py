from dash import *
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(__name__,meta_tags=[{"name":"viewport","content":"width=device-width","initial-scale":"1"}])
server = app.server

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

df = pd.read_csv('goalie_stats.csv')

#add code to get means for columns
save_percent_df = df.iloc[:,21:-2]
league_averages = save_percent_df.mean()

x_labels = ['Total SV%','Against Leftwing','Against Center','Against Rightwing','Against Defense']

app.layout = html.Div(style={'background-color': colors['background'],'font-family':'Arial'}, children=[
    html.H1(
        children='NHL Goalies 2019/2020',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    
    html.Div(children=[
             html.P("The basic metrics for evaluating goalie performance in the NHL are shots against, saves, save percentage, and wins."),
             html.Br(),
             html.P("I dug deeper into each goalie's performance by calculating their save percentage against each shooting position, and broke it down further by the shooters shooting hand")
    ], 
             style={
        'textAlign': 'left',
        'color': colors['text']
    }),

    html.Div(style = {'display':'flex'},children=[
   
    html.Div(style={'margin-top':'25px','width': '100%','display':'inline-block'},
    children=[
    
    dcc.Dropdown(
        id = 'dropdown_goalie',
        options=[
        {'label': i, 'value': i} for i in df['player_name']
        ] ,
        value='Corey Crawford'
    ),

    dcc.RadioItems(
        style={'margin-top': '20px'},
        id = 'hand_shoots',
        options=[
        {'label': 'Against All Players', 'value': 'all'},
        {'label': 'Against Right Handed Players', 'value': 'righty'},
        {'label': 'Against Left Handed Players', 'value': 'lefty'} 
        ],
        value='all'
    ),
    dcc.Graph(
        id='graph-1',
    )
    ])
    ]) 
])

#call back takes dropdown and radio button selections as inputs, outputs updated graph with player data
@app.callback(
    Output(component_id='graph-1', component_property='figure'),
    Input(component_id='dropdown_goalie', component_property='value'),
    Input(component_id='hand_shoots',component_property='value')
)
    
def update_fig(dropdown_individual,hand_shoots):
    selected_df = df.loc[df['player_name']==dropdown_individual]
    selected_df = selected_df.transpose().iloc[21:-2,]
    col = selected_df.columns.values[0]
    selected_df = selected_df.rename(columns={col:'stats'})
    selected_df['labels']=selected_df.index.tolist()
    selected_df['league_averages'] = league_averages
   
    if hand_shoots == 'all':
        selected_df = selected_df.loc[['SV%','SV%_LeftWing_Total','SV%_Center_Total','SV%_RightWing_Total','SV%_Defense_Total']]
    elif hand_shoots == 'righty':
        selected_df = selected_df.loc[['SV%_Right','SV%_LeftWing_Right','SV%_Center_Right','SV%_RightWing_Right','SV%_Defense_Right']]
    else:
        selected_df = selected_df.loc[['SV%_Left','SV%_LeftWing_Left','SV%_Center_Left','SV%_RightWing_Left','SV%_Defense_Left']]

    fig = go.Figure(data=[
    go.Bar(name=dropdown_individual, x=x_labels, y=selected_df['stats']),
    go.Bar(name='League Average', x=x_labels, y=selected_df['league_averages'])
    ])
    fig.update_layout(
        yaxis_range=[0.5,1.0],
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        barmode = 'group'
        )
    fig.update_traces(width=0.3)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
