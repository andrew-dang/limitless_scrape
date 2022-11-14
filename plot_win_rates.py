#!/usr/bin/env python
# coding: utf-8

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


# Read in data
plot_df = pd.read_csv('data_collection/results/latest/scrape_results.csv')
set_calendar_df = pd.read_csv('set_release_calendar.csv')

# Make sure set_names don't have white space
set_calendar_df["set_name"] = set_calendar_df["set_name"].str.strip()


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
            persistence=True, 
            persistence_type='memory'),
        
        dcc.Dropdown(
            id='dropdown_deck', 
            options=[{'label': x, 'value': x} for x in plot_df.sort_values('deck')['deck'].unique()], 
 #           value='Mew Genesect',
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
        
# # Set persistence for dropdown_format
# @app.callback(
#     Output('dropdown_format', 'persistence')
#     Input('dropdown_format', 'value')
# )

# Filter what active decks are available in the dropdown based on format that is selected
@app.callback(
    Output('dropdown_deck', 'options'),
    Input('dropdown_format', 'value')
)
def available_active_decks(selected_format):
    # Filter by date
    set_df = set_calendar_df[set_calendar_df["set_name"]==selected_format]
    start_date = set_df.iloc[0]['start_date']
    end_date = set_df.iloc[0]['end_date']
    
    filtered_by_date_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]
    return [{'label': x, 'value': x} for x in filtered_by_date_df.sort_values('deck')['deck'].unique()]

# Set active deck to most popular deck
@app.callback(
    Output('dropdown_deck', 'value'),
    Input('dropdown_format', 'value')
)
def set_active_deck(selected_format):
    # Filter by date
    set_df = set_calendar_df[set_calendar_df["set_name"]==selected_format]
    start_date = set_df.iloc[0]['start_date']
    end_date = set_df.iloc[0]['end_date']
    
    filtered_by_date_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]

    # group by games played 
    gp_df = filtered_by_date_df.groupby('deck').sum()['games_played'].reset_index()

    # Return top played deck 
    return [{'label': x, 'value': x} for x in gp_df.sort_values('games_played', ascending=False)['deck'].unique()][0]['value']


# Filter what opposing decks are available in the dropdown based on the format and active deck selected
@app.callback(
    Output('dropdown_opp_deck', 'options'),
    [
        Input('dropdown_format', 'value'),
        Input('dropdown_deck', 'value')
    ]
)
def available_opp_decks(selected_format, selected_active_deck):
    # Filter by date
    set_df = set_calendar_df[set_calendar_df["set_name"]==selected_format]
    start_date = set_df.iloc[0]['start_date']
    end_date = set_df.iloc[0]['end_date']
    
    filtered_by_date_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]
    
    # Filter for deck of interest
    filtered_df = filter_plot_df(filtered_by_date_df, selected_active_deck)
    
    # Return list of opposing decks after filters are applied 
    return [{'label': x, 'value': x} for x in filtered_df.sort_values('opposing_deck')['opposing_deck'].unique()]

# Set opposing decks to top 5 most played in the selected format
@app.callback(
    Output('dropdown_opp_deck', 'value'),
    Input('dropdown_format', 'value'),
)
def available_opp_decks(selected_format):
    # Filter by date
    set_df = set_calendar_df[set_calendar_df["set_name"]==selected_format]
    start_date = set_df.iloc[0]['start_date']
    end_date = set_df.iloc[0]['end_date']
    
    filtered_by_date_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]

    # group by games played 
    gp_df = filtered_by_date_df.groupby('deck').sum('games_played').reset_index()
    
    # Return 5 most played deck  
    return  [x['value'] for x in [{'label': x, 'value': x} for x in gp_df.sort_values('games_played', ascending=False)['deck'].unique()]][0:5]


# Plot our graph based on our selections in the dropdown 
@app.callback(
    Output('our_graph', 'figure'),
    [
        Input('dropdown_format', 'value'),
        Input('dropdown_deck','value'),
        Input('dropdown_opp_deck', 'value')
     ]
     )
     
def build_graph(dropdown_format, dropdown_deck, dropdown_opp_deck):
    """Plot win rates for selected active deck and selected opposing decks in the selected format.

    Arguments:
        dropdown_format (str): Name of a Pokemon TCG expansion. Filters data for plotting 
                               to only include data from the start of the expansion's release date, 
                               til the day before the next expansion's release date.  
        dropdown_deck (str): Name of a Pokemon TCG archetype. Filters the data for plotting. Show 
                             this decks win rate against other archetypes. 
        dropdown_opp_deck (list): Name(s) of Pokemon TCG archetype(s). Filters the data to show the 
                                  win rates of the deck selected in dropdown_deck against the decks 
                                  selected in dropdown_opp_deck.

    Returns:
        fig (plotly.express line graph): A line graph showing the data filtered by the three dropdown 
                                         menus.  
    """
     
    # Get a set's start and end date
    set_df = set_calendar_df[set_calendar_df["set_name"]==dropdown_format]
    start_date = set_df.iloc[0]['start_date']
    end_date = set_df.iloc[0]['end_date']
    
    # Filter dataframe by date
    filtered_by_date_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]
    
    # Filter for deck of interest
    filtered_df = filter_plot_df(filtered_by_date_df, dropdown_deck)
    
    # Filter the data for opposing deck
    temp_df = filtered_df[filtered_df["opposing_deck"].isin(dropdown_opp_deck)]
     
    # Create line graph
    fig = px.scatter(temp_df, x='date', y='winrate', color='opposing_deck', hover_data=["games_played"], size=temp_df['games_played'], labels=dict(date="Date", 
                                                                                                                  opposing_deck="Opposing Deck", 
                                                                                                                  winrate="Win Rate",
                                                                                                                  games_played="Games Played")) \
                                                                                                                  .update_traces(mode='lines+markers')
    
    # Update layout
    fig.update_layout(width=1080, height=720)
    fig.update_layout(showlegend=True, yaxis_range=[-0.05,1.05], title_text=f"{dropdown_deck}'s win rate against opposing decks")
    fig.update_layout(title={"x": 0.45, "y": 0.95, "xanchor": "center", "yanchor": "middle"})
    fig.add_hline(y=0.5)
    fig.update_xaxes(ticks="outside", ticklen=10)
    fig.update_yaxes(ticks="outside", dtick=0.1, ticklen=10)
     
     
    return fig 


if __name__ == '__main__':
    app.run_server(debug=False)