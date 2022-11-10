#!/usr/bin/env python
# coding: utf-8

# imports 
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go


def plot_winrate_by_date(plot_df, deck):
    """Plot win rate of active deck against other archetypes over time.

    Arguments:
        plot_df (DataFrame): DataFrame containing the name of active deck, the name of opposing deck, date of the 
                             tournament, the win rate for the active deck against the opposing deck, and the number 
                             of games played between the two decks.
        deck (str): Name of the active deck. 

    """
    filtered_df = filter_plot_df(plot_df, deck)
    fig = px.line(filtered_df, x="date", y="winrate", color="opposing_deck", title=deck)
    fig.show()
    
    
def plot_wr_vs_top_five(plot_df, deck):
    """Plot a decks winrate over time against the top 5 decks by usage. 
    
    Arguments:
        plot_df (df): DataFrame containing winrates for each archetype. 
        deck (str): Name of the deck of interest.

    """

    # Filter df 
    filtered_df = filter_plot_df(plot_df, deck)
    
    
    # Empty lists, dictionaries, and figure
    um = {}
    button_list = []
    
    # Instantiate empty plotly figure, set dimensions
    fig = go.Figure()
    fig.update_layout(width=1080, height=720)
    # colors = px.colors.qualitative.Plotly

    top5 = [
        "Palkia Inteleon",
        "Giratina LZ Box", 
        "Kyurem Palkia",
        "Lost Zone Box", 
        "Mew Genesect"
    ]
    
    # If deck is in top 5, replace that entry with Regis
    for i, d in enumerate(top5):
        if d == deck:
            top5[i] = "Regis"

    # Create a line graph for each deck in the top 5 and create corresponding buttons
    for i, archetype in enumerate(top5):
        temp_df = filtered_df[filtered_df['opposing_deck'] == archetype]

        hovertemplate = "Games Played: %{customdata} <br>Winrate: %{y} </br>"

        # Add line for each archetype in top5
        fig.add_trace(go.Scatter(x=temp_df['date'], 
                                 y=temp_df['winrate'], 
                                 customdata=temp_df['games_played'], 
                                 visible=True, 
                                 name=archetype, 
                                 hovertemplate=hovertemplate)
                     )


        # Create buttons for dropdown menu
        button = dict(method='restyle',
                  label=archetype,
                  visible=True,
                  args=[{'visible':True}, [i]],
                  args2 = [{'visible': False}, [i]],
                 )

        button_list.append(button)
    
    # Adjust updatemenus for dropdown
    um['buttons'] = button_list
    um['direction'] = 'down'
    um['showactive'] = True
    um['pad'] = {"r": 10, "t": 10}
    um['type'] ='dropdown'
    updatemenus = [um]

    # add dropdown menus to the figure
    fig.update_layout(showlegend=True, updatemenus=updatemenus)
    fig.update_layout(yaxis_range=[0,1], title_text=deck)
    fig.add_hline(y=0.5)

    f = fig.full_figure_for_development(warn=False)
    
    fig.show()