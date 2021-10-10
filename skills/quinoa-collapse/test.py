# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


########################  PARAMETERS To TUNE ######################## 
MAX_LENGTH=1000
MIN_LENGTH=100

#*************************************INITIALIZATION***************

###Other imports
import newspaper
import requests
import random
import pathlib
import re
#import nltk
#nltk.download('punkt') #NOTE: only for the first time...

from utils import cut_extract, retrieve_google_urls, clean_text, load_data_txt


#####**********FOR TEST
with open(str(pathlib.Path(__file__).parent.absolute())+'/data/gaia_concerns.txt', 'r') as f:
    gaia_concerns=[line.rstrip('\n') for line in f]#f.readlines()
# load message
path_folder=str(pathlib.Path(__file__).parent.absolute())+'/messages/'
MSG_WONDER=load_data_txt("message_wonder.txt", path_folder=path_folder)

#####*****************************************************************************************
######*********************** SCRAPING PROCEDURES ***********************************************
######*****************************************************************************************

def parse_article(urls):
    article_downloaded = False
    MIN_LENGTH=50
    count=1
    while count<10 and (not article_downloaded):
        try:
            # choose random url from list obtained from Google
            url = urls[random.randint(0, len(urls)-1)]
            # locate website
            article = newspaper.Article(url)
            # download website
            print('Downloading ' + url)
            article.download()
            # parse .html to normal text
            article.parse()
            #get text
            content=article.text
            if len(content)>MIN_LENGTH:
                article_downloaded = True
                print("Happy scraping. Article downloaded succeeded.")
            count+=1
        except:#requests.exceptions.RequestException:
            print("Unhappy scraping.Article download failed. Trying again")
            pass
    
    # analyze text with natural language processing
    # article.nlp()
    return content

keyword="strange loop" #NOTE: Here to test, try with different keywords...


urls=["https://www.researchgate.net/post/What-is-your-opinion-about-plastic-waste", "https://www.scientificamerican.com/article/is-there-a-thing-or-a-relationship-betweenthings-at-the-bottom-of-things/"]
content=parse_article(urls)
print(content)
print("=======================================================")
print("==========step 1: Share concern=======")
print("=======================================================")
# - pick search_context picked randomly among concerns
search_context=random.choice(gaia_concerns)
# -- share what will look for online 
text=random.choice(MSG_WONDER)
text=text.replace("stuff",keyword)
text=text.replace("concern",search_context)
print(text)

print("=======================================================")
print("==========step 2: Retrieve urls from Google=======")
print("=======================================================")
# 2---- query Google and retrieve urls
query = keyword + " " + search_context 
print("Querying on the web: " + query)
urls = retrieve_google_urls(query)
# urls= alt_retrieve_google_urls(query, api_key=my_api_key, cse_id=my_cse_id) #alternative w/Google API keys...)

print("=======================================================")
print("==========step 3: Pick & Parse Some Content=======")
print("=======================================================")
# 3----  parse contents of the page
scraped_data = parse_article(urls)

print("=======================================================")
print("==========step 4: Share what found=======")
print("=======================================================")
# 4----share an extract of what found online once cleaned
final_extract= cut_extract(scraped_data, MAX_LENGTH)#TODO: issue with cut extract for now with unconventional format
final_extract = clean_text(final_extract)

print("Extract of what found online:"+ final_extract)
