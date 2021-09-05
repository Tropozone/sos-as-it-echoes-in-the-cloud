# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############



# ============================================
# ------------------TODO-----------------------
# =============================================

#--- NOW
# TODO: RECORD for some events
# TODO: What trigger it ? Spontaneously when movement or sound detected ? "hey, come here..."
# TODO: Replace Location and Temporalities and objects to fit Expo in Public space
# TODO: use regex for reading text file ? ore 
#https://github.com/galaxykate/tracery
#https://github.com/aparrish/pytracery

#--- LATER
# TODO: Event asking for successive interaction as conversation
# TODO: More objects?
# TODO: More events

# =============================================
# --------------INITIALIZATION---------------
# ======================================

# --------------IMPORTS----------------------
from mycroft.skills.core import FallbackSkill
import random
import pathlib
import time
from .utils import load_makingkin, load_objects, read_event

# --------PARAMETERS TO TUNE-----------------------
WAITING_TIME=5 #waiting time in seconds where will wait for human...
# -------------OTHER PARAMETERS----------------------
WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-hello-socket/data/"
WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]

# =============================================
# ------------------SKILL---------------
# =============================================

class HelloSocketFallback(FallbackSkill):

    def __init__(self):
        super(HelloSocketFallback, self).__init__(name='Hello Socket Fallback Skill')

        # load events and objects
        self.log.info("Load events and objects...")
        self.eventscores= load_makingkin()
        self.log.info("Number different Events score:"+ str(len(self.eventscores)))
        self.objects= load_objects()
        
        self.log.info("Load dictionary...")
        self.dico = {} #Dictionnary of list words
        for filename in WORDS_LISTS:
            self.dico[filename] = [line.rstrip('\n') for line in open(WORDS_PATH+filename+'.txt')]

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
     
        #TODO: here would change so may be triggered by other sound
        utterance = message.data.get("utterance")


        self.log.info("=======================================================")
        self.log.info("step 1---Extract object ")
        self.log.info("=======================================================")
        # step 1-- pick an object
        agent= random.choice(self.objects).strip("\n")

        self.log.info("=======================================================")
        self.log.info("step 2---Created a Makin kin Event Score:")
        self.log.info("=======================================================")
        # step 2--- pick a seed from file and replace if xxx by keyword
        event_score = random.choice(self.eventscores)
        event=read_event(event_score, agent, self.dico)

        self.speak(event)
        self.log.info("Event: "+ "\n" + event)
        
        self.log.info("=======================================================")
        self.log.info("step 3---Possibly record what human share")
        self.log.info("=======================================================")
        # step 3 -- If has asked the human to share something, then wait for answer and record...
        if ("tell me" in event) or ("Tell me" in event) or ("Share your thoughts with me." in event):
            #record NOW
            #TODO: Add "I am listening ?"
            print("Recording Human Answer...")
            #TODO: RECORDING

        elif ("Narrate me" in event):
            #record after a lil pause to let person to think
            print("About to record Human Answer in 5 seconds")
            time.sleep(WAITING_TIME)
            self.speak("Please share it with me now.")
            print("Recording Human Answer...")
            #TODO: RECORDING

        else:
            print("******Interaction Ended******")
        
        return True



    def shutdown(self):
        """
            Remove the skill from list of fallback skills
        """
        self.remove_fallback(self.handle_make_kin)
        super(HelloSocketFallback, self).shutdown()


##-----------------CREATE

def create_skill():
    return HelloSocketFallback()

    