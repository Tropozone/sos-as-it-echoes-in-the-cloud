
#!/usr/bin/env python3 # to use in terminal
#**********************************************************************IMPORT**************************************************************************

import random
import spacy
from string import punctuation
from googlesearch import search #google library
import newspaper
import nltk
nltk.download('punkt')
import requests
from time import sleep
from urllib.error import URLError
import pathlib


# FIX for the scraper method 1 to work: (no need for method 2)
#TODO: This is a temporary insecure fix, as disable need for certificate
# Better fix: https://stackoverflow.com/questions/25981703/pip-install-fails-with-connection-error-ssl-certificate-verify-failed-certi
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#TODO: CHECK ALL FILTERS/EXTRACT AND IMPROVE. cf bottom page


# #FOR ALTERMATIVE URL SCRAPER ONLY
# from configparser import ConfigParser
# from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper

#NEEDED for alternative scraper?
# import requests
# from bs4 import BeautifulSoup #More beautiful to see html
# import urllib.parse
# import lxml
# import cssselect
# import sys
# import subprocess 


#***********************************************************************PARAMETERS INITIALIZATION***************************************************************************

####LOAD CONFIG PARAMETERS for alt_retrieve_google_urls only, not for main method
# config = ConfigParser()
# config.read(str(pathlib.Path(__file__).parent.absolute())+'/data/config.ini') 
# my_api_key = config.get('auth', 'my_api_key')
# my_cse_id = config.get('auth', 'my_cse_id')


   
######*****************************************************************************************
######*********************** SCRAPER  ***********************************************
######*****************************************************************************************

 
def retrieve_google_urls(query):
    # query search terms on google
    # tld: top level domain, in our case "google.com"
    # lang: search language
    # num: how many links we should obtain
    # stop: after how many links to stop (needed otherwise keeps going?!)
    # pause: if needing multiple results, put at least '2' (2s) to avoid being blocked)
    try:
        online_search = search(query, tld='com',
                            lang='en', num=5, stop=3, pause=2)
    except URLError:
        pass

    # extract the urls:
    urls = []
    for link in online_search:
        urls.append(link)

   
    return urls

def parse_article(urls):
    #TODO: Use random article instead first one fine?
    #TODO: Check first above certain length ?
    #TODO: May filter differently

    article_downloaded = False
    while not article_downloaded:
        try:
            # choose random url from list obtained from Google
            url = urls[random.randint(0, len(urls)-1)]
            # locate website
            article = newspaper.Article(url)
            # download website
            print('Downloading ' + url)
            article.download()
            article_downloaded = True
        except requests.exceptions.RequestException:
            print("Article download failed. Trying again")
            article_downloaded = False
            pass
    # parse .html to normal text
    article.parse()
    # analyze text with natural language processing
    article.nlp()
    # return summary
    return article.summary
    # Or return text:
    #return article.text



#**********************************************************************MAIN PROCEDURE**************************************************************************


def surf_google(query):
    """
    Main procedure to scrap google result of a query: will scrap the urls first, then the texts of the articles, parse the text and choose
    one of these extracts.

    """
    #TODO: If none result satisfying criteria (length etc), relaunch further pages? OR TAKE SMALLER TEXT
    ###(0) Scrap data from Google Search
    print("=======================================================")
    print("Scraping Google results and get urls")
    urls = retrieve_google_urls(query)
    # TODO: Check, this is an alternative urlprocedure else but need Google API key:
    #urls= alt_retrieve_google_urls(query, api_key=my_api_key, cse_id=my_cse_id)
    print(urls)

    ###(2) Extract one part
    print("=======================================================")
    print("Extracting the texts")
    extract=parse_article(urls) #extract_text(urls, min_char_bit, min_char_block)
    print(extract)

   
    return extract

###Example to run it:
surf_google("amino acids are hot")


######*****************************************************************************************
######*********************** ALTERNATIVE URL SCRAPER  ***********************************************
######*****************************************************************************************


def alt_retrieve_google_urls(self, search_term, api_key, cse_id, **kwargs):
    """
        Use Google Search API to get Google results over a query
        Send back urls
    """
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()

    search_items = res.get("items")
    urls=[]
    for i, search_item in enumerate(search_items, start=1):
        title = search_item.get("title")
        link = search_item.get("link")
        urls.append(link)
    return urls
