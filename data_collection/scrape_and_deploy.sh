#!/bin.sh

# # Scrape data 
python scrape_and_process.py

# push to heroku
git add . 
git commit -m "scrape and deploy"
git push heroku main 

# push to github
git push origin main 