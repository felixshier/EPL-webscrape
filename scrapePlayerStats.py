import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

# import & parse webpage consisting of all premier league clubs
URL = "https://www.premierleague.com"
page = requests.get(URL + "/clubs")
soup = BeautifulSoup(page.content, 'html.parser')

# create a list containing the links for all premier league club squad web pages
clubLinks = soup.findAll('a', {'class': 'indexItem'})
clubs = []
for link in clubLinks:
    clubURL = URL + link['href']
    clubURL = clubURL.replace("overview", "squad")
    clubs.append(clubURL)

# loop through each club, appending the link to each players web page to the list 'players'
playerStats = []
for club in clubs:
    while True:
        # import and parse club web pages, 'a' tags
        try:
            clubPage = requests.get(club)
            clubSoup = BeautifulSoup(clubPage.content, 'html.parser')
            playerLinks = clubSoup.findAll('a', {'class': 'playerOverviewCard'})

            # grabs links to each players web page and append to list 'players'
            for link in playerLinks:
                playerURL = URL + link['href']
                playerURL = playerURL.replace("overview", "stats")
                playerStats.append(playerURL)
            break
        # exception written for the case that data is requested too frequently from pages
        except:
            time.sleep(5)
            continue
# list of valid positions
validPositions = ['Goalkeeper', 'Midfielder', 'Defender', 'Forward']

# empty lists for all data we want to grab
names = []
apps = []
positions = []
cs = []
goals = []
assists = []

# loop through every player link in list 'players'
# import and parse players web page
# find data and add to list
# if there is an exception (i.e. data doesn't exist) append 'None'
for playerURL in playerStats:
    playerPage = requests.get(playerURL)
    playerSoup = BeautifulSoup(playerPage.content, 'html.parser')

    # scrape names
    try:
        playerName = playerSoup.findAll('div', {'class': 'name'})
        playerName = playerName[0].text.strip()
        names.append(playerName)
    except:
        names.append(None)

    # scrape appearances
    try:
        playerApps = playerSoup.findAll('span', {'class': 'allStatContainer statappearances'})
        playerApps = playerApps[0].text.strip()
        apps.append(playerApps)
    except:
        apps.append(None)

    # scrape positions
    try:
        temp = playerSoup.findAll('div', {'class': 'info'})
        tempPosition = temp[1].text.strip()
        if tempPosition in validPositions:
            playerPosition = tempPosition
        else:
            tempPosition = temp[0].text.strip()
            playerPosition = tempPosition
        positions.append(playerPosition)
    except:
        positions.append(None)

    # if goalkeeper or defender
    # scrape clean sheets
    if ((playerPosition == 'Goalkeeper') or (playerPosition == 'Defender')):
        try:
            playerCS = playerSoup.findAll('span', {'class': 'allStatContainer statclean_sheet'})
            playerCS = playerCS[0].text.strip()
            cs.append(playerCS)
        except:
            cs.append(None)

    else:
        cs.append(None)

    # scrape goals
    try:
        playerGoals = playerSoup.findAll('span', {'class': 'allStatContainer statgoals'})
        playerGoals = playerGoals[0].text.strip()
        goals.append(playerGoals)
    except:
        goals.append(None)

    # scrape assists
    try:
        playerAssists = playerSoup.findAll('span', {'class': 'allStatContainer statgoal_assist'})
        playerAssists = playerAssists[0].text.strip()
        assists.append(playerAssists)
    except:
        assists.append(None)

# create dictionary containing all lists as well as headers
d = {
    'Name': names,
    'Position': positions,
    'Appearances': apps,
    'Clean Sheets': cs,
    'Goals': goals,
    'Assists': assists
}
# dictionary -> dataframe
playerStats = pd.DataFrame(d)
# export to .csv
playerStats.to_csv(r'C:\Users\Felix\Documents\pl_scrape\playerStats.csv')
