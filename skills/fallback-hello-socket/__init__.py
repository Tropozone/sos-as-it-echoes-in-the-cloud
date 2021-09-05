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

#FOR RECORDING
from mycroft.skills.audioservice import AudioService
from mycroft.audio import wait_while_speaking
from mycroft.messagebus.message import Message
from mycroft.util import record, play_wav
from mycroft.util.parse import extract_datetime
from mycroft.util.format import nice_duration
from mycroft.util.time import now_local
import os
from os.path import exists
from datetime import datetime
from datetime import timedelta

# --------PARAMETERS TO TUNE-----------------------
WAITING_TIME=5 #waiting time in seconds where will wait for human...
# -------------OTHER PARAMETERS----------------------
WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-hello-socket/data/"
WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]


#-----------  PARAMETERS to TUNE ---------
DEFAULT_RECORDING_TIME=10 #TODO: PUT MORE AND HOW CUT FILE THEN IF LONGER ?
MAX_RECORDING_TIME=60

#----------- OTHER PARAMETERS --------
COLLECTIVE_MEMORY_FOLDER="/home/pi/collective_memory"#TODO: REPLACE IF ON A SERVER
#"/home/pi/.mycroft/skills/Collective Memory Skill/


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

        #FOR RECORDINGS
        self.record_process = None
        self.start_time = 0
        self.last_index = 24  # index of last pixel in countdowns #WHAT IS IT FOR ???
        self.init_recording_settings()

    def init_recording_settings(self):
        # min free diskspace (MB)
        self.settings.setdefault("min_free_disk", 100)
        self.settings.setdefault("rate", 16000)  # sample rate, hertz
        self.settings.setdefault("channels", 1)  # recording channels (1 = mono)
        self.settings.setdefault("file_folder", COLLECTIVE_MEMORY_FOLDER)
        self.settings.setdefault("duration", DEFAULT_RECORDING_TIME)

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
        if ("tell me" in event) or ("Tell me" in event) or ("Share your thoughts with me." in event) or ("Narrate me" in event):

            #--- Preliminary for recordings:
            recording_time, recording_id, recording_path, has_free_disk_space=self.recording_preliminary()

            if ("Narrate me" in event):
                #record after a lil pause to let person to think
                self.log.info("About to record Human Answer in 5 seconds")
                time.sleep(WAITING_TIME)
                self.speak("Please share it with me now.")
                self.log.info("Please share it with me now.")
            
            wait_while_speaking()
        
            if has_free_disk_space:
                self.log.info("***Start Recording Human ***")
                # Initiate recording
                self.start_time = now_local()   # recalc after speaking completes
                self.record_process = record(recording_path,
                                                int(recording_time),
                                                self.settings["rate"],
                                                self.settings["channels"])
                self.enclosure.eyes_color(255, 0, 0)  # set color red #WHAT FOR ?
                self.last_index = 24
                #self.schedule_repeating_event(self.recording_feedback, None, 1,
                #                                name='RecordingFeedback')
            else:
                self.speak_dialog("audio.record.disk.full")
            time.sleep(recording_time)#TODO: NEEDED? 
            self.log.info("***Recording Ended***")      
            self.speak("Thanks for sharing it with the Collective.") #TODO: Replace by messages
        

        else:
            self.log.info("******Interaction Ended******")
        
        return True

    def recording_preliminary(self):
        #--- Calculate how long to record
        self.start_time = now_local()
        # Extract time, if missing default to 30 seconds
        stop_time, _ = (
            (now_local() + timedelta(seconds=self.settings["duration"]), None)
        )
        recording_time = (stop_time -self.start_time).total_seconds()
        #-- check time betweem min and max bound                            
        if (recording_time <= 0) or (recording_time>MAX_RECORDING_TIME):
            recording_time = DEFAULT_RECORDING_TIME  # default recording duration
        #--- Recording id and path
        now = datetime.now()
        recording_id = now.strftime("%H:%M:%S") #TODO: Add id NOde in collective memory
        recording_path=COLLECTIVE_MEMORY_FOLDER+recording_id+".wav" 
        self.log.info("Recording path:"+recording_path)
       
        #---check if has free disk space# TODO: add free disk space later on
        has_free_disk_space=self.has_free_disk_space()

        recording_time=int(recording_time)
        
        return recording_time, recording_id, recording_path, has_free_disk_space

    def has_free_disk_space(self):
        #TODO: add free disk space later on
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

    