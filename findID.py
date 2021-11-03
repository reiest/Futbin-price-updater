import requests
import bs4
import time
import os

dirName = input("Name of new directory: ")
os.mkdir(dirName)
file = open(dirName + "/playerID.txt", "w")

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
listLink = []
for name in names:
    link = name.get('href')
    link = "https://www.futbin.com" + link
    listLink.append(link)

if numberPages >= 2:
    for i in range(2,numberPages+1):
        link = 'https://www.futbin.com/players?page='+ str(i) + '&wf=4&skills=4&version=icons'
        res = requests.get(link)
        soup = bs4.BeautifulSoup(res.text, features='lxml')
        names = soup.select('td > div > div > a')
        for name in names:
            link = name.get('href')
            link = "https://www.futbin.com" + link
            listLink.append(link)

# Fixa så att alla spelarstats sparas
playerCounter = 0
for links in listLink:
    res = requests.get(links)
    time.sleep(1)
    soup = bs4.BeautifulSoup(res.content, features='lxml')

    # Player ID
    player_id = soup.find('div', {'id': 'page-info'}).get('data-player-resource')
    cName = soup.select('.pcdisplay-name')
    cardName = cName[0].getText().strip()
    rt = soup.select('.pcdisplay-rat')
    rating = rt[0].getText().strip()

    # förklarar vart i processen det är
    print(str(playerCounter + 1) + "/" + str(len(listLink)), end=": ")
    print(cardName)

    string = "'" + cardName + " " + rating + "': " + player_id + ","
    file.write(string + "\n")

    playerCounter += 1

file.close()

print("Check file")
