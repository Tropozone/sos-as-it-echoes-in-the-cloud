
# =============================================
# --------------ABOUT ---------------
# ======================================
# 
# Skill developped by Tropozone Collective.
# The skill reformulate your request with a ecological concern,
# and scrape the web with this concern, before sharing some results with you.
# 
# May be tested by asking stuff like "how to cook quinoa".
# 
# tbc
#
#

# ============================================
# ------------------TODO-----------------------
# =============================================
# TODO: Grammar test ? vs Keep special characters?


# =============================================
# --------------INITIALIZATION---------------
# ======================================

# --------------PARAMETERS to tune----------------------
MAX_LENGTH=400
MIN_LENGTH=160
WAIT_TIME=2

# --------------IMPORTS----------------------

###Mycroft Imports
from adapt.intent import IntentBuilder # adapt intent parser
from mycroft import MycroftSkill, intent_handler #padatious intent parser
from mycroft.skills.audioservice import AudioService
from mycroft.audio import wait_while_speaking
from datetime import datetime, date

###Other imports
import newspaper
import requests
import random
import pathlib
import re
import time
import yake
#import spacy

from .utils import yake_extract_keyword, extract_keywords, ending_with_punct_manual, cut_extract, retrieve_google_urls, clean_text, load_data_txt

#from configparser import ConfigParser
#For alternative scraper, not needed currently
#from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper
COLLECTIVE_MEMORY_FOLDER="/root/sos-as-it-echoes-in-the-cloud/collective_memory/"#NOTE: Match path with where collective memory resides...

# =============================================
# -------------- SKILL ---------------
# ======================================


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
        self.MSG_END=load_data_txt("message_end.txt", path_folder=path_folder)
        numOfKeywords = 3
        self.keyworder=yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=numOfKeywords, features=None)

        #self.keyworder = spacy.load("en_core_web_sm") #NOTE: temporarily desactivated for raspberry pi


    #What happen when detect like Intent. PADATIOUS: use .intent file
    @intent_handler('classic.intent')
    def handle_classic_intent(self, message):
        self.log.info("=======================================================")
        self.log.info("==========step 0: Caught Human utterance and Extract Keyword=======")
        self.log.info("=======================================================")
        # -- caught what human asked 
        utterance = str(message.data.get("utterance"))
        self.log.info(f'Human said {utterance}')
        # -- extract keyword
        stuff = str(message.data.get('stuff')) #catch what human was talking about
        stuff=stuff.lstrip().rstrip()
        num_words=len(stuff.split(" "))
        keyword=stuff
        if num_words>2: 
            #extract sub keyword from stuff
            keyword= yake_extract_keyword(utterance, self.keyworder) #NOTE: May have issue with raspberry 4 with spacy?
        if keyword=="":
            keyword=stuff
        self.log.info("step 1---Extracted keyword"+keyword)
        self.log.info(f'Stuff human talking about {keyword}')

        self.log.info("=======================================================")
        self.log.info("==========step 1: Share concern=======")
        self.log.info("=======================================================")
        # - pick search_context picked randomly among concerns
        search_context=random.choice(self.gaia_concerns)
        # -- share what will look for online 
        init_text=random.choice(self.MSG_WONDER)
        init_text=init_text.replace("stuff",keyword)
        init_text=init_text.replace("concern",search_context)
        self.speak(init_text)
        self.log.info(init_text)

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
        if len(scraped_data)>MAX_LENGTH:
            scraped_data=scraped_data[:MAX_LENGTH]
        final_extract= ending_with_punct_manual(scraped_data)
        #cut_extract(scraped_data, MAX_LENGTH)
        #final_extract = clean_text(final_extract)

        self.log.info("=======================================================")
        self.log.info("==========step 5: Share what found=======")
        self.log.info("=======================================================")
        #- 5--- share online extract 
        self.speak(final_extract)
        self.log.info("Extract of what found online:"+ final_extract) 
        time.sleep(WAIT_TIME)

        self.log.info("=======================================================")
        self.log.info("==========step 6: Ending note =======")
        self.log.info("=======================================================")
        #- 5--- share online extract 
        text_end=random.choice(self.MSG_END)
        self.speak(text_end)
        self.log.info(text_end)

        self.log.info("---Saving the data---")
        output=init_text+ final_extract+text_end
        today = date.today()
        today_str = today.strftime("%d%m%Y") # dd/mm/YY
        #save output and message in text file #NOTE: here separate log file per day
        log_file=COLLECTIVE_MEMORY_FOLDER+"logs/"+today_str+".txt"
        with open(log_file, 'a+') as f:
            f.write("\n")
            f.write(utterance)
            f.write("\n")
            f.write(output)
            f.write("\n")
        

######*****************************************************************************************
######*********************** SCRAPING PROCEDURES ***********************************************
######*****************************************************************************************

    def parse_article(self, urls):
        article_downloaded = False
        count=1
        while count<20 and (not article_downloaded):
            # choose random url from list obtained from Google
            url = urls[random.randint(0, len(urls)-1)]
            try:
                # locate website
                article = newspaper.Article(url)
                # download website
                self.log.info('Downloading ' + url)
                article.download()
                # parse .html to normal text
                article.parse()
                #get text
                content=article.text
                if len(content)>MIN_LENGTH and not ("JavaScript" in content):#NOTE: because of error "JavaScript is not available..."
                    article_downloaded = True
                    self.log.info("Happy scraping. Article downloaded succeeded.")
                count+=1
            except:#requests.exceptions.RequestException:#TODO:Better catch name exception or not ?
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

