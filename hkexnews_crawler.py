# -*- coding: utf-8 -*-
"""hkexnews_crawler.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aBbeMfS7zCyPCsVPoo239zq2bjhwUvdz

### hkexnews crawler

- Date : 2021-01-20
- Author : Hyewon Jung
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from urllib.request import urlopen
import lxml.html
import time
import json
import csv
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns

headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3)'}

today = datetime.today().strftime('%Y%m%d')
end_date = '2021/01/19'
stock_code = '00001'

url = 'https://www.hkexnews.hk/sdw/search/searchsdw.aspx?__EVENTTARGET=btnSearch&__VIEWSTATE=/wEPDwULLTIwNTMyMzMwMThkZLiCLeQCG/lBVJcNezUV/J0rsyMr&_VIEWSTATEGENERATOR=A7B2BBE2\
&sortBy=shareholding&sortDirection=desc&today=%s&txtShareholdingDate=%s&txtStockCode=%s' % (today, end_date, stock_code)
print(url)

result = requests.get(url, headers = headers)
soup = BeautifulSoup(result.content, "html.parser")

data = soup.findAll("div", {"class": "mobile-list-body"})

participant_id = []
name = []
address = []
shareholding = []
percentage_total = []

total_dt = pd.DataFrame([])

lst = list(range(0, 50))
for i in range(int(len(lst)/5)):
  l = lst[i*5:(i+1)*5]

  participant_id.append(data[l[0]].text)
  name.append(data[l[1]].text)
  address.append(data[l[2]].text)
  shareholding.append(data[l[3]].text)
  percentage_total.append(data[l[4]].text)

total_dt = pd.DataFrame({
    'Participant_Id' : participant_id,
    'Name_of_CCASS_Participant' : name,
    'Addess' : address,
    'Shareholding' : shareholding,
    '%_of_the_total_number_of_Issued' : percentage_total
                         })

def get_holdings_data(today, end_date, stock_code):
    headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3)'}
    url = 'https://www.hkexnews.hk/sdw/search/searchsdw.aspx?__EVENTTARGET=btnSearch&__VIEWSTATE=/wEPDwULLTIwNTMyMzMwMThkZLiCLeQCG/lBVJcNezUV/J0rsyMr&_VIEWSTATEGENERATOR=A7B2BBE2\
    &sortBy=shareholding&sortDirection=desc&today=%s&txtShareholdingDate=%s&txtStockCode=%s' % (today, end_date, stock_code)

    result = requests.get(url, headers = headers)
    soup = BeautifulSoup(result.content, "html.parser")

    data = soup.findAll("div", {"class": "mobile-list-body"})

    participant_id = []
    name = []
    address = []
    shareholding = []
    percentage_total = []

    total_dt = pd.DataFrame([])

    lst = list(range(0, 50))
    for i in range(int(len(lst)/5)):
      l = lst[i*5:(i+1)*5]

      participant_id.append(data[l[0]].text)
      name.append(data[l[1]].text)
      address.append(data[l[2]].text)
      shareholding.append(data[l[3]].text)
      percentage_total.append(data[l[4]].text)

    total_dt = pd.DataFrame({
        'Participant_Id' : participant_id,
        'Name_of_CCASS_Participant' : name,
        'Address' : address,
        'Shareholding' : shareholding,
        '%_of_the_total_number_of_Issued' : percentage_total
    })
    return total_dt

today = datetime.today().strftime('%Y%m%d')
end_date = '2021/01/19'
stock_code = '00001'

get_holdings_data(today, end_date, stock_code)

"""#### __Tab 1 - trend plot__"""

total_dt

# Plot the "Shareholding" of the top 10 participant as of the end date

fig = plt.figure(figsize = (20, 3))
plt.title('Top 10 Shareholding of %s as of %s' % (stock_code, end_date))
plt.bar(total_dt['Name_of_CCASS_Participant'], total_dt['Shareholding'], alpha = 0.8)
plt.show()

plt.figure(figsize=(20,5))
ax = sns.barplot(total_dt['Name_of_CCASS_Participant'], total_dt['Shareholding'].str.replace(',', '').astype(int))
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax.set(xlabel="Name", ylabel='Sharehodling')
for i, v in enumerate(total_dt['Shareholding'].str.replace(',', '').astype(int).iteritems()):        
    ax.text(i ,v[1], "{:,}".format(v[1]), color='black', va ='bottom', rotation=45)
plt.tight_layout()
plt.title('Top 10 Shareholding of %s as of %s' % (stock_code, end_date))
plt.show()

"""#### __Tab 2 - transaction finder__


두 참가자 간에 거래가 있을 수 있으며, 우리는 그들을 탐지하고 싶습니다. % 임계값은 교환된 주식의 최소 %를 입력합니다(예: 1%로 설정된 경우). 하루 중 1%를 초과하여 증감하는 참가자를 찾고, 해당 날짜에 주식을 교환할 수 있는 참가자 ID/명을 나열하십시오.


- Input
> - Stock code
> - Start date
> - End date
> - Threshold % of total number of shares
"""

threshold = 0.01
today = datetime.today().strftime('%Y%m%d')
stock_code = '00001'

start_date = '2021/01/17'
st_dt = get_holdings_data(today, start_date, stock_code)

end_date = '2021/01/19'
end_dt = get_holdings_data(today, end_date, stock_code)

final_dt = st_dt.merge(end_dt, on = ['Participant_Id', 'Name_of_CCASS_Participant', 'Address'])
final_dt['%_of_the_total_number_of_Issued_x'] = final_dt['%_of_the_total_number_of_Issued_x'].str.strip('%').astype(float)/100
final_dt['%_of_the_total_number_of_Issued_y'] = final_dt['%_of_the_total_number_of_Issued_y'].str.strip('%').astype(float)/100
final_dt['change_of_%_of_the_total_number_of_Issued'] = (final_dt['%_of_the_total_number_of_Issued_y']/final_dt['%_of_the_total_number_of_Issued_x'])-1
final_dt.head()

final_dt[final_dt['change_of_%_of_the_total_number_of_Issued'] > threshold][['Participant_Id', 'Name_of_CCASS_Participant']]

f