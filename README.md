Hi there! 

This is the source code for my web app where I scrape Pokemon Trading Card Game (PTCG) tournament results from play.limitlesstcg.com, and plot matchup win rates over time. 
Please check out the app [here](https://limitlesstcg-analysis.herokuapp.com/).

If you have any questions, or encounter a bug, please contact me at andrew.dang94@gmail.com.

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
