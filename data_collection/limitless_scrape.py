#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

request_header = {"User-Agent":  "Late Night Results Compiler (heyitsbluray@gmail.com)"}

# In[ ]:


def create_urls(tournaments):
    """
    Create URLs for the tournament you wish to scrape.
    
    Arguments:
        tournaments (list): list of urls for the late night tournaments.
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
    """
    Scrapes the pairings pages of a Late Night tournament. Returns information including:
    - Player Names
    - Player Records
    - Player IDs
    - Scores of each pairing per round

    
    Arguments: 
        urls (list): list of urls
    """
    
    # Empty dictionary to store results of each round 
    all_round_dict = {}
    
    # Loop through each round 
    for round_i, url in enumerate(urls, start=1):
        # FOR DEBUGGING 
        # logging.info(f"Scraping data for round {round_i}")
        
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
        
    # If there is no round, continue to next url
        # try:    
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

        # Get the data
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

        # except:
            # logging.info("No round...")
        
    
    return all_round_dict
    
    
def scrape_players_and_decks(url):
    """
    Scrape the url that contains the record of each player and the deck they played - usually
    the standings. Relevant information that is grabbed includes Player ID, Player Name, 
    and deck that the player played. 
    
    Arguments:
        url (str): URL that contains the record of each player and the deck they played.
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

    # Find the rows
    for row in player_table.find_all('tr')[1:]:
        data = row.find_all('td')   
        
    # href found in second column 
        for i, td in enumerate(data):
            if i == 1:
                a = td.find('a')
                if a != None:
                    href = a.get('href')
                    player_id = href.split('player/')[-1]
        
        # Deck name is in another html tag
        for it, value in enumerate(data):
            title = value.get('title')
            if title == None:
                continue
            else: 
                deckname = title
                pos = it

        # Get all the other information in the table 
        row_data = [td.text.strip() for td in data]
        row_data.append(player_id)
        row_data[pos] = deckname
        length = len(df)
        df.loc[length] = row_data
  
    return df


def deck_round_performance(deck_record_df, norm=True):
    if norm:
        display(deck_record_df.groupby("Record").value_counts(normalize=True)*100)
    else:
        display(deck_record_df.groupby("Record").value_counts())
        
        
def multi_latenight_scrape(url_dict):
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
    

def format_scraper(set_name):
    """
    Given a Pokemon set name, scrape all the Late Night tournament results for when this set was legal
    
    Arguments:
        set_name (str): Name of the set
    """
    
    set_dict = {
        "Lost Origin": "2022-09-09",
        "Pokemon GO": "2022-07-01"
    }

    release_date = set_dict[set_name]


    # Create DataFrame with dates and URL for each Late Night 
    df_latenight = scrape_for_dates_and_url()

    # Filter for the tournaments that this set was legal for
    df_set = df_latenight[df_latenight["Date"] >= release_date]

    # Get the list of urls
    df_set_urls = df_set['URL'].tolist()

    # Create url_dict
    url_dict = create_urls(df_set_urls)
    
    # Scrape all the tournaments in this format 
    all_tournament_dict = multi_latenight_scrape(url_dict)
    
    return all_tournament_dict


def scrape_for_dates_and_url():
    """
    Scrapes limitlesstcg's organizer page to get a DataFrame that contains 
    all the dates and URLs of Late Night tournaments. 
    """
    
    # Page for scraping tournaments 
    url = 'https://play.limitlesstcg.com/organizer/194'

    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html5lib')

    # Find all tables
    # tables = soup.find_all('table')

    # Completed table is the second one 
    completed = soup.find('table', {'class': 'striped completed-tournaments'})


    # base URl
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

    # filter tournaments for late nights
    df_latenight = df[df[df.columns[1]].str.contains("Late Night #\d{2}")]
    
    return df_latenight


def add_date_to_dict(all_tournament_dict, df_latenight):
    """
    Adds dates to each tournament in all_tournament_dict to use later for plotting. 
    
    Arguments:
        all_tournament_dict (dict): Dictionary that contains the final standings and a DataFrame
                                    for each round for all tournaments scraped. 
        df_latenight (df): DataFrame that contains the dates and urls for all Late Night tournaments. 
    """
    
    # Find the tournaments date in df_latenight
    for key in all_tournament_dict.keys():
        row = df_latenight[df_latenight["URL"].str.contains(key)]
        date = row.iloc[0]["Date"]
        
        # Insert the date into all_tournament_dict
        all_tournament_dict[key]["date"] = date
        
    
    return all_tournament_dict


def update_results(current_results, net_new_results):
    """
    current_results (df): Results previously scraped.
    net_new_results (df): Results just scraped. 
    """
    
    # Add newly scraped data to previously scraped data
    updated_plot_df = pd.concat([net_new_results, current_results], ignore_index=True)
    
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
    """
    
    Arguments:
        wr_dict (dict): Dictionary with the winrates of decks across multiple tournaments.
        ckpt_df (DataFrame): DataFrame that contains URL and dates of tournaments already scraped. 
    """
    
    # Create DataFrame for data just scraped to update the checkpoint
    headers = ["date", "url"]

    net_new_url_df = pd.DataFrame(columns=headers)
    
    # Add data to net_new_url_df
    for url, t_dict in wr_dict.items():
            row = [t_dict["date"], url]
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