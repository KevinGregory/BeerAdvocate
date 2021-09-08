import pandas as pd 
import time
import random
import re

from bs4 import BeautifulSoup

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import warnings
warnings.filterwarnings('ignore')

headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
}

#Read URL that holds links to all 250
url_main = 'https://www.beeradvocate.com/beer/top-rated/'
response = requests.request("GET", url_main, headers=headers, verify=False)

#Sleep for a few seconds
time.sleep(random.uniform(1,10))
soup = BeautifulSoup(response.content, 'html5lib')

#Get the links
links = []
for link in soup.find_all('a'):
    try:
        if link.get('href')[0:14] == '/beer/profile/':
            links.append('https://www.beeradvocate.com' + link.get('href'))
    except:
        continue
        
links = links[0:len(links):2]

#Loop through links and download information
meta_dict = {}
for url in links:
    response = requests.request("GET", url, headers=headers, verify=False)
    time.sleep(random.uniform(1,10))
    soup = BeautifulSoup(response.content, 'html5lib')
    
    #Dictionary to hold current beer information
    beer_dict = {}
    
    #Beer Title
    title = str(soup.find_all('h1'))
    title =  title[5:title.find('<br/>')]
    beer_dict['Name'] = title

    print(title)
    
    for i in range(len(soup.find_all('b'))):

        #Beer Style
        if str(soup.find_all('b')[i]) == '<b>Style:</b>':
            try:
                style = str(soup.find_all('b')[i+1])
                beer_dict['Style'] = style[3:len(style)-4]
            except:
                beer_dict['Style'] = ''

        #ABV
        if str(soup.find_all('b')[i]) == '<b>ABV:</b>':
            try:
                abv = str(soup.find_all('b')[i+1])
                beer_dict['ABV'] = float(abv[3:len(abv)-5])/100
            except:
                beer_dict['ABV'] = None

        #Score
        if str(soup.find_all('b')[i]) == '<b>Score:</b>':
            try:
                score = str(soup.find_all('b')[i+1])
                beer_dict['Score'] = float(score[3:len(score)-4])
            except:
                beer_dict['Score'] = None

        #Avg
        if str(soup.find_all('b')[i]) == '<b>Avg:</b>':
            try:
                avg = str(soup.find_all('b')[i+1])
                beer_dict['Avg Rating'] = float(avg[104:len(avg)-11])
            except:
                beer_dict['Avg Rating'] = None

    
        #Notes
        try:
            beer_dict['Notes'] = str(soup.find_all('div',attrs = \
                                                   {'style':'clear:both; margin:0; padding:0px 20px; font-size:1.05em;'}))\
                                                    .split('</b>')[1].replace('\t</div>]','').replace('\n','')
        except:
            beer_dict['Notes'] = None
            
        #Reviews. A lot of specific HTML tags here.
        reviews = ''
        for i in range(len(str(soup.find_all('div',{'id':'rating_fullview_content_2'})).split('<span class="muted">'))):
            review = str(soup.find_all('div',{'id':'rating_fullview_content_2'})).split('<span class="muted">')[i]
            if 'rDev' in review or 'href' in review:
                continue
            else:
                reviews += review
        
        beer_dict['reviews']=reviews.replace('[<div id="rating_fullview_content_2">','').replace('</span>','')\
        .replace('<br/','').replace('\n','').replace('>','')

        #Add beer to Meta Beer Dictionary
        meta_dict[beer_dict['Name']] = beer_dict
        
top_250 = pd.DataFrame.from_dict(meta_dict, orient='index').reset_index().drop('index', axis = 1)

top_250.to_csv('top_250.csv', index = False)
