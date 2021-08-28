# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############

###### TODO ############
####### NOW
# TODO: More objects?
# TODO: What trigger it ? Spontaneously when movement or sound detected ? "hey, come here..."
# TODO: Some events require conversatioN!

####### MAYBE
# TODO: use regex for reading text file ? ore 
#https://github.com/galaxykate/tracery
#https://github.com/aparrish/pytracery

#********************************************INITIALIZATION***********


from mycroft.skills.core import FallbackSkill
import random
import pathlib

from .utils import load_makingkin, load_objects, read_event

from gingerit.gingerit import GingerIt
gingerParser = GingerIt()  # for grammar

#******************************************PARAMETERS ****************************


WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-hello-socket/data/"
WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]





#****************************************** SKILL ****************************


class HelloSocketFallback(FallbackSkill):

    def __init__(self):
        super(HelloSocketFallback, self).__init__(name='Hello Socket Fallback Skill')

        # load events and objects
        self.log.info("Load events and objects...")
        self.events= load_makingkin()
        self.objects= load_objects()
        
        self.log.info("Load dictionary...")
        dico = {} #Dictionnary of list words
        for filename in WORDS_LISTS:
            dico[filename] = [line.rstrip('\n') for line in open(WORDS_PATH+filename+'.txt')]

    def initialize(self):
        """
            Registers the fallback handler.
            The second argument is the priority associated to the request;
            Because there are several fallback skills available, priority helps
            to tell Mycroft how 'sensitively' this particular skill should be triggered.
            Lower number means higher priority, however number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_make_kin, 6) #NOTE: change priority of other fallback when want to test so no conflict?

    def handle_make_kin(self, message):
        """
            Make Kin practices
        """
        # step-0 Obtain what the human said
        utterance = message.data.get("utterance")#TODO: here not utterance...

        # step 1-- pick an object
        agent= random.choice(self.objects).strip("\n")
        self.log.info("=======================================================")
        self.log.info("step 1---Extracted object "+ agent)
        self.log.info("=======================================================")

        # step 2--- pick a seed from file and replace if xxx by keyword
        event_score = random.choice(self.events)
        event=read_event(event_score, agent, self.dico) #define it.
        self.log.info("=======================================================")
        self.log.info("step 2---Created a Makin kin Event Score:"+"\n"+event)
        self.log.info("=======================================================")

        # step 3 --Speak generated text aloud
        self.speak(event)

        #TODO: wait for comment about it?
        #TODO: More interactive with VA, has to record it to send to network>>>

        return True




    # Required: Skill creator must make sure the skill is removed when the Skill is shutdown by the system.
    def shutdown(self):
        """
            Remove the skill from list of fallback skills
        """
        self.remove_fallback(self.handle_make_kin)
        super(HelloSocketFallback, self).shutdown()


##-----------------CREATE

def create_skill():
    return HelloSocketFallback()

    