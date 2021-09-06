
from googlesearch import search
import newspaper
import nltk
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.tokenize.treebank import TreebankWordDetokenizer
import requests
from urllib.error import URLError
import random
import re


######*****************************************************************************************
######*********************** LOAD PROCEDURES ***********************************************
######*****************************************************************************************


def load_data_txt(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.readlines()
    return data

######*****************************************************************************************
######*********************** STRING PROCEDURES ***********************************************
######*****************************************************************************************

def clean_text(data):
    # Text Cleanup
    sent = nltk.sent_tokenize(data)
    #remove last sentence in case not finish
    if len(sent) > 1:
        sent.pop()
    cut = TreebankWordDetokenizer().detokenize(sent)

    #remove punctuations strange characters...
    punct = """()-[]{};:'"\<>/@#$%^&*_~"""
    stripped = ''
    for char in cut:
        if char not in punct:
            stripped += char

    return stripped

def cut_extract(extract, maximum_char):
    """
    Cut a text extract if above a certain nb character
    """
    extract=" ".join(extract.split())#remove extra white space
    bound_extract=extract[:maximum_char]
    return bound_extract
    #TODO: NEED ADD self.crop_unfinished_sentence(bound_extract) ?



######*****************************************************************************************
######*********************** SCRAPING PROCEDURES ***********************************************
######*****************************************************************************************


def retrieve_google_urls(query, num_links=8):
    # query search terms on google
    # tld: top level domain, in our case "google.com"
    # lang: search language
    # num: how many links we should obtain
    # stop: after how many links to stop (needed otherwise keeps going?!)
    # pause: if needing multiple results, put at least '2' (2s) to avoid being blocked)
    try:
        online_search = search(query, tld='com', lang='en', num=10, stop=num_links, pause=2)
    except URLError:
        pass
    website_urls = []
    for link in online_search:
        website_urls.append(link)
    return website_urls

######*****************************************************************************************
######*********************** ... PROCEDURES ***********************************************
######*****************************************************************************************


######*****************************************************************************************
######*****************************************************************************************
######*****************************************************************************************
######*********************** PROCEDURES BELOW NOT USED CURRENTLY; TEMPORARILY KEPT  ***********************************************
######*****************************************************************************************
######*****************************************************************************************
######*****************************************************************************************


    # def crop_unfinished_sentence(self, text):
    #     """
    #     Remove last unfinished bit from text. 
    #     """
    #     #TODO: better? as SELECT FROM THE RIGHT rindex s[s.rindex('-')+1:]  
    #     stuff= re.split(r'(?<=[^A-Z].[.!?]) +(?=[A-Z])', text)

    #     new_text=""
    #     for i in range(len(stuff)):
    #         if i<len(stuff)-1:
    #             new_text+= " " + stuff[i]
    #         elif len(stuff[i])>0 and (stuff[i][-1] in [".", ":", "?", "!", ";"]):#only if last character punctuation keep
    #             new_text+= " " + stuff[i]

    #     return new_text
######*****************************************************************************************
######*********************** EXTRACTING // NLP PROCEDURES ***********************************************
######*****************************************************************************************

    # def extract_keywords(self, input):
    #     # proper nouns, nouns, and adjectives
    #     pos_tag = ['PROPN', 'NOUN', 'ADJ'] 
    #     # tokenize and store input
    #     phrase = self.keyworder(input.lower())
    #     keywords = []

    #     for token in phrase:
    #         if token.pos_ in pos_tag:
    #             # and if NOT a stop word or NOT punctuation
    #             if token.text not in keyworder.Defaults.stop_words or token.text not in punctuation:
    #                 keywords.append(token.text)
    #     key_string = " ".join(keywords)

    #     return key_string



######*****************************************************************************************
######*********************** ALTERNATIVE SCRAPER  ***********************************************
######*****************************************************************************************


    # def alt_retrieve_google_urls(self, search_term, api_key, cse_id, **kwargs):
    #     """
    #         Use Google Search API to get Google results over a query
    #         Send back urls
    #     """
    #     service = build("customsearch", "v1", developerKey=api_key)
    #     res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()

    #     search_items = res.get("items")
    #     urls=[]
    #     for i, search_item in enumerate(search_items, start=1):
    #         title = search_item.get("title")
    #         link = search_item.get("link")
    #         urls.append(link)
    #     return urls
