#!/usr/bin/env python
# coding: utf-8

# imports 
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go


def deck_and_records(round_dict, players_df):
    """Join the players_df and the Pairings DataFrames.

    Join the players_df and the Pairings DataFrames so that each pairing now has the 
    players' names, IDs, records, deck arcetypes, and who won the pairing, and what 
    archetype the winner was playing. 

    Arguments: 
        round_dict (dict): Dictionary containing a DataFrame for the round with data for 
                           the Player Names, IDs, and their records. 
        players_df (DataFrame): DataFrame with each player's name, ID, and choice of deck.

    Returns: 
        round_df (DataFrame): DataFrame which now has both player's names, IDs, choice of deck, 
                              their records, which player won in each pairing, and what deck the 
                              winning player was using.

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
    
    # Create new column that selects the winning deck
    conditions = [
        (round_df['Winner ID'] == round_df['Player 1 ID']),
        (round_df['Winner ID'] == round_df['Player 2 ID']),
        (round_df['Winner ID'] == '0'),
        (round_df['Winner ID'] == '-1')
    ]
    
    winner = (round_df['Player 1 Deck'], round_df["Player 2 Deck"], "Draw", "Loss")

    round_df["Winning Deck"] = np.select(conditions, winner)
    

    return round_df

# No longer in use?
# # Define function for multi_tournament_round_analysis
# def multi_tournament_round_analysis(all_tournament_dict, round_num):
#     """ 
#     Across multiple tournaments, find out the deck you're most likely going to encounter based on 
#     your record.
    
#     Arguments:
#         all_tournament_dict (dict): Dictionary with all the dataframes for players and pairings
#         round_num (int): Round we want to analyze
#     """
#     proc_dict = {}
    
#     # deck_and_records requires round_dict, and players_df
#     for t in all_tournament_dict:
#         t_dict = all_tournament_dict[t]
#         players_df = t_dict["players"]    # This is a df
#         pairings_dict = t_dict["pairings"]
#         round_dict = pairings_dict[f"round_{round_num}_dict"]
        
#         # Process data for this round_num for each tournament
#         round_df = deck_and_records(round_dict, players_df)
        
#         # Save processed data to proc_dict
#         proc_dict[f"{t}"] = round_df
        
#     # Concatenate all df in proc_dict
#     all_proc_df = pd.DataFrame()
    
#     for d in proc_dict:
#         temp_df = proc_dict[d]
#         all_proc_df = pd.concat([all_proc_df, temp_df], ignore_index=True)
        
#     return all_proc_df


def archetype_wr_per_round(round_dict, standings_df, all_archetype_dict):
    """Count wins, losses and ties for every matchup in a round. 

    Counts wins, losses, and ties of each archetype against every other archetype present
    in a single round of a tournament. 
    
    Arguments:
        round_dict (dict): Dictionary that contains information for a round. Currently is 
                        a DataFrame only inside the dictionary. 
        standings_df (df): DataFrame with the standings for the tournament that the round is in. 
        all_archetype_dict (dict): Dictionary that will store the win rates for all matchups.
        
    Returns: 
        all_archetype_dict: Dictionary that stores win rates for each archetype. 

    """
    
    # Add deck names to each player in the pairings
    round_df = deck_and_records(round_dict, standings_df)
    
    # find unique archetypes 
    all_archetypes = standings_df['Deck'].unique().tolist()
    
    # For each archetype, find the winrates against each other archetype
    for archetype in all_archetypes:

        # Dictionary to store all the matchups for current archetype
        if archetype in all_archetype_dict:
            mu_dict = all_archetype_dict[archetype]
        else:
            mu_dict = {}

        # Try including mirror matches:
        temp_df1 = round_df[(round_df["Player 1"] == archetype)]
        temp_df2 = round_df[(round_df["Player 2"] == archetype)]
        
        # Update winrates when Player 1 played the given archetype
        for i in range(len(temp_df1)):
            row = temp_df1.iloc[i]
            opposing_deck = row["Player 2"]

            # add opposing deck to mu dict if its not already there; start WLT count at zero
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
    """Count wins, losses and ties for every matchup for a tournament.

    Counts wins, losses, and ties of each archetype against every other archetype in each
    round in the tournament.

    Arguments: 
        t_dict: Dictionary that contains the Players DataFrame and for each round in the 
                tournament, the Pairings DataFrame.
    
    Returns: 
        t_wlt_dict (dict): Nested dictionary where the keys are each archetype present at the
                           tournament, and the values are dictionaries where these keys are 
                           the archetypes that this archetype played against in the tournament, 
                           and the values are the total wins, losses and ties in this matchup. 

                           i.e.
                           {
                            "Arceus Goodra": {
                                "Palkia Inteleon": {
                                    "wins": 4, "ties": 2, "losses": 3 
                                },
                                "Regis": {
                                    "wins": 7, "ties": 2, "losses": 1 
                                }}
                            }  

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
    """Count wins, losses and ties for every matchup for multiple tournaments. 

    Unpack the all_tournament_dict and count wins, losses and ties for each archetype for each tournament in
    the all_tournament_dictionary, and store the results in a dictionary.

    Arguments:
        all_tournament_dict (dict): Dictionary that contains Standings and Pairings for multiple tournaments. 

    Returns:
        all_tournament_results_dict (dict): Dictionary that counts the wins, losses, and ties for each archetype in 
                                            every tournament in all_tournament_dict. Does not sum up counts across 
                                            tournaments, only within each individual tournament. 

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
    """Calculate win rates for every matchup in a tournament. 

    Using the win, loss and tie counts, calculate the win rate for every matchup. 

    Arguments:
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
    """ Use the WLT counts for every deck and calculate win rates for multiple tournaments.
    
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
    """Loop through all_tournament_results_dict to populate a DataFrame used for plotting later.

    Each row contains the active deck, the opposing deck, date of the tournament, the win rate for the 
    active deck against the opposing deck, and the number of games played between the two decks. 

    Arguments: 
        all_tournaments_results_dict (dict): Dictionary with the counts the wins, losses, and ties for each archetype in 
                                             every tournament. Does not sum up counts across tournaments, only within 
                                             each individual tournament. 

    Returns:
        plot_df (DataFrame): DataFrame containing the name of active deck, the name of opposing deck, date of the 
                             tournament, the win rate for the active deck against the opposing deck, and the number 
                             of games played between the two decks. 

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
    """Filters plot_df using the selected active deck archetype. 
    
    Arguments:
        plot_df (DataFrame): DataFrame containing the name of active deck, the name of opposing deck, date of the 
                             tournament, the win rate for the active deck against the opposing deck, and the number 
                             of games played between the two decks.
        deck (str): Name of the active deck.

    Returns:
        filtered_df (DataFrame): Filtered plot_df to only contain data where the active deck is equaled to the deck 
                                 argument. Also aggregates data by date, as there are typically two tournaments per 
                                 Tuesday.

    """
    
    filtered_df = plot_df[plot_df["deck"] == deck]
    filtered_df = filtered_df.groupby(["deck", "opposing_deck", "date"]).agg({"winrate":"mean", "games_played": "sum"}).reset_index()
    

    return filtered_df 