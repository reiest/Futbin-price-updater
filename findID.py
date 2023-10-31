import cloudscraper
import bs4
import time
import os
from openpyxl import Workbook
import unicodedata

dirName = input("Name of new directory: ")
os.mkdir(dirName)
file = open(dirName + "/playerIDs.txt", "w")
wb = Workbook()
ws = wb.active
ws.title = "Initiate"
wb.save(filename=dirName+"/playerPrices.xlsx")

scraper = cloudscraper.create_scraper()

# Find players from 1st page
URL = 'https://www.futbin.com/22/players?page=1&ps_price=2000-20000&league=13&version=gold_rare'
res = scraper.get(URL).text
soup = bs4.BeautifulSoup(res, features='lxml')
names = soup.select('td > div > div > a')

# Number of pages to iterate through
if URL.find("/22/") != 1:
    URL = URL.replace("m/pl", "m/22/pl")
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
        res = scraper.get(new_link).text
        soup = bs4.BeautifulSoup(res, features='lxml')
        names = soup.select('td > div > div > a')
        for name in names:
            link = name.get('href')
            link = "https://www.futbin.com" + link
            links.append(link)

def remove_accents(playername):
    try:
        playername = unicode(playername, 'utf-8')
    except NameError: 
        pass
    playername = unicodedata.normalize('NFD', playername).encode('ascii', 'ignore').decode("utf-8")
    return str(playername)


# Finds all IDs and sends them into a text file
playerCounter = 0
for link in links:
    res = scraper.get(link).text
    time.sleep(0.5)
    soup = bs4.BeautifulSoup(res, features='lxml')

    # Player ID
    player_id = soup.find('div', {'id': 'page-info'}).get('data-player-resource')
    cName = soup.select('.pcdisplay-name')
    cardName = cName[0].getText().strip()
    cardName = remove_accents(cardName)
    rt = soup.select('.pcdisplay-rat')
    rating = rt[0].getText().strip()

    # Writes players to file
    string = "'" + cardName + " " + rating + "': " + player_id + ","
    file.write(string + "\n")

    playerCounter += 1
    print(playerCounter, "/", len(links), ":", cardName)

file.close()

command = "sort "+dirName+"/playerIDs.txt -o "+dirName+"/playerIDs.txt"
os.system(command)
print("Check file")
