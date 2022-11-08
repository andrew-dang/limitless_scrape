#!/usr/bin/env python
# coding: utf-8

# imports 
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go


def deck_and_records(round_dict, players_df):
    """
    For a given round, create new DataFrame that has the name of the deck 
    archetype and that player's record at the end of the round. This will help 
    determine what deck you can expect to face in the following round given your record. 
    """
    # Unpack the given round's DataFrame from dictionary
    round_df = round_dict["df"]

    
    # Join round_df and players_df to get deck names 
    round_df = round_df.merge(players_df[["Deck", "Name"]], left_on="Player 1 Name", right_on="Name").drop("Name", axis=1)
    round_df = round_df.rename({"Deck": "Player 1 Deck"}, axis=1)
    round_df = round_df.merge(players_df[["Deck", "Name"]], left_on="Player 2 Name", right_on="Name").drop("Name", axis=1)
    round_df = round_df.rename({"Deck": "Player 2 Deck"}, axis=1)
    
    # Switch Player with Deck name instead so Winner becomes the deck instead
    round_df["Player 1"] = round_df["Player 1 Deck"]
    round_df["Player 2"] = round_df["Player 2 Deck"]
    
    conditions = [
        (round_df['Winner ID'] == round_df['Player 1 ID']),
        (round_df['Winner ID'] == round_df['Player 2 ID']),
        (round_df['Winner ID'] == '0'),
        (round_df['Winner ID'] == '-1')
    ]
    
    winner = (round_df['Player 1 Deck'], round_df["Player 2 Deck"], "Draw", "Loss")

    round_df["Winning Deck"] = np.select(conditions, winner)
    
    return round_df


# Define function for multi_tournament_round_analysis
def multi_tournament_round_analysis(all_tournament_dict, round_num):
    """ 
    Across multiple tournaments, find out the deck you're most likely going to encounter based on 
    your record.
    
    Arguments:
        all_tournament_dict (dict): Dictionary with all the dataframes for players and pairings
        round_num (int): Round we want to analyze
    """
    proc_dict = {}
    
    # deck_and_records requires round_dict, and players_df
    for t in all_tournament_dict:
        # Get the late night number; used for dictionary keys
        # ln_num = re.findall(r"ln\d{2}", t)[0]
        
        t_dict = all_tournament_dict[t]
        players_df = t_dict["players"]    # This is a df
        pairings_dict = t_dict["pairings"]
        round_dict = pairings_dict[f"round_{round_num}_dict"]
        
        # Process data for this round_num for each tournament
        round_df = deck_and_records(round_dict, players_df)
        
        # Save processed data to proc_dict
        proc_dict[f"{t}"] = round_df
        
    # Concatenate all df in proc_dict
    all_proc_df = pd.DataFrame()
    
    for d in proc_dict:
        temp_df = proc_dict[d]
        all_proc_df = pd.concat([all_proc_df, temp_df], ignore_index=True)
        
    return all_proc_df


def archetype_wr_per_round(round_dict, standings_df, all_archetype_dict):
    """
    Counts wins, losses, and ties of each archetype against every other archetype present
    in a round. 
    
    round_dict (dict): Dictionary that contains information for a round. Currently is 
                       a DataFrame only inside the dictionary. 
    standings_df (df): DataFrame with the standings for the tournament that the round is in. 
    all_archetype_dict (dict): Dictionary that will store the winrates
    
    """
    
    # Add deck names to each player in the pairings
    round_df = deck_and_records(round_dict, standings_df)
    
    # find unique archetypes 
    all_archetypes = standings_df['Deck'].unique().tolist()
    
    
    # For each archetype, find the winrates against each other archetype
    for archetype in all_archetypes:

        # Dictionary to store all the matchups
        if archetype in all_archetype_dict:
            mu_dict = all_archetype_dict[archetype]
        else:
            mu_dict = {}

        # # Find rows when either player played the archetype
        # temp_df1 = round_df[(round_df["Player 1"] == archetype) & (round_df["Player 1"] != round_df["Player 2"])]
        # temp_df2 = round_df[(round_df["Player 2"] == archetype) & (round_df["Player 1"] != round_df["Player 2"])]
        
        # Try including mirror matches:
        temp_df1 = round_df[(round_df["Player 1"] == archetype)]
        temp_df2 = round_df[(round_df["Player 2"] == archetype)]
        
        # Update winrates when Player 1 played the given archetype
        for i in range(len(temp_df1)):
            row = temp_df1.iloc[i]
            opposing_deck = row["Player 2"]

            # add opposing deck to mu dict
            if opposing_deck not in mu_dict:
                mu_dict[opposing_deck] = {"wins": 0, "losses": 0, "ties": 0}

            # Check result and update mu_dict
            if row["Winning Deck"] == row["Player 1 Deck"]:
                mu_dict[opposing_deck]["wins"] += 1
            if (row["Winning Deck"] == row['Player 2 Deck']) or (row["Winning Deck"] == "Loss"):
                mu_dict[opposing_deck]["losses"] += 1
            if row["Winning Deck"] == "Draw":
                mu_dict[opposing_deck]["ties"] += 1
        
        # Update winrates when Player 2 played the given archetype
        for i in range(len(temp_df2)):
            row = temp_df2.iloc[i]
            opposing_deck = row["Player 1"]

            # add opposing deck to mu dict
            if opposing_deck not in mu_dict:
                mu_dict[opposing_deck] = {"wins": 0, "losses": 0, "ties": 0}

            # Check result and update mu_dict
            if row["Winning Deck"] == row["Player 2 Deck"]:
                mu_dict[opposing_deck]["wins"] += 1
            if (row["Winning Deck"] == row["Player 1 Deck"]) or (row["Winning Deck"] == "Loss"):
                mu_dict[opposing_deck]["losses"] += 1
            if row["Winning Deck"] == "Draw":
                mu_dict[opposing_deck]["ties"] += 1

        # Update all_archetype_dict
        all_archetype_dict[archetype] = mu_dict
    
    return all_archetype_dict


def archetype_wr_per_tournament(t_dict):
    """
    Counts wins, losses, and ties of each archetype against every other archetype in each
    round in the tournament.
    """
    
    # Create empty dicionaries to store data
    t_wlt_dict = {}
    all_archetype_dict = {}

    standings_df = t_dict["players"]
    
    for round_num in t_dict['pairings']:
        round_dict = t_dict["pairings"][round_num]
        all_archetype_dict = archetype_wr_per_round(round_dict, standings_df, all_archetype_dict)
    
    # Save all_archetype_dict into t_wlt_dict
    t_wlt_dict["date"] = t_dict["date"]
    t_wlt_dict["t_wlt_dict"] = all_archetype_dict
    
        
    return t_wlt_dict


def multi_tournament_wr_per_tournament(all_tournament_dict):
    """
    Unpack the all_tournament_dict and count WLT for each archetype for each tournament in
    the dictionary, and store the results in a dictionary.
    """
    
    # Empty dictionary to store results 
    all_tournament_results_dict = {}
    
    for t in all_tournament_dict:
        t_dict = all_tournament_dict[t]
        
        all_archetype_dict = archetype_wr_per_tournament(t_dict)
        # Put results in all results dictionary 
        all_tournament_results_dict[f"{t}"] = all_archetype_dict
    
    return all_tournament_results_dict
        
    
def calc_wr(archetype_dict):
    """
    archetype_dict (dict): Dictionary that contains a decks WLT against every archetype
                           it has played against in the given tournament. 
    """
    
    # opposing deck is itself a dictionary 
    for key in archetype_dict.keys():
        temp_dict = archetype_dict[key]
        games_played = sum(temp_dict.values())
        wr = round(temp_dict['wins']/games_played, 2)
        
        # Add winrate and gamesplayed to dictionary
        archetype_dict[key]['winrate'] = wr
        archetype_dict[key]['games_played'] = games_played
        
        
def multi_tournament_wr_calc(all_results_dict):
    """ Use the WLT counts for every deck and calculate winrates.
    
    For each tournament scraped, look at each deck played and look at its record against every archetype it played against 
    in a given tournament. Use the WLT counts to calculate winrates. 
    
    Arguments: 
        all_results_dict (dict): Dictionary that contains a dictionary per tournament. Each tournament dictionary contains 
                                 the WLT counts for every deck against every archetype it has played against in a tournament.
                                                     
    """
    
    for t_dict in all_results_dict.values():
        for archetype_dict in t_dict['t_wlt_dict'].values():
            calc_wr(archetype_dict)
            
def create_plot_df(all_tournament_results_dict):
    """
    Loop through all_tournament_results_dict to populate a DataFrame used for plotting later.
    """
    
    headers = ["deck", "opposing_deck", "date", "winrate", "games_played"]
    plot_df = pd.DataFrame(columns = headers)

    # first loop gets t_dict as value
    for t_url, t_dict in all_tournament_results_dict.items():
        date = t_dict['date']
        # Second loop will give us deck of interest name, and the archetype dict
        for deck_of_interest, archetype_dict in t_dict['t_wlt_dict'].items():
            # Third loop gives opposing deck name and WLT counts
            for opposing_deck, wlt_counts in archetype_dict.items():
                row = [deck_of_interest, opposing_deck, date, wlt_counts['winrate'], wlt_counts['games_played']]

                # Put data in df 
                length = len(plot_df)
                plot_df.loc[length] = row
                
    return plot_df


def filter_plot_df(plot_df, deck):
    """
    deck (str): Name of deck of interest
    """
    filtered_df = plot_df[plot_df["deck"] == deck]
    filtered_df = filtered_df.groupby(["deck", "opposing_deck", "date"]).agg({"winrate":"mean", "games_played": "sum"}).reset_index()
    
    return filtered_df 


def plot_winrate_by_date(plot_df, deck):
    
    filtered_df = filter_plot_df(plot_df, deck)
    fig = px.line(filtered_df, x="date", y="winrate", color="opposing_deck", title=deck)
    fig.show()
    
    
def plot_wr_vs_top_five(plot_df, deck):
    """
    Plot a decks winrate over time against the top 5 decks by usage. 
    
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