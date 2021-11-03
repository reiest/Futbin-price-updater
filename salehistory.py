import requests
import pandas as pd
import numpy as np
import time
import datetime
from openpyxl import load_workbook
import math
from statistics import mode
import statistics as st

platform = "xone"  # Xbox = xone,    Playstation = ps,   PC = pc
directory = "icons450"  # Change to directory you want to use (category, ex: icons, heros, silvers)
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

# Returns lowest, mean and highest sale
def calculations(pricelist):
    lowest = min(pricelist)
    average = np.mean(pricelist)
    highest = max(pricelist)
    median = st.median(pricelist)
    return lowest, average, highest, median

# Find 95% of all sales are between this interval
def percent_of_data(pricelist):
    prices = sorted(pricelist, reverse=False)
    percents = int(round(len(pricelist) * 0.025))
    liste = prices[percents:-percents]
    low = min(liste)
    high = max(liste)
    average = np.mean(liste)
    interval = (low, high)
    return interval, int(average)


# Find buyprice (currenly set buyprice to 10% lower than average, 5% profit after tax)
def buyprices(average, low):
    if (average * 0.9) < low:
        buy = int(average * 0.9)
    else:
        buy = int(low)
    buy = int(math.floor(buy / 1000))
    return int(buy)


# Most frequent/common sell price and how many sales has been at that price
def most_frequent(pricelist):
    frequent = mode(pricelist)
    amount = pricelist.count(frequent)
    return frequent, amount


# Percentage of sales a given percentage over the average price
# Ex: Average price: 100k. If percentage is 5%, this check how many % of sales are over 105k
def sales_over_average(pricelist, average, percentage):
    per = int(average * percentage)
    new_list = []
    for i in pricelist:
        if i > (per):
            new_list.append(i)
    compare = len(new_list) / len(pricelist)
    return compare


database = {}
playercount = 0
for (name, ID) in players.items():
    # Don't change this, you can be IP banned from futbin if you send too many requests within a time limit.
    time.sleep(2)
    tempdata = {}  # Temporary data

    # Gets player's sale data
    link = 'https://www.futbin.com/getPlayerChart?type=live-sales&resourceId=' + \
        str(ID) + '&platform=' + platform
    r_sell = requests.get(link)
    r_data = r_sell.json()

    # Prints the progress, how many players have been processed
    print(str(playercount + 1) + "/" + str(len(players)), end=": ")
    print(name)

    sales_list = []  # List of all sale prices, used for calculations
    for data in r_data:
        sales_list.append(data[1])
    date = r_data[0][0]  # First date in sales list
    low_price, avg_price, high_price, median = calculations(sales_list)
    percent, avg = percent_of_data(sales_list)
    buyprice = buyprices(avg, percent[0])
    frequent_saleprice, frequency = most_frequent(sales_list)
    sales_over_avg = sales_over_average(sales_list, avg_price, 1.025)

    # Updates temporary data
    tempdata.update({"ID": ID, "Name": name, "Buyprice": buyprice, "Lowest": low_price, "Average": avg_price,
                     "Median": median, "Highest": high_price, "95% of sales": percent,
                     "Most frequent": frequent_saleprice, "Frequency": frequency,
                     "Occurency rate (+2.5%)": sales_over_avg, "First sale data": date})
    database.update({tempdata['ID']: tempdata})  # Updates database
    playercount += 1

# Write data to excel
date = str(datetime.datetime.now().date())
ExcelWorkbook = load_workbook(directory+"/"+exc)
writer = pd.ExcelWriter(directory+"/"+exc, engine='openpyxl')
writer.book = ExcelWorkbook
df = pd.DataFrame(database).T
df.to_excel(writer, sheet_name=date)
writer.save()

print("Done, check excel file")
