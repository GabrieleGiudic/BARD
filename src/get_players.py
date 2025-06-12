import requests
from bs4 import BeautifulSoup
import pandas as pd

nba_team_abbreviations = [
    "ATL",  # Atlanta Hawks
    "BOS",  # Boston Celtics
    "BRK",  # Brooklyn Nets
    "CHO",  # Charlotte Hornets
    "CHI",  # Chicago Bulls
    "CLE",  # Cleveland Cavaliers
    "DAL",  # Dallas Mavericks
    "DEN",  # Denver Nuggets
    "DET",  # Detroit Pistons
    "GSW",  # Golden State Warriors
    "HOU",  # Houston Rockets
    "IND",  # Indiana Pacers
    "LAC",  # Los Angeles Clippers
    "LAL",  # Los Angeles Lakers
    "MEM",  # Memphis Grizzlies
    "MIA",  # Miami Heat
    "MIL",  # Milwaukee Bucks
    "MIN",  # Minnesota Timberwolves
    "NOP",  # New Orleans Pelicans
    "NYK",  # New York Knicks
    "OKC",  # Oklahoma City Thunder
    "ORL",  # Orlando Magic
    "PHI",  # Philadelphia 76ers
    "PHO",  # Phoenix Suns
    "POR",  # Portland Trail Blazers
    "SAC",  # Sacramento Kings
    "SAS",  # San Antonio Spurs
    "TOR",  #Toronto Raptors
    "UTA",  #Utah Jazz
    "WAS",  # Washington Wizards
    ]

players_data = []
import time

for t  in nba_team_abbreviations:
    url = "https://www.basketball-reference.com/teams/"+ t +"/2025.html#all_roster"
    
    # Send a GET request to fetch the HTML content
    response = requests.get(url)
    
    
    # Sleep 
    time.sleep(0.5)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the roster table
        roster_table = soup.find('table', {'id': 'roster'})
    
        # Check if the table was found
        if roster_table:
            # Iterate through table rows and extract player names and numbers
            for row in roster_table.find_all('tr')[1:]:  # Skip the header row
                cols = row.find_all('th')
                if len(cols) >= 0:  # Ensure there are enough columns
                    player_number = cols[0].text.strip()  # Player number
                cols = row.find_all('td')
                if len(cols) >= 3:  # Ensure there are enough column
                    player_name = cols[0].text.strip()  # Player name
                    players_data.append({
                        'Player Name': player_name,
                        'Number': player_number,
                        'Team': t
                    })
            
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        print(t)

df = pd.DataFrame(players_data)

df.to_csv('players.csv', index=False)

# To load the DataFrame back
loaded_df = pd.read_csv('players.csv')