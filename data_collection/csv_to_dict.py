#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import numpy as np
import os
import glob

import datetime

from limitless_scrape import *
from limitless_analysis import *


# In[2]:


# Create path for scraped data
scraped_data = os.path.join(os.getcwd(), "scraped_data")

folder_paths = [x[0] for x in os.walk(scraped_data)][1:]


# In[3]:


def csv_to_dict(t_dir):
    folder_paths = [x[0] for x in os.walk(t_dir)][1:]
    
    # Dict for all csv files
    csv_dict = {}

    for path in folder_paths: 
        csvs = glob.glob(os.path.join(path, '*.csv'))
        csv_dict[path] = csvs
    
    # Read in all scraped data into a new dict; add date
    scraped_dict = {}

    for t in csv_dict:
        # Read in players/standings
        t_name = t.split('_')[-1]
        scraped_dict[t_name] = {}
        scraped_dict[t_name]['players'] = pd.read_csv(os.path.join(t, "players.csv"))

        # Read in rounds 
        scraped_dict[t_name]["pairings"] = {}

        for round_num in range(1,15):
            csv_path = os.path.join(t, f"round_{round_num}.csv")
            # print(csv_path)
            try:
                scraped_dict[t_name]["pairings"][f"round_{round_num}_pairings"] = {} 
                scraped_dict[t_name]["pairings"][f"round_{round_num}_pairings"]["df"] = pd.read_csv(csv_path)
            except:
                continue
                
    # Scrape completed tournaments to get dates
    df_latenight = scrape_for_dates_and_url()
    
    # For every tournament, if t_name in URL, grab the date
    for t in scraped_dict:
        row = df_latenight[df_latenight['URL'].str.contains(t)]
        scraped_dict[t]["date"] = row.iloc[0]["Date"]
    
    return scraped_dict
    


# In[4]:


scraped_data = csv_to_dict(scraped_data)


# In[5]:


new_dict = {}

# Add player's archetype to each player
for t in scraped_data:
    new_dict[t] = {}
    
    # Add players to new_dict
    t_players = scraped_data[t]["players"]
    new_dict[t]["players"] = t_players
    
    
    for round_num in scraped_data[t]["pairings"]:
        try:
            round_dict = scraped_data[t]["pairings"][round_num]

            df_with_archetype = deck_and_records(round_dict, t_players)
            new_dict[t][f"{round_num}"] = df_with_archetype
        
        except:
            continue
    


# In[39]:


deck_counts['Mew Genesect']


# In[74]:


# Only want players and round 9 pairings
p2_conversion_rate_dict = {}

for t in new_dict:
    p2_conversion_rate_dict[t] = {}
    
    players = new_dict[t]["players"]
    deck_counts = players["Deck"].value_counts()
    
    # total number of players
    players_at_tournament = players.shape[0]
    
    # Check for round 10 for phase 2
    try:
        phase_2_swiss = new_dict[t]["round_10_pairings"]
        archetypes = pd.concat([phase_2_swiss["Player 1 Deck"], phase_2_swiss["Player 2 Deck"]])
        phase_2_archetypes = archetypes.value_counts()
        
        # num players in day 2
        num_players_day_2 = archetypes.shape[0]
        
        for deck in deck_counts.keys():
            # Create blank dictionary for deck 
            p2_conversion_rate_dict[t][deck] = {}
            
            p1_count = deck_counts[deck]
            
            if deck in phase_2_archetypes.keys():
                p2_count = phase_2_archetypes[deck]
            else:
                p2_count = 0 
            
            # print(p2_count)
            # calc conversion rate and metashare
            conv_rate = round(p2_count/p1_count, 2)
            overall_metashare = round(p1_count/players_at_tournament, 2)
            day_2_metashare = round(p2_count/num_players_day_2, 2)
            
            # Save to dict
            p2_conversion_rate_dict[t][deck]["conv_rate"] = conv_rate
            p2_conversion_rate_dict[t][deck]["overall_metashare"] = overall_metashare
            p2_conversion_rate_dict[t][deck]["day_2_metashare"] = day_2_metashare
            p2_conversion_rate_dict[t][deck]["p1_count"] = p1_count
            p2_conversion_rate_dict[t][deck]["total_num_players"] = players_at_tournament
            p2_conversion_rate_dict[t][deck]["p2_count"] = p2_count
            p2_conversion_rate_dict[t][deck]["num_players_day_2"] = num_players_day_2
            
            
        
    except:
        continue


# In[75]:


p2_conversion_rate_dict


# In[69]:


phase_2_archetypes["Palkia Inteleon"]


# In[70]:


# p2_conversion_rate_dict


# In[14]:


archetypes = pd.concat([phase_2_swiss["Player 1 Deck"], phase_2_swiss["Player 2 Deck"]])


# In[27]:


test = archetypes.value_counts()


# In[29]:


test["Palkia Inteleon"]


# In[31]:


for key in test.keys():
    print(key)


# In[32]:


archetypes.unique()


# In[59]:


if "Mew Geesect" in archetypes.unique():
    print(1)


# In[ ]:




