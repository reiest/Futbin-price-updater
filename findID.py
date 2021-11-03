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
URL = 'https://www.futbin.com/22/players?page=1&version=fut_heroes&sort=Player_Rating&order=asc'
res = requests.get(URL)
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
        new_link = ""
        count = 0
        for j, c in enumerate(URL):
            if c.isdigit() and count < 3:
                if count < 2:
                    count += 1
                    new_link += c
                    continue
                count += 1
                new_link += str(i)
                continue
            new_link += c
        res = requests.get(new_link)
        soup = bs4.BeautifulSoup(res.text, features='lxml')
        names = soup.select('td > div > div > a')
        for name in names:
            link = name.get('href')
            link = "https://www.futbin.com" + link
            links.append(link)

# Finds all IDs and sends them into a text file
playerCounter = 0
for link in links:
    res = requests.get(link)
    time.sleep(1)
    soup = bs4.BeautifulSoup(res.content, features='lxml')

    # Player ID
    player_id = soup.find('div', {'id': 'page-info'}).get('data-player-resource')
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
