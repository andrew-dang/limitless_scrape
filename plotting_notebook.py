#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Standard imports
import numpy as np
import pandas as pd

from limitless_scrape import *
from limitless_analysis import *

import plotly.express as px
import plotly.graph_objects as go
import plotly 
import dash 
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)
server = app.server


# In[9]:


# Read in data
plot_df = pd.read_csv('data_collection/results/latest/scrape_results.csv')
set_calendar_df = pd.read_csv('set_release_calendar.csv')

# Make sure set_names don't have white space
set_calendar_df["set_name"] = set_calendar_df["set_name"].str.strip()


# In[10]:


app.layout = html.Div([
    
    html.Div([
        dcc.Graph(id='our_graph')
    ], className='nine columns'),
    
    html.Div([
        
        html.Br(), 
        html.Label(["Choose archetypes to display on the graph:"], style={'font-weight': 'bold', "text-align": "center"}),
        dcc.Dropdown(
            id='dropdown_format', 
            options=[{'label': x, 'value': x} for x in set_calendar_df['set_name'].unique()], 
            value="Lost Origin",
            multi=False, 
            disabled=False,
            clearable=True, 
            searchable=True,
            placeholder='Select a set',
            persistence='string', 
            persistence_type='memory'),
        
        dcc.Dropdown(
            id='dropdown_deck', 
            options=[{'label': x, 'value': x} for x in plot_df.sort_values('deck')['deck'].unique()], 
            value='Mew Genesect',
            multi=False, 
            disabled=False,
            clearable=True, 
            searchable=True,
            placeholder='Select archetype',
            persistence='string', 
            persistence_type='memory'),
        
        dcc.Dropdown(
            id='dropdown_opp_deck', 
            options=[{'label': x, 'value': x} for x in plot_df.sort_values('opposing_deck')['opposing_deck'].unique()], 
            value = ["Palkia Inteleon", "Mew Genesect", "Kyurem Palkia", "Giratina LZ Box", "Lost Zone Box"],
            multi=True, 
            disabled=False,
            clearable=True, 
            searchable=True,
            placeholder='Show winrates against...',
            persistence='string', 
            persistence_type='memory'),
            
        
    ], className='three columns'),
    
])        
        


# In[11]:


@app.callback(
    Output('our_graph', 'figure'),
    [
        Input('dropdown_format', 'value'),
        Input('dropdown_deck','value'),
        Input('dropdown_opp_deck', 'value')
     ]
     )
     
def build_graph(dropdown_format, dropdown_deck, dropdown_opp_deck):
    """
    dropdown (list): Values selected in dropdown menu. 
    """
    
    
    # Filter by date
    set_df = set_calendar_df[set_calendar_df["set_name"]==dropdown_format]
    start_date = set_df.iloc[0]['start_date']
    end_date = set_df.iloc[0]['end_date']
    
    filtered_by_date_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]
    
    # Filter for deck of interest
    filtered_df = filter_plot_df(filtered_by_date_df, dropdown_deck)
    
    # Filter the data for opposing deck
    temp_df = filtered_df[filtered_df["opposing_deck"].isin(dropdown_opp_deck)]
     
    # Create line graph
    fig = px.line(temp_df, x='date', y='winrate', color='opposing_deck', hover_data=["games_played"], labels=dict(date="Date", 
                                                                                                                  opposing_deck="Opposing Deck", 
                                                                                                                  winrate="Win Rate",
                                                                                                                  games_played="Games Played"), markers=True)
    
    # Update layout
    fig.update_layout(width=1080, height=720)
    fig.update_layout(showlegend=True, yaxis_range=[0,1], title_text=f"{dropdown_deck}'s win rate against opposing decks")
    fig.update_layout(title={"x": 0.45, "y": 0.95, "xanchor": "center", "yanchor": "middle"})
    fig.add_hline(y=0.5)
    fig.update_xaxes(ticks="outside", ticklen=10)
    fig.update_yaxes(ticks="outside", dtick=0.1, ticklen=10)
     
     
    return fig 


# In[ ]:


if __name__ == '__main__':
    app.run_server(debug=False)


# In[ ]:




