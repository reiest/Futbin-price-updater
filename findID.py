import requests
import bs4
import time
import os
from openpyxl import Workbook

dirName = input("Name of new directory: ")
os.mkdir(dirName)
file = open(dirName + "/playerIDs.txt", "w")
wb = Workbook()
ws = wb.active
ws.title = "Initiate"
wb.save(filename=dirName+"/playerPrices.xlsx")

# Find players from 1st page
res = requests.get(
    'https://www.futbin.com/players?page=1&wf=4&skills=4&version=icons')
soup = bs4.BeautifulSoup(res.text, features='lxml')
names = soup.select('td > div > div > a')

# Number of pages to iterate through
try:
    pages = soup.select('.page-link')
    numberPages = int(pages[-2].get_text().strip())
except:
    numberPages = 1

# Find all links to players
links = []
for name in names:
    link = name.get('href')
    link = "https://www.futbin.com" + link
    links.append(link)

# Find players from other pages
if numberPages >= 2:
    for i in range(2, numberPages+1):
        link = 'https://www.futbin.com/players?page=' + \
            str(i) + '&wf=4&skills=4&version=icons'
        res = requests.get(link)
        soup = bs4.BeautifulSoup(res.text, features='lxml')
        names = soup.select('td > div > div > a')
        for name in names:
            link = name.get('href')
            link = "https://www.futbin.com" + link
            links.append(link)

# Finds all IDs and sends them into a text file
playerCounter = 0
for links in links:
    res = requests.get(links)
    time.sleep(1)
    soup = bs4.BeautifulSoup(res.content, features='lxml')

    # Player ID
    player_id = soup.find('div', {'id': 'page-info'}
                          ).get('data-player-resource')
    cName = soup.select('.pcdisplay-name')
    cardName = cName[0].getText().strip()
    rt = soup.select('.pcdisplay-rat')
    rating = rt[0].getText().strip()

    # Writes players to file
    string = "'" + cardName + " " + rating + "': " + player_id + ","
    file.write(string + "\n")

    playerCounter += 1
    print(playerCounter, "/", len(links), ":", cardName)

file.close()

print("Check file")
