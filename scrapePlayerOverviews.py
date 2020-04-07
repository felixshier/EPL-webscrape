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
playerOverviews = []
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
                playerOverviews.append(playerURL)
            break
        # exception written for the case that data is requested too frequently from pages
        except:
            time.sleep(5)
            continue

# list of valid positions
validPositions = ['Goalkeeper', 'Midfielder', 'Defender', 'Forward']

# empty lists for all data we want to grab
names = []
clubs = []
ages = []
heights = []
weights = []
nations = []
positions = []

# loop through every player link in list 'players'
# import and parse players web page
# find data and add to list
# if there is an exception (i.e. data doesn't exist) append 'None'
for playerURL in playerOverviews:
    playerPage = requests.get(playerURL)
    playerSoup = BeautifulSoup(playerPage.content, 'html.parser')

    # scrape names
    try:
        playerName = playerSoup.findAll('div', {'class': 'name'})
        playerName = playerName[0].text.strip()
        names.append(playerName)
    except:
        names.append(None)

    # scrape clubs
    try:
        playerClub = playerSoup.findAll('td', {'class': 'team'})
        playerClub = playerClub[0].findAll('span', {'class': 'short'})
        playerClub = playerClub[0].text.strip()
        clubs.append(playerClub)
    except:
        ages.append(None)

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

    # scrape ages
    try:
        playerAge = playerSoup.findAll('ul', {'class': 'pdcol2'})
        playerAge = playerAge[0].findAll('span', {'class': 'info--light'})
        playerAge = playerAge[0].text.strip().replace('(', '').replace(')', '')
        ages.append(playerAge)
    except:
        ages.append(None)

    # scrape heights
    try:
        playerPhysical = playerSoup.findAll('ul', {'class': 'pdcol3'})
        playerPhysical = playerPhysical[0].findAll('div', {'class': 'info'})
        playerHeight = playerPhysical[0].text.strip()
        heights.append(playerHeight)
    except:
        heights.append(None)

    # scrape weights
    try:
        playerPhysical = playerSoup.findAll('ul', {'class': 'pdcol3'})
        playerPhysical = playerPhysical[0].findAll('div', {'class': 'info'})
        playerWeight = playerPhysical[1].text.strip()
        weights.append(playerWeight)
    except:
        weights.append(None)

    # scrape nationalities
    try:
        playerNation = playerSoup.findAll('ul', {'class': 'pdcol1'})
        playerNation = playerNation[0].findAll('div', {'class': 'info'})
        playerNation = playerNation[0].text.strip()
        nations.append(playerNation)
    except:
        nations.append(None)

# create dictionary containing all lists as well as headers
d = {
    'Name': names,
    'Position': positions,
    'Club': clubs,
    'Nationality': nations,
    'Age': ages,
    'Height': heights,
    'Weight': weights
    }
# dictionary -> dataframe
playerOverview = pd.DataFrame(d)

playerOverview.dropna(axis = 0, inplace = True)
playerOverview.reset_index(drop=True, inplace=True)

loan = []
for i in range(len(playerOverview)):
    club = playerOverview['Club'][i]
    if '(Loan)' in club:
        loan.append(True)
        club = club.replace('(Loan)', '')
        playerOverview['Club'][i] = club
    else:
        loan.append(False)
playerOverview['On Loan'] = loan

# remove 'cm' from Height collumn then turn Height into an integer value
for i in range(len(playerOverview)):
            height = playerOverview['Height'][i]
            newHeight = ''
            for letter in height:
                if not(letter.isalpha()):
                    newHeight += letter
            newHeight = int(newHeight)
            playerOverview['Height'][i] = newHeight
            
# remove 'kg' from Weight collumn then turn Weight into an integer value
for i in range(len(playerOverview)):
            weight = playerOverview['Weight'][i]
            newWeight = ''
            for letter in weight:
                if not(letter.isalpha()):
                    newWeight += letter
            newWeight = int(newWeight)
            playerOverview['Weight'][i] = newWeight
            
playerOverview.rename(columns={'Height': 'Height (cm)', 'Weight': 'Weight (kg)'}, inplace=True)            

# export to .csv
playerOverview.to_csv(r'C:\Users\Felix\Documents\pl_scrape\playerOverviews.csv')
