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
URL = "https://www.futbin.com/players?page=1&pos_type=all&ps_price=0-230000&version=icons"
res = scraper.get(URL).text
soup = bs4.BeautifulSoup(res, features='lxml')

# Number of pages to iterate through
try:
    pages = soup.select('.page-link')
    numberPages = int(pages[-2].get_text().strip())
except:
    numberPages = 1


def find_player_links(number_of_pages):
    links = []
    for i in range(1, number_of_pages+1):
        url = URL.replace("page=1", f"page={i}")
        res = scraper.get(url).text
        soup = bs4.BeautifulSoup(res, features='lxml')
        names = soup.select('td > div > div > a')
        for name in names:
            link = name.get('href')
            link = "https://www.futbin.com" + link
            links.append(link)
    return links


def remove_accents(playername):
    try:
        playername = unicode(playername, 'utf-8')
    except NameError:
        pass
    playername = unicodedata.normalize('NFD', playername).encode(
        'ascii', 'ignore').decode("utf-8")
    return str(playername)


links = find_player_links(numberPages)

# Finds all IDs and sends them into a text file
playerCounter = 0
with open(dirName + "/playerIDs.txt", "w") as file:
    for link in links:
        res = scraper.get(link).text
        time.sleep(0.5)
        soup = bs4.BeautifulSoup(res, features='lxml')

        # Player ID
        player_id = soup.find(
            'div', {'id': 'page-info'})['data-player-resource']
        cName = soup.select_one('.pcdisplay-name')
        cardName = remove_accents(cName.getText().strip())
        rating = soup.select_one('.pcdisplay-rat').getText().strip()

        # Writes players to file
        string = f"'{cardName} {rating}': {player_id},"
        file.write(string + "\n")

        playerCounter += 1
        print(f"{playerCounter}/{len(links)}: {cardName}")

# Sort the playerIDs.txt file
command = f"sort {dirName}/playerIDs.txt -o {dirName}/playerIDs.txt"
os.system(command)
