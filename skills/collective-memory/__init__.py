########################  ABOUT THIS SKILL




# =============================================
# --------------TODO---------------
# ======================================

#--- NOW
# TODO: Test it

#--- LATER
# TODO: Other functionality? Play back?

# and small TODO in text

# =============================================
# --------------INITIALIZATION---------------
# ======================================

# -------------IMPORTS---------------
from adapt.intent import IntentBuilder # adapt intent parser
from mycroft import MycroftSkill, intent_handler #padatious intent parser
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
import random
import pathlib

#from configparser import ConfigParser
#For alternative scraper, not needed currently
#from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper

#-----------  PARAMETERS to TUNE ---------
DEFAULT_RECORDING_TIME=10
MAX_RECORDING_TIME=60

#----------- OTHER PARAMETERS --------
RECORDING_FOLDER="./outputs/"#.wav #TODO: Has to record in other folder...

# =============================================
# --------------SKILL---------------
# ======================================

class CollectiveMemorySkill(MycroftSkill):
    def __init__(self):
        """ The __init__ method is called when the Skill is first constructed.
        It is often used to declare variables or perform setup actions, however
        it cannot utilise MycroftSkill methods as the class does not yet exist.
        """
        super(CollectiveMemorySkill, self).__init__(name='Collective Memory Skill')
        #self.learning = True 

        self.play_process = None
        self.record_process = None
        self.start_time = 0
        self.last_index = 24  # index of last pixel in countdowns #WHAT IS IT FOR ???

        self.init_settings()

    def init_settings(self):
        # min free diskspace (MB)
        self.settings.setdefault("min_free_disk", 100)
        self.settings.setdefault("rate", 16000)  # sample rate, hertz
        self.settings.setdefault("channels", 1)  # recording channels (1 = mono)
        self.settings.setdefault("file_folder", RECORDING_FOLDER)
        self.settings.setdefault("duration", DEFAULT_RECORDING_TIME)

    def initialize(self):
        """ Perform any final setup needed for the skill here.
        This function is invoked after the skill is fully constructed and
        registered with the system. Intents will be registered and Skill
        settings will be available."""
        # my_setting = self.settings.get('my_setting') #not needed yet

        self.init_settings()


    #What happen when detect like Intent. PADATIOUS: use .intent file
    @intent_handler('share.intent')
    def handle_share_intent(self, message):
        #TODO: CHECK FURTHER  how record etc if memory disk full etc
        #https://github.com/MycroftAI/skill-audio-record/blob/21.02/__init__.py
        #TODO: CAN RECORD until silence? but max time?
        self.log.info("=======================================================")
        self.log.info("=========SKILL COLLECTIVE MEMORY TRIGGERED=======")
        utterance = message.data.get('utterance')
        self.log.info(f'Human said {str(utterance)}')

        self.log.info("=======================================================")
        self.log.info("=========step 0: Preliminary=======")
        self.log.info("=======================================================")
        #--- Calculate how long to record
        self.start_time = now_local()
        #TODO: may say time in human mesage !
        # Extract time, if missing default to 30 seconds
        stop_time, _ = (
            extract_datetime(utterance, lang=self.lang) or
            (now_local() + timedelta(seconds=self.settings["duration"]), None)
        )
        recording_time = (stop_time -
                                     self.start_time).total_seconds()
        #-- check time betweem min and max bound                            
        if recording_time <= 0:
            recording_time = DEFAULT_RECORDING_TIME  # default recording duration
        elif recording_time>MAX_RECORDING_TIME:
            recording_time=MAX_RECORDING_TIME
        
        #--- Recording id and path
        now = datetime.now()
        recording_id = now.strftime("%H:%M:%S") #TODO: Add id NOde in collective memory
        recording_path=self.settings["file_folder"]+recording_id+".wav" 
       
        #---check if has free disk space#TODO: add free disk space later on
        has_free_disk_space=True#self.has_free_disk_space():

        self.log.info("=======================================================")
        self.log.info("==========step 1: Start Recording=======")
        self.log.info("=======================================================")
        self.speak("Tell me, we are curious about it.") #TODO: Replace by messages ? We or they ?
        

        if self.has_free_disk_space():#TODO: add free disk space later on
            record_for = nice_duration(int(recording_time),
                                        lang=self.lang)
            self.speak_dialog('audio.record.start.duration',
                                {'duration': record_for})

            # Initiate recording
            wait_while_speaking()
            self.start_time = now_local()   # recalc after speaking completes
            self.record_process = record(recording_path,
                                            int(recording_time),
                                            self.settings["rate"],
                                            self.settings["channels"])
            self.enclosure.eyes_color(255, 0, 0)  # set color red #WHAT FOR ?
            self.last_index = 24
            self.schedule_repeating_event(self.recording_feedback, None, 1,
                                            name='RecordingFeedback')
        else:
            self.speak_dialog("audio.record.disk.full")


        self.log.info("=======================================================")
        self.log.info("==========step 2: End Recording=======")
        self.log.info("=======================================================")
      
        self.speak("Thanks for sharing it to the Collective Memory.") #TODO: Replace by messages
       



    # def save_recording(self, filename, recording, mode="w"):
    #     try:
    #         file_system = FileSystemAccess(str(self.skill_id))
    #         file = file_system.open(filename, mode)
    #         file.write(data)
    #         file.close()
    #         return True
    #     except Exception:#as e
    #         self.log.info("ERROR: could not save skill file " + filename)
    #         #LOG.error(e)
    #         return False

######*****************************************************************************************
######*********************** SKILL ***********************************************
######*****************************************************************************************

    def stop(self):
        pass


def create_skill():
    return CollectiveMemorySkill()




        # Throw away any previous recording
        #try:
        #    os.remove(self.settings["file_path"])
        #except Exception:
        #    pass
