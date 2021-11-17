import requests
import pandas as pd
import numpy as np
import time
import datetime
from openpyxl import load_workbook
import os

platform = "xone"  # Xbox = xone,    Playstation = ps,   PC = pc
directory = "heroes"  # Change to directory you want to use (category, ex: icons, heros, silvers)
txt = "playerIDs.txt"  # Don't need to change
exc = "playerPrices.xlsx"  # Don't need to change

filereference = open(directory+"/"+txt, "r")

# Make players directory and go through file to append the playersto the directory
players = dict()
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
def buyprices(average, high, low):
    avg_avg = (average + high)/2
    if (avg_avg * 0.9) < int(low)*1.03:
        buy = int((avg_avg * 0.9)//1000)
    else:
        buy = int(((low)*1.03)//1000)
    if average >= 200000:
        buy = int((avg_avg*0.95 - 10000)//1000)
    if average >= 400000:
        buy = int((avg_avg*0.95 - 15000)//1000)
    return int(buy)


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



database = {}
playercount = 0
def find_player_data(liste):
    low_price, avg_price, high_price = calculations(liste)
    price_trend = trend(liste) + "%"
    best_sale_interval = most_sales_interval(avg_price, len(liste))
    buyprice = buyprices(avg_price, best_sale_interval[0][1]*1000, low_price)
    sales_over_avg = sales_over_number(liste, best_sale_interval[0][1]*1000)+"%"
    three = split_in_three(liste)
    return low_price, avg_price, high_price, price_trend, buyprice, best_sale_interval, sales_over_avg, three

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
    low_price, avg_price, high_price, price_trend, buyprice, best_sale_interval, sales_over_avg, three = find_player_data(sales_list)
    
    # Part two, only last 100 sales
    sales_list100 = []  # List of all sale prices, used for calculations
    for data in r_data[-100:]:
        sales_list100.append(data[1])
    date2 = r_data[-100][0]  # First date in sales list
    low_price1, avg_price1, high_price1, price_trend1, buyprice1, best_sale_interval1, sales_over_avg1, three1 = find_player_data(sales_list100)
    rndm = "-"

    # Updates temporary data
    tempdata.update({"Buyprice": buyprice, "Lowest": low_price, "Average": avg_price,
                     "Highest": high_price,"Trend": price_trend, "Most sales int": best_sale_interval,
                     "Occurency rate": sales_over_avg, "Median per 1/3": three, "First sale data": date, "-": rndm,  
                     "Buyprice (100)": buyprice1, "Lowest (100)": low_price1, "Average (100)": avg_price1,
                     "Highest (100)": high_price1,"Trend (100)": price_trend1, "Most sales int (100)": best_sale_interval1,
                     "Occurency rate (100)": sales_over_avg1, "Median per 1/3 (100)": three1, "First sale data (100)": date2})
    database.update({name: tempdata})  # Updates database

    # Prints the progress, how many players have been processed
    print(str(playercount + 1) + "/" + str(len(players)), end=": ")
    print(name)
    playercount += 1

# Write data to excel
date = str(datetime.datetime.now().date())
ExcelWorkbook = load_workbook(directory+"/"+exc)
writer = pd.ExcelWriter(directory+"/"+exc, engine='openpyxl')
writer.book = ExcelWorkbook
df = pd.DataFrame(database).T
df.to_excel(writer, sheet_name=date)
writer.save()

print("Done, opening excel file")
command = "open "+directory+"/"+exc
os.system(command)
