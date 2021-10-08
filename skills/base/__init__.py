
# =============================================
# --------------ABOUT ---------------
# ======================================
# 
# Skill developped by Tropozone Collective.
# The skill is answering certain question by picking in a database of answers
# 
# May be tested by asking stuff like "..."
# 
# tbc
#
#pip install textdistance


# ============================================
# ------------------TODO-----------------------
# =============================================



# =============================================
# --------------INITIALIZATION---------------
# ======================================

# --------------PARAMETERS to tune----------------------

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
import json

from .utils import .

#from configparser import ConfigParser
#For alternative scraper, not needed currently
#from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper

# =============================================
# -------------- SKILL ---------------
# ======================================


class BaseSkill(MycroftSkill):
    def __init__(self):
        """ The __init__ method is called when the Skill is first constructed.
        It is often used to declare variables or perform setup actions, however
        it cannot utilise MycroftSkill methods as the class does not yet exist.
        """
        super(BaseSkill, self).__init__(name='Base Skill')
        #self.learning = True 

    def initialize(self):
        """ Perform any final setup needed for the skill here.
        This function is invoked after the skill is fully constructed and
        registered with the system. Intents will be registered and Skill
        settings will be available."""
        # my_setting = self.settings.get('my_setting') #not needed yet

        self.log.info("--Importing Answers as dictionary Concerns--")#
        with open(str(pathlib.Path(__file__).parent.absolute())+'/data/base_qa.json', 'r') as json_file:
            self.base_qa=json.load(json_file)

        # load message
        path_folder=str(pathlib.Path(__file__).parent.absolute())+'/messages/'
        #self.MSG_WONDER=load_data_txt("message_wonder.txt", path_folder=path_folder)
        


    #What happen when detect like Intent. PADATIOUS: use .intent file
    @intent_handler('classic.intent')
    def handle_classic_intent(self, message):

        # -- caught what human asked 
        utterance = str(message.data.get("utterance"))
        self.log.info(f'Human said {utterance}')
        
        #---- find answer in dictionary question
        distance_=10000
        response=""
        for key in list(self.base_qa.keys()):
            distance = sum([1 for x, y in zip(utterance, key) if x.lower() != y.lower()])
            if distance<distance_:
                response=random.choice(self.base_qa[key]) #pick one of this key

        #- answer
        self.speak(response)
        self.log.info(response) 
       
        #-TODO: Ending node?
        #text_end=random.choice(self.MSG_END)
        #self.speak(text_end)
        #self.log.info(text_end)

        



######*****************************************************************************************
######*********************** SKILL ***********************************************
######*****************************************************************************************

    def stop(self):
        pass


def create_skill():
    return BaseSkill()

