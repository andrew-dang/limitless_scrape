#!/bin.sh

# activate the conda env
# CALL conda.bat activate dash_app

# cd to right directory
cd C:/Users/andre/Desktop/limitless_scrape/data_collection

# Scrape data 
python scrape_and_process.py

# push to heroku
git add . 
git commit -m "scrape and deploy"
git push heroku main 

# push to github
git push origin main 