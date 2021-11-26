import requests
import pandas as pd
import numpy as np
import time
import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import openpyxl

platform = "xone"  # Xbox = xone,    Playstation = ps,   PC = pc
directory = "heroes"  # Change to directory you want to use (category, ex: icons, heros, silvers)
want_pdf = 1 # Change to 1 if you want pdf with graphs, and 0 for no pdf
txt = "playerIDs.txt"  # Don't need to change
exc = "playerPrices.xlsx"  # Don't need to change
pdf = "SaleGraphs.pdf" # Don't need to change
 
filereference = open(directory+"/"+txt, "r")

# Make players directory and go through file to append the playersto the directory
players = dict()
print("Starting up...")
for line in filereference:
    line_stripped = line.strip()
    line_split = line_stripped.split(":")
    player = line_split[0].split("'")
    ID = line_split[1].split(",")
    ID = ID[0].strip()
    ID = int(ID)
    players[player[1]] = ID


# Cuts off 2% of lowest sales and 2% of highest sales so the deviation is gone
# Calculates the lowest, average, highest sales.
def calculations(pricelist):
    pricelist_copy = pricelist.copy() 
    prices = sorted(pricelist_copy, reverse=False)
    percents = int(round(len(pricelist) * 0.02))
    liste = prices[percents:-percents]
    low, high = min(liste), max(liste)
    average = np.mean(liste)
    return low, int(average), high


# Returns if the price is on uptrend or downtrend
def trend(pricelist):
    lengde = int(len(pricelist)//2)
    part1 = pricelist[:lengde]
    part2 = pricelist[lengde:]
    avg1 = np.mean(part1)
    avg2 = np.mean(part2)
    return str(round(((avg2-avg1)/avg1)*100, 1))


# Find buyprice (currently set buyprice to 10% lower than average, 5% profit after tax)
def buyprices(average, high, fluct, low):
    avg_avg = (average + high)/2
    buy = average*(0.9+fluct)
    #buy = ((buy1 + buy2)/2) // 1000
    if buy < int(low):
        buy = int(low)
    if buy > average*0.95:
        buy = average*0.9
    if average >= 200000:
        buy = int((avg_avg*0.95 - 10000)//1000)
    if average >= 400000:
        buy = int((avg_avg*0.95 - 15000)//1000)
    return int(buy//1000)


# Most sales happen in these 5 percent
def most_sales_interval(avg, rng):
    rng = int(rng)
    count = 0
    commons = 0
    percennn = int((avg*0.025)//250)*250
    if percennn < 1000:
        percennn = 1000
    for i in range(min(sales_list[-rng:])+percennn,max(sales_list[-rng:])-percennn,250):
        internalcount = 0
        for j in range(-percennn,percennn+1,250):
            internalcount += sales_list[-rng:].count(i + j)
        if internalcount > count:
            count = internalcount
            commons = i
    interval = (int((commons-percennn)//1000),int((commons+percennn)//1000))
    return interval, count

# Percentage of sales over a given number
def sales_over_number(pricelist, number):
    new_list = []
    for price in pricelist:
        if price >= number:
            new_list.append(price)
    compare = (len(new_list) / len(pricelist))*100
    compare = round(compare,1)
    return str(compare)

# Median per three
def split_in_three(pricelist):
    lengde = len(pricelist)//3
    pt1 = np.median(pricelist[:lengde])
    pt2 = np.median(pricelist[lengde:lengde*2])
    pt3 = np.median(pricelist[-lengde:])
    return (int(pt1),int(pt2),int(pt3))

def timedifference(date):
    if date.find("21,") != -1:
        date = date.replace("21,", "2021")
    if date.find("22,") != -1:
        date = date.replace("22,", "2022")
    if date.find("pm") != -1:
        date = date.replace(" pm","")
    if date.find("am") != -1:
        date = date.replace(" am","")
    conve = datetime.datetime.strptime(date, "%b %d %Y %H:%M")
    now = datetime.datetime.now()
    diff = now - conve
    differnce_hrs = str(diff.days)+ " day(s) & "+ str(int(diff.seconds/3600)) + " hrs"
    return differnce_hrs

def plotgraph(x,date,title, mean, buyprice):
    fig = plt.figure(figsize=(12,5))
    plt.ylabel("Price")
    xlabel = "Last " + str(date)
    plt.xlabel(xlabel)
    y_avg = [mean]*len(x)
    y_buy = [buyprice*1000]*len(x)
    plt.title(title, fontsize=20)
    plt.plot(x, "b-", alpha=0.15,linewidth=1, label="Sales")
    plt.plot(x, "b.", markersize=4)
    avg_label = "Average: "+str(int(mean))
    plt.plot(y_avg, "m",label=avg_label, linestyle="--")
    buy_label = "Buyprice: "+str(buyprice)
    plt.plot(y_buy, "g",label=buy_label, linestyle="--")
    plt.legend(loc=2)
    y =[]
    for i in range(len(x)):
        y.append(i)
    plt.fill_between(y,x, alpha=0.15)
    if min(x) > buyprice*1000:
        btm = int((buyprice*1000)//1.05)
    else:
        btm = int(min(x)//1.05)
    plt.ylim(bottom=btm)
    plt.xlim(0,y[-1])
    plt.close()
    return fig

database = {}
playercount = 0
def find_player_data(liste):
    low_price, avg_price, high_price = calculations(liste)
    sorted_list = sorted(liste)
    lengde = int(len(liste)*0.9)
    potato = sorted_list[lengde]
    fluctuation = ((potato-avg_price)/avg_price)/2.2
    price_trend = trend(liste) + "%"
    best_sale_interval = most_sales_interval(avg_price, len(liste))
    buyprice = buyprices(avg_price, best_sale_interval[0][1]*1000, fluctuation, low_price)
    sales_over_avg = sales_over_number(liste, best_sale_interval[0][1]*1000)+"%"
    three = split_in_three(liste)
    return low_price, avg_price, high_price, price_trend, buyprice, best_sale_interval, sales_over_avg, three

if want_pdf == 1:
    pp = PdfPages(directory+"/"+pdf)
for (name, ID) in players.items():
    # Don't change this, you can be IP banned from futbin if you send too many requests within a time limit.
    time.sleep(1)
    tempdata = {}  # Temporary data

    # Gets player's sale data
    link = 'https://www.futbin.com/getPlayerChart?type=live-sales&resourceId=' + \
        str(ID) + '&platform=' + platform
    r_sell = requests.get(link)
    r_data = r_sell.json()

    sales_list = []  # List of all sale prices, used for calculations
    for data in r_data:
        sales_list.append(data[1])
    date = r_data[0][0]  # First date in sales list
    time1 = timedifference(date)
    low_price, avg_price, high_price, price_trend, buyprice, best_sale_interval, sales_over_avg, three = find_player_data(sales_list)
    
    # Part two, only last 100 sales
    sales_list100 = []  # List of all sale prices, used for calculations
    for data in r_data[-100:]:
        sales_list100.append(data[1])
    date2 = r_data[-100][0]  # First date in sales list
    time2 = timedifference(date2)
    low_price1, avg_price1, high_price1, price_trend1, buyprice1, best_sale_interval1, sales_over_avg1, three1 = find_player_data(sales_list100)
    rndm = "-"

    if want_pdf == 1:
        plot1 = plotgraph(sales_list, time1, str(name),avg_price,buyprice)
        plot2 = plotgraph(sales_list100, time2, str(name),avg_price1,buyprice1)
        pp.savefig(plot1)
        pp.savefig(plot2)

    # Updates temporary data
    tempdata.update({"Buyprice": buyprice, "Lowest": low_price, "Average": avg_price,
                     "Highest": high_price,"Trend": price_trend, "Most sales int": best_sale_interval,
                     "Occurency rate": sales_over_avg, "Median per 1/3": three, "Data from last": time1, "-": rndm,  
                     "Buyprice (100)": buyprice1, "Lowest (100)": low_price1, "Average (100)": avg_price1,
                     "Highest (100)": high_price1,"Trend (100)": price_trend1, "Most sales int (100)": best_sale_interval1,
                     "Occurency rate (100)": sales_over_avg1, "Median per 1/3 (100)": three1, "Data from last(100)": time2})
    database.update({name: tempdata})  # Updates database

    # Prints the progress, how many players have been processed
    print(str(playercount + 1) + "/" + str(len(players)), end=": ")
    print(name)
    playercount += 1

# Write data to excel
date = str(datetime.datetime.now().date())
ExcelWorkbook = openpyxl.load_workbook(directory+"/"+exc)
writer = pd.ExcelWriter(directory+"/"+exc, engine='openpyxl')
worksheets = ExcelWorkbook.sheetnames
while len(worksheets) > 3:
    rmv = ExcelWorkbook[worksheets[0]]
    ExcelWorkbook.remove(rmv)
    worksheets = ExcelWorkbook.sheetnames
writer.book = ExcelWorkbook
df = pd.DataFrame(database).T
df.to_excel(writer, sheet_name=date)
writer.save()
if want_pdf == 1:
    pp.close()

print("Done, opening excel file...")
command = "open "+directory+"/"+exc
os.system(command)
if want_pdf == 1:
    command2 = "open "+directory+"/"+pdf
    os.system(command2)
