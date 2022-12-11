# %%
# Standard imports
import numpy as np
import pandas as pd

# For web scraping
import requests
from bs4 import BeautifulSoup

# For performing regex operations
import re

import os
import datetime

from limitless_scrape import *
from limitless_analysis import *

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# %% [markdown]
# 1. Create DataFrame that contains dates and URLs for each tournament in the Late Night's organizer page. 
# 2. Use checkpoint to compare which tournaments have already been scraped. 
# 3. Filter the DataFrame so that it only contains tournaments that have not been scraped. 
# 4. Put all URLs of filtered DataFrame to a list. 
# 5. Pass list to create_urls to create url_dict. 
# 6. Scrape all the URLs in url_dict. 
# 7. Process data so it looks like results
# 8. Update Checkpoint. 


# Use checkpoint or scrape everything?
use_checkpoint = False

# %%
# 1. Create DataFrame that contans dates and URLS for each tournament
df_latenight = scrape_for_dates_and_url()

# 2. Use checkpoint. If not using checkpoint, scrape everything
if use_checkpoint == True:
    logging.info("Using checkpoint. Loading in checkpoint...")
    ckpt_df = pd.read_csv("checkpoint/latest/checkpoint.csv")
    current_results_df = pd.read_csv("results/latest/scrape_results.csv")
    
    # 3. and 4. Instead of filtering the DataFrame, we can use list comprehension to find net new urls. 
    ckpt_url_ls = ckpt_df['url'].unique().tolist()
    all_url_ls = df_latenight['URL'].unique().tolist()
    net_new_url_ls = [url for url in all_url_ls if url not in ckpt_url_ls] 
    
    # 5. Create url dict; Only use first 2 urls as a test
    url_dict = create_urls(net_new_url_ls)

    logging.info('Scraping tournaments...')                   
    # # 6. Scrape urls in dict and add date
    scrape_results_dict = multi_latenight_scrape(url_dict)
    scrape_results_dict = add_date_to_dict(scrape_results_dict, df_latenight)

    # 6a. Save results to csv
    logging.info("Saving scraped results...")
    scrape_results_to_csv(scrape_results_dict)
    
    # 7. Process data: Get WLT counts for each deck in each tournament
    all_tournament_results_dict = multi_tournament_wr_per_tournament(scrape_results_dict)

    logging.info('Calculating win rates...')
    # Calculate winrates
    multi_tournament_wr_calc(all_tournament_results_dict)
    
    # Create plot_df
    plot_df = create_plot_df(all_tournament_results_dict)
    
    # 8. Append plot_df to current results, and update checkpoint
    update_results(current_results_df, plot_df)
    update_checkpoint(all_tournament_results_dict, ckpt_df)
                           
else: 
    logging.info("Checkpoint not in use. Scraping all data...")
    # Scrape everything
    url_list = df_latenight['URL'].unique().tolist()
    url_dict = create_urls(url_list)

    scrape_results_dict = multi_latenight_scrape(url_dict)
    scrape_results_dict = add_date_to_dict(scrape_results_dict, df_latenight)

    # Save results to csv
    logging.info("Saving scraped results...")
    scrape_results_to_csv(scrape_results_dict)
    
    # Process data: Get WLT counts for each deck in each tournament
    all_tournament_results_dict = multi_tournament_wr_per_tournament(scrape_results_dict)

    # Calculate winrates
    logging.info('Calculating win rates...')
    multi_tournament_wr_calc(all_tournament_results_dict)
    
    # Create plot_df
    plot_df = create_plot_df(all_tournament_results_dict)

    # Create blank current results and append net new results (plot_df)
    headers = ["deck", "opposing_deck", "t_url", "date", "wins", "winrate", "games_played"]
    current_results_df = pd.DataFrame(columns=headers)
    update_results(current_results_df, plot_df)

    # Create and save checkpoint 
    ckpt_df = pd.DataFrame(columns=["date", "name", "url"])
    update_checkpoint(all_tournament_results_dict, ckpt_df)