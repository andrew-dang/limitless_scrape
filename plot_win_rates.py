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
    ], className='seven columns'),
    
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
            
        
    ], className='four columns'),

    html.Div([
        dcc.Graph(id='heatmap')
    ], className='four columns')
    
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
    format_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]
    
    # Filter for deck of interest
    active_deck_df = filter_plot_df(format_df, dropdown_deck)
    
    # Filter the data for opposing deck
    opp_deck_df = active_deck_df[active_deck_df["opposing_deck"].isin(dropdown_opp_deck)]

    # Aggregate by day - need weighted win rates here
    gp_per_day = opp_deck_df.groupby(["deck", "opposing_deck", "date"]).sum().reset_index()
    gp_per_day["gp_per_day"] = gp_per_day["games_played"]
    
    join_conditions = ["deck", "opposing_deck", "date"]
    weighted_df = opp_deck_df.merge(gp_per_day[["deck", "opposing_deck", "date", "gp_per_day"]], how="left", on=join_conditions)

    weighted_df['wt'] = weighted_df["games_played"] / weighted_df["gp_per_day"]
    weighted_df['wt_wr'] = round(weighted_df['winrate'] * weighted_df['wt'], 2)

    weighted_df = weighted_df.groupby(["deck", "opposing_deck", "date"]).sum(["games_played", "wt_wr"]).reset_index()
     
    # Create line graph
    fig = px.scatter(weighted_df, 
                     x='date', 
                     y='wt_wr', 
                     color='opposing_deck', 
                     hover_data=["games_played"], 
                     size='games_played', 
                     labels=dict(date="Date", 
                                 opposing_deck="Opposing Deck", 
                                 wt_wr="Win Rate", 
                                 games_played="Games Played")) \
                                 .update_traces(mode='lines+markers')
    
    # Update layout
    fig.update_layout(width=1080, height=720)
    fig.update_layout(showlegend=True, yaxis_range=[-0.05,1.05], title_text=f"{dropdown_deck}'s win rate against opposing decks over time since {dropdown_format}'s release")
    fig.update_layout(title={"x": 0.45, "y": 0.95, "xanchor": "center", "yanchor": "middle"})
    fig.add_hline(y=0.5)
    fig.update_xaxes(ticks="outside", ticklen=10)
    fig.update_yaxes(ticks="outside", dtick=0.1, ticklen=10)
     
     
    return fig 


@app.callback(
    Output('heatmap', 'figure'),
    [
        Input('dropdown_format', 'value'),
        Input('dropdown_deck','value'),
        Input('dropdown_opp_deck', 'value')
     ]
     )  
def build_heatmap(selected_format, selected_active_deck, selected_opp_deck):
    # Filter by selected format 
    set_df = set_calendar_df[set_calendar_df["set_name"]==selected_format]
    start_date = set_df.iloc[0]['start_date']
    end_date = set_df.iloc[0]['end_date']
    
    # Filter dataframe by date
    format_df = plot_df[(plot_df['date'] >= start_date) & (plot_df['date'] <= end_date)]   

    # Create list of decks selected in dropdown 
    selected_opp_deck.append(selected_active_deck)
    unique_decks = []
    for deck in selected_opp_deck:
        if deck not in unique_decks:
            unique_decks.append(deck)
    
    # Filter active deck by decks in unique decks, filter again on opposing deck by unique decks also 
    active_deck_df = format_df[format_df['deck'].isin(unique_decks)] 
    filtered_df = active_deck_df[active_deck_df['opposing_deck'].isin(unique_decks)]

    # blank heatmaps for wins and games played
    heatmap_gp = pd.DataFrame(columns=unique_decks, index=unique_decks)
    heatmap_wr = pd.DataFrame(columns=unique_decks, index=unique_decks)

    # Get total games played and weighted win rates
    filtered_df["total_games"] = filtered_df.apply(lambda x: total_gp(filtered_df, x), axis=1)
    filtered_df["weight"] = filtered_df["games_played"]/filtered_df["total_games"]
    filtered_df["wt_wr"] = filtered_df["winrate"] * filtered_df["weight"]
    
    # Create aggregated df 
    agg_df = filtered_df.groupby(['deck', 'opposing_deck']).agg({"wt_wr": "sum", "games_played": "sum"}).reset_index()

    # Loop through active decks to fill in columns in blank heatmaps
    for active_deck in heatmap_wr:
        filtered_df = agg_df[agg_df['deck']==active_deck]
        
        # Find win rate for every deck in index (opposing deck)
        wr_ls = []
        gp_ls = []
        for deck in heatmap_wr.index:
            if deck in filtered_df['opposing_deck'].unique():
                winrate = filtered_df[filtered_df['opposing_deck']==deck].iloc[0]['wt_wr']
                gp = filtered_df[filtered_df['opposing_deck']==deck].iloc[0]['games_played']
                wr_ls.append(round(winrate,2))
                gp_ls.append(gp)
            else:
                winrate = None
                wr_ls.append(winrate)
                gp_ls.append(None)
            
        # set column to mu 
        heatmap_wr[active_deck] = wr_ls
        heatmap_gp[active_deck] = gp_ls

    # Heatmap hovertext
    hovertext = []
    for xi, xx in enumerate(heatmap_wr.columns):
        hovertext.append(list())
        for yi, yy in enumerate(heatmap_wr.index):
            hovertext[-1].append(f"Active Deck: {yy}<br />Opposing Deck: {xx}<br />Win Rate: {heatmap_wr.values[xi][yi]}<br />Games Played: {heatmap_gp.values[xi][yi]}")

    fig = go.Figure(data=go.Heatmap(
                   z=heatmap_wr.values,
                   x=heatmap_wr.columns.tolist(),
                   y=heatmap_wr.index.tolist(),
                   hoverinfo='text',
                   text=hovertext,
                   texttemplate="%{z}",
                   textfont={"size": 12},
                   hoverongaps = False,
                   xgap=3,
                   ygap=3,
                #    zmin=0, 
                #    zmax=1
                   ))
    
    # Layout
    title_text = f"Average win rates since {selected_format}'s release"
    xaxis_title = "Active Decks" 
    yaxis_title = "Opposing Decks"
    fig.update_layout(width=800, 
                      height=800,
                      title_text=title_text,
                      title={"x": 0.5, "y": 0.9, "xanchor": "center", "yanchor": "bottom"},
                      xaxis_title=xaxis_title,
                      yaxis_title=yaxis_title)

    
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)