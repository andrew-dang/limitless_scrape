#!/bin.sh

# # Scrape data 
python scrape_and_process.py

# login to Heroku 
git add . 
git commit -m "scrape and deploy"
git push heroku main 