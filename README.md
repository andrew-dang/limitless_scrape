Hi there! 

This is the source code for my web app where I scrape Pokemon Trading Card Game (PTCG) tournament results from play.limitlesstcg.com, and plot matchup win rates over time. 
[Please check out the app here](https://limitlesstcg-analysis.herokuapp.com/).

The code for the Dash app can be found in plot_win_rates.py. Helper functions in limitless_scrape.py and limitless_analysis.py are imported into the script data_collection/scrape_and_process.py which scrapes and processes the data.

If you have any questions, or encounter a bug, please contact me at andrew.dang94@gmail.com.

# Inspiration for the project - I want to be the very best, like no one ever was
I wanted to build an ETL pipeline that scrapes PTCG tournament results, processes the data to calculate win rates, and then plot the win rates over time. 
This project perfectly blends two things that I love - the Pokemon Trading Card Game, and data. By monitoring different matchup win rates over time, I can 
uncover which archetypes are performing well, and which archetypes are trending upward and downward. This knowledge can help me select an archetype to play in 
future events to help maximize my chances of winning. 

# Using the App
## Dropdowns 
### 1. Select a format/expansion 
The first dropdown menu selects a PTCG expansion set. This filters the data to only include deck archetypes that were played in tournaments when this expansion was first released, up until 
the day before the expansion that follows it is/was released. 

### 2. Select an 'Active Deck'
The second dropdown menu selects an 'Active Deck'. The selected deck will update the plot so that it shows it's win rate against the opposing decks selected in the third dropdown menu. 
This also filters the data so that the options in the third dropdown menu only show opposing decks that the Active Deck has played against in the selected expansion. 

### 3. Select opposing decks
The third dropdown menu allows for multiple selections. Deck archetypes selected here will update the plot to show the Active Deck's win rates against the decks selected in this dropdown menu. 
