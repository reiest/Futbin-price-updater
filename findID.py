import requests
import bs4
import pandas as pd


# Fixa spelarnamn
res = requests.get('https://www.futbin.com/22/players?page=1&league=4&position=CDM,CM,CAM&pdribbling=75,0')
soup = bs4.BeautifulSoup(res.text, features='lxml')

# ta fram namn
names = soup.select('td > div > div > a')

# rating
ratings = soup.select('.form')

# ta fram antal sidor
pages = soup.select('.page-link')

# rakna fram hur maanga sidor som ska gaas igenom
sistaSidan = (len(pages))
antalSidor = pages[sistaSidan-2].get_text()

# initiera lista med alla namn
listName = []
listLink = []
listRating = []

# spara namn och fullstandig lank till lista
for name in names:
    name = name.get_text()
    listName.append(name)

for name in names:
    link = name.get('href')
    link = "https://www.futbin.com" + link
    listLink.append(link)
    
for rating in ratings:
    rating = rating.get_text()
    listRating.append(rating)
############

############

# ta fram namn for resterande sidor paa hemsidan
for page in range(int(antalSidor)):
    #print(f"{page+1}/{int(antalSidor)-1}")
    # Fixa spelarnamn
    res = requests.get('https://www.futbin.com/22/players?page='+page+'&league=4&position=CDM,CM,CAM&pdribbling=75,0')
    soup = bs4.BeautifulSoup(res.text, features='lxml')

    # ta fram namn
    names = soup.select('td > div > div > a')
    # = soup.findAll('span', {'class': 'form rating ut22 icon gold rare'})
    ratings = soup.select('.form')
    
    # spara namn och fullstandig lank till lista
    for name in names:
        name = name.get_text()
        listName.append(name)

    for name in names:
        link = name.get('href')
        link = "https://www.futbin.com" + link
        listLink.append(link)
    
    for rating in ratings:
        rating = rating.get_text()
        listRating.append(rating)

############

print(listRating)
# init databas
database = {}

# Fixa saa att alla spelarstats sparas
playerCounter = 0
for links in listLink:
    # FIXA VARJE SPELARES STATS
    res = requests.get(links)
    soup = bs4.BeautifulSoup(res.content, features='lxml')
    
    # spara ner stats och vad det ar for stats
    stats = soup.select('.stat_val')
    statText = soup.select('div.stat_holder_sub.left_stat_name > span')
    
    # ID
    IDtext = soup.select('#page-data')
    spelarID = IDtext[0].get('data-player-id').strip()
    
    # INFO
    infoStats = soup.select('.table-row-text')
    infoText = soup.select('tr > th')
    
    # Header name
    hName = soup.select('.header_name')
    headerName = hName[0].getText().strip()
    
    # forklarar vart i processen det ar
    #print(str(playerCounter + 1) + "/" + str(len(listName)), end=": ")
    print(headerName)

    # lagg alla stats i en dict
    tempStats = {}
    
    # lagg info i en temporar dict
    statsCounter = 0
    for i in infoText:
        namnPaaInfo = i.getText().strip()
        vardePaaInfo = infoStats[statsCounter].getText().strip()
        
        # visa endast cm paa langd
        if namnPaaInfo == "Height":
            vardePaaInfo = vardePaaInfo[:3]
        
        # lagg till i tempStats
        tempStats.update({namnPaaInfo : vardePaaInfo})
        statsCounter += 1
    
    # lagg stats, headerName och ID i samma temporara dict
    counter = 0
    for i in statText:
        namnPaaStats = (i.getText().strip())
        vardePaaStats = (stats[counter].getText().strip())
        tempStats.update({namnPaaStats : vardePaaStats, "ID" : spelarID, "Header Name": headerName})
        counter += 1

    # uppdatera databasen for spelaren
    database.update({tempStats['ID'] : tempStats})
    playerCounter += 1
    
############
# skriv till excel

df = pd.DataFrame(database).T
df.to_excel('Futbin - FIFA 21.xlsx')

print("Klar ")