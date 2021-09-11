import pandas as pd 
import time
import random
import re
import pickle

from bs4 import BeautifulSoup

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import warnings
warnings.filterwarnings('ignore')

headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
}

#FINAL SCRAPER LOOPS
style_links = []

url_main = 'https://www.beeradvocate.com/beer/styles/'
response = requests.request("GET", url_main, headers=headers, verify=False)

#Sleep for a few seconds
time.sleep(random.uniform(1,10))
soup = BeautifulSoup(response.content, 'html5lib')

for link in soup.find_all('a'):
    tail = link.get('href')
    try:
        if tail[0:13]=='/beer/styles/':
            is_style = int(tail[-2])
            style_links.append(tail)
    except:
        continue
        
for style in style_links:
#     style = style_links[0]
    print(style)
    url_style = 'https://www.beeradvocate.com'+style
    response = requests.request("GET", url_style, headers=headers, verify=False)

    #Sleep for a few seconds
    time.sleep(random.uniform(1,10))
    soup = BeautifulSoup(response.content, 'html5lib')

    count = 0

    beer_links = []
    #First Page
    i=1
    for link in soup.find_all('a'):
        tail = link.get('href')
        try:
            if tail[0:14]=='/beer/profile/' and i % 2 != 1:
                beer_link = 'https://www.beeradvocate.com'+tail
                beer_links.append(beer_link)
                count += 1
            i += 1
        except:
            continue



    # Page 2
    for link in soup.find_all('b'):
        link = str(link)
        if 'out of' in link:
            num_beers = int(link[link.find('out of')+7:link.find(')')])

    #Start page of 50 needs special treatment
    new_url = 'https://www.beeradvocate.com/beer/styles/68/?sort=revsD&start=50'

    # url_style = 'https://www.beeradvocate.com/beer/styles/68/'
    response = requests.request("GET", new_url, headers=headers, verify=False)

    #Sleep for a few seconds
    time.sleep(random.uniform(1,10))
    soup = BeautifulSoup(response.content, 'html5lib')

    j=1
    for link in soup.find_all('a'):
        tail = link.get('href')
        try:
            if tail[0:14]=='/beer/profile/':
                if j % 2 == 1:
                    beer_link = 'https://www.beeradvocate.com'+tail
                    beer_links.append(beer_link)
            j += 1
        except:
            continue
    
    #All other pages. Pages 1 and 2 required special treatment
    for i in range(100,min(num_beers,1000),50):
        new_url = 'https://www.beeradvocate.com/beer/styles/68/?sort=revsD&start=' + str(i)

        url_style = 'https://www.beeradvocate.com/beer/styles/68/'
        response = requests.request("GET", new_url, headers=headers, verify=False)

        #Sleep for a few seconds
        time.sleep(random.uniform(1,10))
        soup = BeautifulSoup(response.content, 'html5lib')

        j=1
        for link in soup.find_all('a'):
            tail = link.get('href')
            try:
                if tail[0:14]=='/beer/profile/':
                    if j % 2 != 1:
                        beer_link = 'https://www.beeradvocate.com'+tail
                        beer_links.append(beer_link)
                j += 1
            except:
                continue

    #Loop through links and download information
    meta_dict = {}
    for url in beer_links:
        response = requests.request("GET", url, headers=headers, verify=False)
        time.sleep(random.uniform(1,10))
        soup = BeautifulSoup(response.content, 'html5lib')

        #Dictionary to hold current beer information
        beer_dict = {}

        #Beer Title
        title = str(soup.find_all('h1'))
        title =  title[5:title.find('<br/>')]

        #Brewery
        for item in soup.find_all('h1'):
            item = str(item)
            brewery = item[item.find('0.75em;">')+9:item.find('</span></h1>')]

        print(f'Beer: {title}\nBrewery: {brewery}\n\n')

        beer_key = title+brewery
        beer_dict['ID'] = beer_key

        for i in range(len(soup.find_all('b'))):

            #Beer Style
            if str(soup.find_all('b')[i]) == '<b>Style:</b>':
                try:
                    beer_style = str(soup.find_all('b')[i+1])
                    beer_dict['Style'] = beer_style[3:len(style)-4]
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
            meta_dict[beer_dict['ID']] = beer_dict

    file_title = style.replace('/','_')+'.pickle'

    print(file_title)

    #Save out this style's meta dictionary
    with open(file_title,'wb') as handle:
        pickle.dump(meta_dict, handle, protocol = pickle.HIGHEST_PROTOCOL)
    
