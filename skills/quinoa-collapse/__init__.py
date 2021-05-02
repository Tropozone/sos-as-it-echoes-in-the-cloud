########################  ABOUT THIS SKILL

##### Will reformulate your request with a ecological concern and scrape the web.

# May be tested by asking stuff like "how to cook quinoa".
# To see the other triggers, cf vocab file.
# 

# TODO: What are the things triggering it ?
# TODO: Desactivate other Mycroft skills for other intents
######################## INITIALISATION

###Mycroft Imports
from adapt.intent import IntentBuilder # adapt intent parser
from mycroft import MycroftSkill, intent_handler #padatious intent parser
from mycroft.skills.audioservice import AudioService
from mycroft.audio import wait_while_speaking
###Other imports
import spacy
from string import punctuation
from googlesearch import search
import newspaper
import nltk
import requests
from random import randint
from time import sleep
from urllib.error import URLError
import random
from configparser import ConfigParser
import pathlib
import re

#For alternative scraper, not needed currently
#from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper


class QuinoaCollapseSkill(MycroftSkill):
    def __init__(self):
        """ The __init__ method is called when the Skill is first constructed.
        It is often used to declare variables or perform setup actions, however
        it cannot utilise MycroftSkill methods as the class does not yet exist.
        """
        super().__init__()
        #self.learning = True 

    def initialize(self):
        """ Perform any final setup needed for the skill here.
        This function is invoked after the skill is fully constructed and
        registered with the system. Intents will be registered and Skill
        settings will be available."""
        # my_setting = self.settings.get('my_setting') #not needed yet

        # load machine learning model for keyword extraction
        self.log.info("--Importing ML model--")
        self.keyworder = spacy.load("en_core_web_sm")
        self.log.info("--Importing Gaia Concerns--")#
        with open(str(pathlib.Path(__file__).parent.absolute())+'/data/gaia_concerns.txt', 'r') as f:
            self.gaia_concerns=[line.rstrip('\n') for line in f]#f.readlines()

        # ####LOAD CONFIG PARAMETERS: only if use alternative method to scrap url but need api keys in config file
        # config = ConfigParser()
        # config.read(str(pathlib.Path(__file__).parent.absolute())+'/data/config.ini') 
        # my_api_key = config.get('auth', 'my_api_key')
        # my_cse_id = config.get('auth', 'my_cse_id')

    #What happen when detect like Intent. PADATIOUS: use .intent file
    @intent_handler('classic.intent')
    def handle_classic_intent(self, message):
        self.log.info("=======================================================")
        self.log.info("==========step 0: QuinoaCollapse caught Human Utterance=======")
        self.log.info("=======================================================")
        # 0-- extract what human asked 
        human_said = str(message.data.get("utterance"))
        self.log.info(f'Human said {human_said}')
        stuff = str(message.data.get('stuff')) #catch what human was talking about
        self.log.info(f'Stuff human talking about {stuff}')

        self.log.info("=======================================================")
        self.log.info("==========step 1: Extract Keywords and pick concern=======")
        self.log.info("=======================================================")
        # 1--- extract keywords from the phrase and add a search_context picked randomly among concerns
        search_context=random.choice(self.gaia_concerns)
        keyword = stuff
        #keyword=extract_keywords(str(human_said))  # Dont need this now, but alternatively could use it

        self.log.info("=======================================================")
        self.log.info("==========step 2: Retrieve urls from Google=======")
        self.log.info("=======================================================")
        # 2---- query Google and retrieve urls
        query = keyword + " " + search_context 
        self.log.info("Querying on the web: " + query)
        urls = self.retrieve_google_urls(query)
        # urls= alt_retrieve_google_urls(query, api_key=my_api_key, cse_id=my_cse_id) #alternative w/Google API keys...)

        self.log.info("=======================================================")
        self.log.info("==========step 3: Pick & Parse Some Content=======")
        self.log.info("=======================================================")
        # 3----  parse contents of the page
        content = self.parse_article(urls)
        self.log.info(content)

        self.log.info("=======================================================")
        self.log.info("==========step 4: Share what found=======")
        self.log.info("=======================================================")
        # 4----share an extract of what found online
        extract=self.cut_extract(content, maximum_char=1000)
        self.log.info("FOUND ONLINE:"+ extract)
        self.speak(extract)
        

######*****************************************************************************************
######*********************** SCRAPING PROCEDURES ***********************************************
######*****************************************************************************************

    def cut_extract(self, extract, maximum_char):
        """
        Cut a text extract if above a certain nb character
        """
        bound_extract=extract[:maximum_char]
        return  self.crop_unfinished_sentence(bound_extract)

    def crop_unfinished_sentence(self, text):
        """
        Remove last unfinished bit from text. 
        """
        #TODO: better? as SELECT FROM THE RIGHT rindex s[s.rindex('-')+1:]  
        stuff= re.split(r'(?<=[^A-Z].[.!?]) +(?=[A-Z])', text)

        new_text=""
        for i in range(len(stuff)):
            if i<len(stuff)-1:
                new_text+= " " + stuff[i]
            elif len(stuff[i])>0 and (stuff[i][-1] in [".", ":", "?", "!", ";"]):#only if last character punctuation keep
                new_text+= " " + stuff[i]

        return new_text

    def retrieve_google_urls(self,query, num_links=8):
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


    def parse_article(self,urls):
        article_downloaded = False
        MIN_LENGTH=50
        count=1
        while not article_downloaded and count<10:
            try:
                # choose random url from list obtained from Google
                url = urls[random.randint(0, len(urls)-1)]
                # locate website
                article = newspaper.Article(url)
                # download website
                self.log.info('Downloading ' + url)
                article.download()
                # parse .html to normal text
                article.parse()
                #get text
                content=article.text
                if len(content)>MIN_LENGTH:
                    article_downloaded = True
                    self.log.info("WHAT FOUND ONLINE:"+content)
                count+=1
            except requests.exceptions.RequestException:
                self.log.info("Article download failed. Trying again")
                pass
        
        # analyze text with natural language processing
        # article.nlp()
        return content

######*****************************************************************************************
######*********************** EXTRACTING // NLP PROCEDURES ***********************************************
######*****************************************************************************************

    def extract_keywords(self, input):
        # proper nouns, nouns, and adjectives
        pos_tag = ['PROPN', 'NOUN', 'ADJ'] 
        # tokenize and store input
        phrase = self.keyworder(input.lower())
        keywords = []

        for token in phrase:
            if token.pos_ in pos_tag:
                # and if NOT a stop word or NOT punctuation
                if token.text not in keyworder.Defaults.stop_words or token.text not in punctuation:
                    keywords.append(token.text)
        key_string = " ".join(keywords)

        return key_string

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



######*****************************************************************************************
######*********************** SKILL ***********************************************
######*****************************************************************************************

    def stop(self):
        pass


def create_skill():
    return QuinoaCollapseSkill()


