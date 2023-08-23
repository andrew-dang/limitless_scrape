#!/usr/bin/env python
# coding: utf-8

# imports
import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

import re
import logging
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import os

request_header = {"User-Agent":  "Late Night Results Compiler (andrew.dang94@gmail.com)"}


def create_urls(tournaments):
    """Generate dictionary of URLs for the Standings and Pairings tabs.

    Create URLs for the tournament you wish to scrape.
    
    Arguments:
        tournaments (list): list of urls (str) for the late night tournaments.

    Returns: 
        url_dict (dict): Dictionary with the tournament's details page URL as the key, and 
                         the tournament's Standings and Pairings URLs as values. 

    """
    url_dict = {}
    
    for t in tournaments:
        # Create dictionary for tournament
        t_dict = {} 
        round_urls = []
        standings_url = t + "standings"
        
        # Get urls for rounds 
        for i in range(1,15):
            round_url = t + f"pairings?round={i}"
            round_urls.append(round_url)
        
        t_dict['standings'] = standings_url
        t_dict['rounds'] = round_urls
        
        # Save t_dict inside url_dict
        url_dict[t] = t_dict
    

    return url_dict


def scrape_limitless_latenight(urls):
    """Scrape Pairings tab of a tournament.

    Scrapes the pairings pages of a Late Night tournament. Returns a DataFrame
    containing Player Names, Player Recods, Player IDs, and the result of each pairing.
    
    Arguments: 
        urls (list): list of urls

    Returns: 
        all_round_dict (dict): Dicionary that contains DataFrames with the above information for each 
                               round of pairings in a given tournament. 

    """
    
    # Empty dictionary to store results of each round 
    all_round_dict = {}
    
    # Loop through each round 
    for round_i, url in enumerate(urls, start=1):
        # Create dictionaries to store data 
        round_dict = {}
        
        page = requests.get(url, headers=request_header).text
        soup = BeautifulSoup(page, 'html5lib')

        # Find the table
        table = soup.find('table')

        # If no table, round doesn't exist, go to next round
        if table == None:
            continue

        # get headers
        headers = []
        
        # Find headers
        for item in table.find_all('th'):
            title = item.text
            headers.append(title)

        # Rename headers
        headers[0] = 'Pairing'
        headers[1] = "Player 1"
        headers[2] = 'Player 1 Score'
        headers[3] = 'Player 2 Score'
        headers[4] = 'Player 2'
        headers.append('Player 1 Name')
        headers.append('Player 2 Name')
        headers.append('Player 1 Record')
        headers.append('Player 2 Record')
        headers.append('Winner ID')
        headers.append('Player 1 ID')
        headers.append('Player 2 ID')

        # Create df
        df = pd.DataFrame(columns = headers)

        players_list = ['skip']
        records_list = ['skip']
        ids_list = ['skip']

        # Get the data in each row
        for row_i, row in enumerate(table.find_all('tr')[1:], start=1):

            # Get player id of winner
            winner_id = row.get('data-winner')
            
            data = row.find_all('td')

            # empty list of player names and records 
            pairings = []
            records = []
            player_ids = []

            # Get data for each row
            for ri, td in enumerate(data):
                # Get player names and records for each row, found in the 'a' tag 
                a = td.find_all('a')
                
                # get player names, player ids, and player records
                for tag in a:
                    # player ids
                    href = tag.get('href')
                    player_id = href.split('player/')[-1]
                    player_ids.append(player_id)
                        
                    # records and names
                    score = tag.find('div', {"class": "score"}).string
                    player = tag.find('div', {"class": "name"}).string
                    pairings.append(player)
                    records.append(score)

            # Make sure players and records list has len 2
            if len(player_ids) != 2:
                player_ids.append("*Bye*")
            
            if len(pairings) != 2:
                pairings.append("*Bye*")

            if len(records) != 2:
                records.append("N/A")

            # append append pairings to player_list and records to records_list
            players_list.append(pairings)
            records_list.append(records)
            ids_list.append(player_ids)

            # Get data from row
            row_data = [td.text.strip() for td in data]
            # Add player names and records to row data
            row_data.extend(players_list[row_i])
            row_data.extend(records_list[row_i])
            row_data.append(winner_id)
            row_data.extend(ids_list[row_i])

            # Write row to df
            length = len(df)
            df.loc[length] = row_data
            
        # # Save df to dictionary
        round_dict["df"] = df

        all_round_dict[f"round_{round_i}_dict"] = round_dict
        
    
    return all_round_dict
    
    
def scrape_players_and_decks(url):
    """Scrape Players tab of a tournament.

    Scrape the url that contains the record of each player and the deck they played - usually
    the standings. Relevant information that is grabbed includes Player ID, Player Name, 
    and deck that the player played. 
    
    Arguments:
        url (str): URL that contains the record of each player and the deck they played.

    Returns:
        df (DataFrame): DataFrame that contains Player IDs, Player Names, and the deck that 
                        each player played with for the tournament. 

    """
    # Send request to get html
    page = requests.get(url, headers=request_header).text
    soup = BeautifulSoup(page, 'html5lib')
        
    # Find the table
    player_table = soup.find('table')
    
    # Get header 
    headers = []

    for item in player_table.find_all('th'):
        title = item.text
        headers.append(title)

    # Rename headers
    headers[2] = 'Country'
    headers.append("Player ID")

    # Create df
    df = pd.DataFrame(columns = headers)

    header_row = player_table.find_all('tr')[0]
    
    if "Deck" not in header_row.get_text('th'):
        pass
    else:
        # Find the rows
        for row in player_table.find_all('tr')[1:]:
            data = row.find_all('td')   

        # href found in second column; used to get player ID 
            for i, td in enumerate(data):
                if i == 1:
                    a = td.find('a')
                    if a != None:
                        href = a.get('href')
                        player_id = href.split('player/')[-1]

            # Deck name is in another html tag
            for it, value in enumerate(data):
                span = value.find("span")
                if span != None:
                    if "Dropped" in span.get('data-tooltip'):
                        continue
                    else:
                        deckname = span.get('data-tooltip')
                        pos = it

            # Get all the other information in the table 
            row_data = [td.text.strip() for td in data]
            row_data.append(player_id)
            row_data[pos] = deckname
            length = len(df)
            df.loc[length] = row_data
  
    return df
        
        
def multi_latenight_scrape(url_dict):
    """Scrape Standings and Pairings tabs for multiple tournaments

    Unpack the url_dict to get the URLS of the Standings and Pairings pages of each tournament 
    present in the dictionary. Scrape these URLs and put relevant information into DataFrames. 
    Place these DataFrames into the all_tournament_dict. 

    Args:
        url_dict (dict): Dictionary that contains URLs for the Standings and Pairings pages of the tournament(s).

    Returns:
        all_tournament_dict (dict): Dictionary that has DataFrames for the Standings and Pairings tables for each
                                    tournament present in the url_dict.

    """
    
    all_tournament_dict = {}
    
    # Unpack each tournament in url_dict, scrape, and place in new dict
    for t in url_dict:
        # ln_num = re.findall(r"ln\d{2}", t)[0]
        
        t_dict = {}
        standings_url = url_dict[t]['standings']    # this is a string
        round_urls = url_dict[t]['rounds']      # this is a list
        
        # FOR DEBUGGING
        logging.info(f"Scraping players table for {standings_url}")
        t_dict["players"] = scrape_players_and_decks(standings_url)
        
        t_dict["pairings"] = scrape_limitless_latenight(round_urls)
        
        all_tournament_dict[f"{t}"] = t_dict
        
    return all_tournament_dict
    

def scrape_for_dates_and_url():
    """Scrape to retrieve table with URLs and dates for all completed Late Night tournaments.

    Scrapes the organizer page for Late Night tournaments to get a DataFrame that contains 
    all the dates and URLs of Late Night tournaments. 

    Returns:
        df_latenight (DataFrame): DataFrame that contains the date, name and url of all 
                                  the tournaments a part of the 'Late Night' series.

    """
    
    # Page for scraping tournaments 
    url = 'https://play.limitlesstcg.com/organizer/194'

    page = requests.get(url, headers=request_header).text
    soup = BeautifulSoup(page, 'html5lib')

    # Completed table is the second one 
    completed = soup.find('table', {'class': 'striped completed-tournaments'})

    # base URL; to be appended to URLs found through scraping
    base_url = "play.limitlesstcg.com"

    # Get header
    headers = []

    for item in completed.find_all('th'):
        title = item.text
        headers.append(title)

    # Rename 3rd header
    headers[2] = 'Format'
    headers.append("URL")

    # Create empty df 
    df = pd.DataFrame(columns = headers)

    # Look for td 
    date_list = []
    url_list = []

    # Get date and tournament url; found in first column of table
    for row_i, row in enumerate(completed.find_all('tr')[1:], start=0):
        data = row.find_all('td')
        for it, td in enumerate(data):
            a = td.find_all('a')

            # Look for timestamp and url
            for item in a:
                timestamp = re.findall(r'\d{13}', str(item))
                if len(timestamp) != 0:
                    timestamp = datetime.datetime.fromtimestamp(int(timestamp[0])/1000).strftime('%Y-%m-%d')
                    date_list.append(timestamp)
                if it == 0:
                    t_url = str(re.findall(r'href=".*"', str(item))).split('"')[1].split("standings")[0]
                    t_url = "https://" + base_url + t_url
                    url_list.append(t_url)


        row_data = [td.text.strip() for td in data]
        # add date and url to row_data
        row_data[0] = date_list[row_i]
        row_data.append(url_list[row_i])
        length = len(df)
        df.loc[length] = row_data

    # filter tournaments for late nights; exclude special events 
    df_latenight = df[
    (~df[df.columns[1]].str.contains("Late Late")) &
    (~df[df.columns[1]].str.contains("Invitational")) &
    (~df[df.columns[1]].str.contains("Testing")) &
    (~df[df.columns[1]].str.contains("Bonus Event")) &
    (~df[df.columns[1]].str.contains("Marvel Snap")) & 
    (~df[df.columns[1]].str.contains("Atlas")) &
    (~df[df.columns[1]].str.contains("Upper Hand")) & 
    (~df[df.columns[1]].str.contains("Metafy Regionals")) &
    (~df[df.columns[1]].str.contains("Special")) &
    (~df[df.columns[1]].str.contains("Fan Expo"))
    ]
    
    return df_latenight


def add_date_to_dict(all_tournament_dict, df_latenight):
    """Add dates to all_tournament_dict.

    Adds dates to each tournament in all_tournament_dict to use later for plotting. 
    
    Arguments:
        all_tournament_dict (dict): Dictionary that contains the final standings and a DataFrame
                                    for each round for all tournaments scraped. 
        df_latenight (df): DataFrame that contains the dates and urls for all Late Night tournaments. 

    Returns: 
        all_tournament_dict (dict): The all_tournament_dict with the addition of the "date" key and value
                                    for each tournament. 

    """
    
    # Find the tournaments date in df_latenight
    for key in all_tournament_dict.keys():
        row = df_latenight[df_latenight["URL"].str.contains(key)]
        date = row.iloc[0]["Date"]
        t_name = row.iloc[0]["Name"]
        
        # Insert the date into all_tournament_dict
        all_tournament_dict[key]["date"] = date
        all_tournament_dict[key]["name"] = t_name
        
    
    return all_tournament_dict


def update_results(current_results, net_new_results):
    """Add net new tournament results to existing dataset.

    Takes the processed results from the latest folder and appends the processed data of the net new tournaments.
    Saves the DataFrame back into the latest folder, as well as the dated folder with a date string. 

    Arguments:
        current_results (df): DataFrame with processed data of previously scraped tournaments.
        net_new_results (df): DataFrame with processed data of net net tournaments that were just scraped. 
    """
    
    # Add newly scraped data to previously scraped data
    updated_plot_df = pd.concat([net_new_results, current_results], ignore_index=True)
    logging.info(f"Number of rows before dropping duplicates: {updated_plot_df.shape[0]}")

    # Drop duplicate rows 
    updated_plot_df = updated_plot_df.drop_duplicates(ignore_index=True)
    logging.info(f"Number of rows after dropping duplicates: {updated_plot_df.shape[0]}")
   
    # Define variables and paths for saving checkpoint
    today = datetime.date.today().strftime("%Y-%m-%d")
    path_to_latest = os.path.join(os.getcwd(), "results/latest/scrape_results.csv")
    path_to_dated = os.path.join(os.getcwd(), f"results/dated/scrape_results_{today}.csv")
    
     # Save ckpt to latest and dated
    logging.info("Saving results to 'latest' folder...")
    updated_plot_df.to_csv(path_to_latest, header=True, index=False)
    logging.info("Saving results to 'dated' folder...")
    updated_plot_df.to_csv(path_to_dated, header=True, index=False)   
    
    
def update_checkpoint(wr_dict, ckpt_df):
    """Update checkpoint file with the date and URLs of net new tournaments scraped.

    Takes the checkpoint.csv from the latest folder and updates it to include the 
    net new tournament dates and URLs. 

    Arguments:
        wr_dict (dict): Dictionary with the win rates of decks across multiple tournaments for net new tournaments.
        ckpt_df (DataFrame): DataFrame that contains URL and dates of tournaments already scraped. 
    """
    
    # Create DataFrame for data just scraped to update the checkpoint
    headers = ["date", "name", "url"]

    net_new_url_df = pd.DataFrame(columns=headers)
    
    # Add data to net_new_url_df
    for url, t_dict in wr_dict.items():
            row = [t_dict["date"], t_dict["name"], url]
            length = len(net_new_url_df)
            net_new_url_df.loc[length] = row
    
    # Add net new to checkpoint
    ckpt_df = pd.concat([ckpt_df, net_new_url_df], ignore_index=True)
    
    # Define variables and paths for saving checkpoint
    today = datetime.date.today().strftime("%Y-%m-%d")
    path_to_latest = os.path.join(os.getcwd(), "checkpoint/latest/checkpoint.csv")
    path_to_dated = os.path.join(os.getcwd(), f"checkpoint/dated/checkpoint_{today}.csv")
    
    # Save ckpt to latest and dated
    logging.info("Saving checkpoint to 'latest' folder...")
    ckpt_df.to_csv(path_to_latest, header=True, index=False)
    logging.info("Saving checkpoint to 'dated' folder...")
    ckpt_df.to_csv(path_to_dated, header=True, index=False)


def scrape_results_to_csv(scrape_results_dict):
    """Saves scraped data to CSVs so scraping isn't required everytime a change is made to analysis. 

    Args:
        scrape_results_dict (dict): Dictionary that contains all the scraped tables. 
    """
    for key, value in scrape_results_dict.items():
        strings = key.split('/')
        folder_name = '_'.join(strings[-3:-1])
        folder_path = f"scraped_data/{folder_name}"
        os.makedirs(folder_path, exist_ok=True)
        for table_name, table_value in value.items():
            if table_name == "players":
                filename = "players.csv"
                file_path = f"{folder_path}/{filename}"
                df = value[table_name]
                df.to_csv(file_path, index=False, header=True)
            if table_name == "pairings":
                pairings_dict = value[table_name]
                for round_dict, round_dict_value in pairings_dict.items():
                    round_filename = f"{round_dict.split('_dict')[0]}.csv"
                    round_file_path = f"{folder_path}/{round_filename}"
                    round_df = round_dict_value['df']
                    round_df.to_csv(round_file_path, index=False, header=True)