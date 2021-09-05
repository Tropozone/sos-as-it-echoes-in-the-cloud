# =============================================================================
# About
# =============================================================================


##### Will reformulate your request with a ecological concern and scrape the web.

# May be tested by asking stuff like "how to cook quinoa".
# To see the other triggers, cf vocab file.



# =============================================================================
# TODO
# =============================================================================


#--- NOW
# TODO: What happens at end ?

#--- LATER
# TODO: Other triggers.
# TODO: Say special characters ? Test filtering



# =============================================================================
# Initialisation
# =============================================================================



# --------------PARAMETERS to tune----------------------
MAX_LENGTH=1000 #TODO: here max length with special characters...So upper bound
MIN_LENGTH=100

# --------------IMPORTS----------------------

###Mycroft Imports
from adapt.intent import IntentBuilder # adapt intent parser
from mycroft import MycroftSkill, intent_handler #padatious intent parser
from mycroft.skills.audioservice import AudioService
from mycroft.audio import wait_while_speaking

###Other imports
import newspaper
import requests
import random
import pathlib
import re

from .utils import cut_extract, retrieve_google_urls, clean_text, load_data_txt

#from configparser import ConfigParser
#For alternative scraper, not needed currently
#from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper

# =============================================================================
# SKILL
# =============================================================================



class QuinoaCollapseSkill(MycroftSkill):
    def __init__(self):
        """ The __init__ method is called when the Skill is first constructed.
        It is often used to declare variables or perform setup actions, however
        it cannot utilise MycroftSkill methods as the class does not yet exist.
        """
        super(QuinoaCollapseSkill, self).__init__(name='Quinoa Collapse Skill')
        #self.learning = True 

    def initialize(self):
        """ Perform any final setup needed for the skill here.
        This function is invoked after the skill is fully constructed and
        registered with the system. Intents will be registered and Skill
        settings will be available."""
        # my_setting = self.settings.get('my_setting') #not needed yet

        self.log.info("--Importing Gaia Concerns--")#
        with open(str(pathlib.Path(__file__).parent.absolute())+'/data/gaia_concerns.txt', 'r') as f:
            self.gaia_concerns=[line.rstrip('\n') for line in f]#f.readlines()

        # load message
        path_folder=str(pathlib.Path(__file__).parent.absolute())+'/messages/'
        self.MSG_WONDER=load_data_txt("message_wonder.txt", path_folder=path_folder)
        
        # ####LOAD CONFIG PARAMETERS: only if use alternative method to scrap url but need api keys in config file
        # config = ConfigParser()
        # config.read(str(pathlib.Path(__file__).parent.absolute())+'/data/config.ini') 
        # my_api_key = config.get('auth', 'my_api_key')
        # my_cse_id = config.get('auth', 'my_cse_id')

    #What happen when detect like Intent. PADATIOUS: use .intent file
    @intent_handler('classic.intent')
    def handle_classic_intent(self, message):
        self.log.info("=======================================================")
        self.log.info("==========step 0: Caught Human utterance and Extract Keyword=======")
        self.log.info("=======================================================")
        # -- caight what human asked 
        human_said = str(message.data.get("utterance"))
        self.log.info(f'Human said {human_said}')
        # -- extract keyword
        keyword = str(message.data.get('stuff')) #catch what human was talking about
        self.log.info(f'Stuff human talking about {keyword}')
        #keyword=extract_keywords(str(human_said))  # Dont need this now, but alternatively could use it
        
        self.log.info("=======================================================")
        self.log.info("==========step 1: Share concern=======")
        self.log.info("=======================================================")
        # - pick search_context picked randomly among concerns
        search_context=random.choice(self.gaia_concerns)
        # -- share what will look for online 
        text=random.choice(self.MSG_WONDER)
        text=text.replace("stuff",keyword)
        text=text.replace("concern",search_context)
        self.speak(text)
        self.log.info(text)

        self.log.info("=======================================================")
        self.log.info("==========step 2: Retrieve urls from Google=======")
        self.log.info("=======================================================")
        # 2---- query Google and retrieve urls
        query = keyword + " " + search_context 
        self.log.info("Querying on the web: " + query)
        urls = retrieve_google_urls(query)
        # urls= alt_retrieve_google_urls(query, api_key=my_api_key, cse_id=my_cse_id) #alternative w/Google API keys...)

        self.log.info("=======================================================")
        self.log.info("==========step 3: Pick & Parse Some Content=======")
        self.log.info("=======================================================")
        # 3----  parse contents of the page
        scraped_data = self.parse_article(urls)
        self.log.info(scraped_data)

        self.log.info("=======================================================")
        self.log.info("==========step 4: Clean & Cut extract=======")
        self.log.info("=======================================================")
        # 4----clean & cut extract of what found online
        final_extract= cut_extract(scraped_data, MAX_LENGTH)#TODO: issue with cut extract for now with unconventional format
        final_extract = clean_text(final_extract)

        self.log.info("=======================================================")
        self.log.info("==========step 5: Share what found=======")
        self.log.info("=======================================================")
        #- 5--- share online extract 
        self.speak(final_extract)
        self.log.info("Extract of what found online:"+ final_extract)        

######*****************************************************************************************
######*********************** SCRAPING PROCEDURES ***********************************************
######*****************************************************************************************

    def parse_article(self, urls):
        article_downloaded = False
        count=1
        while count<20 and (not article_downloaded):
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
                    self.log.info("Happy scraping. Article downloaded succeeded.")
                count+=1
            except requests.exceptions.RequestException:
                self.log.info("Unhappy scraping.Article download failed. Trying again")
                pass
        
        # analyze text with natural language processing
        # article.nlp()
        return content



######*****************************************************************************************
######*********************** SKILL ***********************************************
######*****************************************************************************************

    def stop(self):
        pass


def create_skill():
    return QuinoaCollapseSkill()

