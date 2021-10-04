
# =============================================
# --------------ABOUT ---------------
# ======================================
# 
# Skill developped by Tropozone Collective.
# The skill is answering certain question by picking in a dataDream of answers
# 
# May be tested by asking stuff like "..."
# 
# tbc
#
#

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

from .utils import load_data_txt

#from configparser import ConfigParser
#For alternative scraper, not needed currently
#from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper


#https://www.dreambank.net/random_sample.cgi?series=blind-f&min=50&max=300&n=100

# =============================================
# -------------- SKILL ---------------
# ======================================


class DreamSkill(MycroftSkill):
    def __init__(self):
        """ The __init__ method is called when the Skill is first constructed.
        It is often used to declare variables or perform setup actions, however
        it cannot utilise MycroftSkill methods as the class does not yet exist.
        """
        super(DreamSkill, self).__init__(name='Quinoa Collapse Skill')
        #self.learning = True 

    def initialize(self):
        """ Perform any final setup needed for the skill here.
        This function is invoked after the skill is fully constructed and
        registered with the system. Intents will be registered and Skill
        settings will be available."""
        # my_setting = self.settings.get('my_setting') #not needed yet

        self.log.info("--Importing Dreams-")#
        with open(str(pathlib.Path(__file__).parent.absolute())+'/data/blind_dreams.txt', 'r') as f:
            self.dreams=f.read()
        self.dreams=self.dreams.split("\n \n") 
        self.log.info("number of dreams loaded {}".format(len(self.dreams)))

        # load message
        path_folder=str(pathlib.Path(__file__).parent.absolute())+'/messages/'
        self.MSG_START=load_data_txt("message_start.txt", path_folder=path_folder)
        self.MSG_END=load_data_txt("message_end.txt", path_folder=path_folder)
        


    #What happen when detect like Intent. PADATIOUS: use .intent file
    @intent_handler('classic.intent')
    def handle_classic_intent(self, message):
        self.log.info("=======================================================")
        self.log.info("==========step 0: Caught Human utterance and Extract Keyword=======")
        self.log.info("=======================================================")

        #- --- beginning note
        text_start=random.choice(self.MSG_START)
        self.speak(text_start)
        self.log.info(text_start)

         #- --- share dream
        dream=random.choice(self.dreams)
        self.speak(dream)

        #- --- ending note#TODO: Ask question ?
        text_end=random.choice(self.MSG_END)
        self.speak(text_end)
        self.log.info(text_end)


        



######*****************************************************************************************
######*********************** SKILL ***********************************************
######*****************************************************************************************

    def stop(self):
        pass


def create_skill():
    return DreamSkill()

