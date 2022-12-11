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


# Dict for all csv files
csv_dict = {}

for path in folder_paths: 
    csvs = glob.glob(os.path.join(path, '*.csv'))
    csv_dict[path] = csvs


# In[4]:


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
            scraped_dict[t_name]["pairings"][f"round_{round_num}_pairings"] = pd.read_csv(csv_path)
        except:
            continue


# In[5]:


# Scrape completed tournaments to get dates
# 1. Create DataFrame that contans dates and URLS for each tournament
df_latenight = scrape_for_dates_and_url()


# In[21]:


# For every tournament, if t_name in URL, grab the date
for t in scraped_dict:
    row = df_latenight[df_latenight['URL'].str.contains(t)]
    scraped_dict[t]["date"] = row.iloc[0]["Date"]


# In[27]:


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
    


# In[28]:


test = csv_to_dict(scraped_data)


# In[36]:


new_dict = {}

# Add player's archetype to each player
for t in test:
    new_dict[t] = {}
    
    # Add players to new_dict
    t_players = test[t]["players"]
    new_dict[t]["players"] = t_players
    
    
    for round_num in test[t]["pairings"]:
        try:
            round_dict = test[t]["pairings"][round_num]

            df_with_archetype = deck_and_records(round_dict, t_players)
            new_dict[t][f"{round_num}"] = df_with_archetype
        
        except:
            continue
    


# In[37]:


new_dict


# In[ ]:




