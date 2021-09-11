# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############

# =============================================
# --------------INITIALIZATION---------------
# ======================================

# --------------IMPORTS----------------------

from mycroft.skills.core import FallbackSkill
from mycroft.skills.audioservice import AudioService
#FOR RECORDING
from mycroft.audio import wait_while_speaking
from mycroft.messagebus.message import Message
from mycroft.util import record, play_wav
from mycroft.util.parse import extract_datetime
from mycroft.util.format import nice_duration
from mycroft.util.time import now_local

import random
import pathlib
import time
import re
import os
from os.path import exists
import spacy #NOTE: Temporarily desactivate spacy for reapsberry 4
import torch
import transformers 
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from datetime import datetime
from datetime import timedelta


# for grammar
from gingerit.gingerit import GingerIt

from .utils import cool_judgement_enter_the_weird, cool_judgement_what_if, load_data_txt, load_makingkin, load_objects, read_event, extract_keywords, load_whatif, cut_one_sentence, remove_context, ending_with_punct



# ============================================
# ------------------TODO-----------------------
# =============================================

#--- CHECKS//TUNES
# TODO: ENTER THE WEIRD: Tune ML Param. Too human filter, HomeMade gpt2
# TODO: ENTER THE WEIRD: Test with different versions homemade gpt2

#--SOON:
# TODO: Hello Socket : Object//Events
# TODO: Tune Grammar & Filters for skills
# TODO: Hello Socket: Recording Time ? Fix or ? Can make longer and cut sound?
# TODO: Hello Socket : Replace in EventsLocation and Temporalities and objects to fit Expo in Public space
# TODO: Hello SOcket Event asking for successive interaction as conversation
# TODO: ENTER THE WEIRD:  different seeds ?// Use PERSONNA gpt2! 
# TODO: ENTER THE WEIRD: Manipulation audio
# TODO: Elsewhere Tunes: SHARE MORE ABOUT NODES?
# TODO: What if: Structure of a fabulation instead, query only gpt2 for words?  or use generator without ML?
# TODO: What if: More interaction with human? Ask its reaction, opintion ? and RECORD ?
# TODO: What If: Rework a lot the counterfactuals, history, etc. Add some grammar etc

# --------------PARAMETERS to TUNE---------------------

#Likelihood different skills
#0--->Hello Socket
#1----> What if we Bucket
#2----> Enter the Weird
#3----> Elsewhere Tunes
LIKELIHOOD_SKILLS=[15,20,50,15]

#FOR HELLO SOCKET
WAITING_TIME=5 

#FOR WHAT IF WE BUCKET:
MAX_LENGTH = 80
TEMPERATURE = 0.8
REPETITION_PENALTY = 1.4
TOP_K=4

#FOR ENTER THE WEIRD:
MAX_LENGTH_WEIRD = 100
VARIANCE_LENGTH_WEIRD = 20
TEMPERATURE_WEIRD = 0.8
VARIANCE_TEMPERATURE_WEIRD = 0.4
REPETITION_PENALTY_WEIRD = 1.4
NUM_DRIFTS_WEIRD=1
TOP_K_WEIRD=10

#for Recording (hello socket and elsewhere tunes)
DEFAULT_RECORDING_TIME=10 
MAX_RECORDING_TIME=60

# -------------OTHER PARAMETERS----------------------
WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-merge/data/"
WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]

# --FOR ML MODEL
my_ML_model = False  # If do have a fine-tuned model, set to True
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-merge/gpt2_model'  # path to your fine tuned model


COLLECTIVE_MEMORY_FOLDER="/home/pi/collective_memory"#NOTE: Match path with where collective memory resides...
#"/home/pi/.mycroft/skills/Collective Memory Skill/

SONOR=True #NOTE: For a text-based VA, put false !

# =============================================
# ------------------SKILL---------------
# =============================================

class MergeFallback(FallbackSkill):

    def __init__(self):
        super(MergeFallback, self).__init__(name='Merge Fallback Skill')    
        self.log.info("*****INIT FALLBACK MERGE ****")
        #Merge Fallback reroute to the following skills: hello socket, what if we bucket, ELsewhereTunes, Enter the ")
        self.SUBSKILLS=["Hello Socket", "What if we bucket", "Enter the Weird", "Elsewhere Tunes"]
        self.NUM_SUBSKILLS=len(self.SUBSKILLS)
        self.settings_what_if=dict()
        self.settings_enter_the_weird=dict()
        self.gingerParser = GingerIt()    
        self.load_messages()
        self.init_hello_socket()
        self.init_what_if_we_bucket()
        self.init_enter_the_weird()
        self.init_elsewhere_tunes()
        self.sonor=SONOR
        if self.sonor:#only if sound on:
            self.init_recording_settings()
            self.record_process = None
            self.start_time = 0
            self.last_index = 24  # index of last pixel in countdowns #WHAT IS IT FOR ???

        
    
    def load_messages(self):
        # load message
        path_folder=str(pathlib.Path(__file__).parent.absolute())+'/messages/'
        self.MSG_TELL=load_data_txt("message_tell.txt", path_folder=path_folder)
        self.MSG_LISTEN=load_data_txt("message_listen.txt", path_folder=path_folder)
        self.MSG_THANKS=load_data_txt("message_thanks.txt", path_folder=path_folder)
        

    def init_recording_settings(self):

        # min free diskspace (MB)
        self.log.info("Init Recording Settings - in fallback-merge")
        self.settings.setdefault("min_free_disk", 100)
        self.settings.setdefault("rate", 16000)  # sample rate, hertz
        self.settings.setdefault("channels", 1)  # recording channels (1 = mono)
        self.settings.setdefault("file_folder", COLLECTIVE_MEMORY_FOLDER)
        self.settings.setdefault("duration", DEFAULT_RECORDING_TIME)


    def init_hello_socket(self):
        # load events and objects
        self.log.info("Init Hello Socket - in fallback-merge")
        self.eventscores= load_makingkin()
        self.log.info("Number different Events score:"+str(len(self.eventscores)))
        self.objects= load_objects()
        self.dico = {} #Dictionnary of list words
        for filename in WORDS_LISTS:
            self.dico[filename] = [line.rstrip('\n') for line in open(WORDS_PATH+filename+'.txt')]

    def init_what_if_we_bucket(self):
        self.log.info("Init gpt2 and What if We Bucket - in fallback-merge")
        # Initialize language generation model
        if my_ML_model:
            self.log.info("Loading my own machine learning model")
            self.model = GPT2LMHeadModel.from_pretrained(my_ML_model_path)
        else:
            self.log.info("Loading generic GPT-2 model")
            self.model = GPT2LMHeadModel.from_pretrained("distilgpt2")

        # Initialise a tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
        # initialise keyworder
        self.keyworder = spacy.load("en_core_web_sm") #NOTE: temporarily desactivated for raspberry pi
        # load
        path_folder=str(pathlib.Path(__file__).parent.absolute())
        self.whatif = load_data_txt("/whatif.txt", path_folder=path_folder)
        self.whatif_nokey = load_data_txt("/whatif_nokey.txt", path_folder=path_folder)
        
        self.settings_what_if.setdefault("repetition_penalty", REPETITION_PENALTY)  
        self.settings_what_if.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
        self.settings_what_if.setdefault("max_length", MAX_LENGTH)
        self.settings_what_if.setdefault("top_k", TOP_K)

        
    def init_enter_the_weird(self):
        self.log.info("Init Enter the Void - in fallback-merge")
        # min free diskspace (MB)
        self.settings_enter_the_weird.setdefault("repetition_penalty", REPETITION_PENALTY_WEIRD)  
        self.settings_enter_the_weird.setdefault("temperature", TEMPERATURE_WEIRD)  # recording channels (1 = mono)
        self.settings_enter_the_weird.setdefault("max_length", MAX_LENGTH_WEIRD)
        self.settings_enter_the_weird.setdefault("variance_length", VARIANCE_LENGTH_WEIRD)
        self.settings_enter_the_weird.setdefault("variance_temperature", VARIANCE_TEMPERATURE_WEIRD)
        self.settings_enter_the_weird.setdefault("num_drifts", NUM_DRIFTS_WEIRD)
        self.settings_enter_the_weird.setdefault("top_k", TOP_K_WEIRD)

        
    def init_elsewhere_tunes(self):
        pass

    def initialize(self):
        """
            Registers the fallback handler.
            The second argument is the priority associated to the request;
            Because there are several fallback skills available, priority helps
            to tell Mycroft how 'sensitively' this particular skill should be triggered.
            Lower number means higher priority, however number 1-4 are bypassing other skills.
        """
        self.audio_service = AudioService(self.bus)#instantiate an AudioService object:
        self.register_fallback(self.handle_routing, 6) 

    def handle_routing(self, message):
        """
            Make Kin practices
        """
     
        utterance = message.data.get("utterance")

        self.log.info("=======================================================")
        self.log.info("step 0---Randomly redirect to other skills")
        self.log.info("=======================================================")
        
        #-------Sampling
        #NOTE: weighted random sampling so some skills mlore likely than other

        rand=random.choices(range(self.NUM_SUBSKILLS), weights=LIKELIHOOD_SKILLS, k=1)[0]


        #------Rrerouting to skill
        self.log.info("=======================================================")
        if rand==0:
            self.log.info("***Redirecting to Hello Socket***")
            self.log.info("=======================================================")
            self.make_kin(message)
        elif rand==1:
            self.log.info("***Redirecting to What if We Bucket***")
            self.log.info("=======================================================")
            self.what_if(message)
        elif rand==2:
            self.log.info("***Redirecting to Enter the Weird***")
            self.log.info("=======================================================")
            self.enter_the_weird(message) 
        elif rand==3:
            self.log.info("***Redirecting to Elsewhere Tunes***")
            self.log.info("=======================================================")
            self.elsewhere_tunes(message)
        else:
            raise NotImplementedError

        self.log.info("=======================================================")
        self.log.info("---END of this INTERACTION")
        self.log.info("=======================================================")
    
        return True


    def make_kin(self, message):
        """
            Make Kin practices
        """
        #utterance = message.data.get("utterance")
        #TODO: Starting Message ?

        self.log.info("step 1---Pick Object")
        agent= random.choice(self.objects).strip("\n")
        
        self.log.info("step 2---Create a Makin kin Event Score:")
        event_score = random.choice(self.eventscores)
        event=read_event(event_score, agent, self.dico)
        
        self.log.info("step 3---Share the Event")
        self.speak(event)
        self.log.info("Event: "+ "\n" + event)
        
        # step 3 -- If has asked the human to share something, then wait for answer and record...
        if self.sonor: 
            if ("tell me" in event) or ("Tell me" in event) or ("Share your thoughts with me." in event) or ("Narrate me" in event):
                self.log.info("=======================================================")
                self.log.info("step 4---Record what human share")
                self.log.info("=======================================================")

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
                    self.log.info("***Start Recording Human NOW ***")
                    # Initiate recording
                    self.start_time = now_local()   # recalc after speaking completes
                    self.record_process = record(recording_path,
                                                    int(recording_time),
                                                    self.settings["rate"],
                                                    self.settings["channels"])
                    #TODO: ERASE IF SILENCE?
                    self.enclosure.eyes_color(255, 0, 0)  # set color red #WHAT FOR ?
                    self.last_index = 24
                    #self.schedule_repeating_event(self.recording_feedback, None, 1,
                    #                                name='RecordingFeedback')
                else:
                    self.speak_dialog("audio.record.disk.full")
                time.sleep(recording_time) #NOTE: NEEDED? 
                self.log.info("***RECORDING ENDED***")
                thanks=random.choice(self.MSG_THANKS)
                self.speak(thanks)
            
    
       #TODO: Ending Message ? 
        

    def what_if(self, message):
        """
            What if Skill...
        """
        # step 0 --Obtain what the human said
        utterance = message.data.get("utterance")

         # step 1-- extract a keyword from what human said
        keyword= extract_keywords(utterance, self.keyworder) #NOTE: May have issue with raspberry 4 with spacy
        self.log.info("step 1---Extracted keyword"+keyword)
        self.log.info("=======================================================")

        # step 2--- pick a seed from file and replace if xxx by keyword
        if keyword=="":
            seed = random.choice(self.whatif_nokey)
        else:
            seed = random.choice(self.whatif)
            seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
        self.log.info("step 2---Seed used"+seed)
        self.log.info("=======================================================")

        # step 3--Generate with gpt2 until okay
        self.log.info("step 3---gpt2 generation until pass the filter")
        cool=False
        count=0

        while ((not cool) and (count<10)): 
            count+=1
            raw_response = self.gpt2_generation(seed, self.settings_what_if)
            #judge answer:
            cool=cool_judgement_what_if(seed, raw_response)
            if not cool:
                self.log.info("***UNCOOL answer filtered out:***"+ raw_response)
               

        # step 4 ---
        self.log.info("step 4---final output")
        #good ending for ...
        response=ending_with_punct(raw_response)
        #grammar check
        response=self.gingerParser.parse(response)['result']
        self.log.info("***COOL and filtered ***"+response)
        self.speak(response)
        self.log.info("=======================================================")
        


    def gpt2_generation(self, seed, settings):
        #More parameters ? 
        #  #early_stopping=True, no_repeat_ngram_size=repetition_penalty,

        encoded_context = self.tokenizer.encode(seed, return_tensors="pt")
        generated = self.model.generate(encoded_context, max_length = settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=settings["top_k"])
        #early_stopping=True, no_repeat_ngram_size=repetition_penalty,
        raw_response = self.tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
        return raw_response

    def one_drift(self, utterance):
        """
            One gpt-2 drift from the last blabla
        """
        too_human=False
        # step 1--- Choose the mode and possible seed and add it after the blabla
        # self.pickMoodySeed()
        # blabla=blabla+ " " + self.moodySeed
        seed="" #NOTE: Could add a seed ?
        context = utterance + seed

        self.log.info("=======================================================")
        self.log.info("Step 1--context:"+context )
        self.log.info("=======================================================") 

        
        #step 2--- ML Drift according to parameters
        self.log.info("=======================================================")
        self.log.info("Step 2--gpt2 generation until pass filter")
        current_settings=self.settings_enter_the_weird.copy()
        current_settings["max_length"]+=random.randint(-current_settings["variance_length"], current_settings["variance_length"])
        current_settings["temperature"]+=current_settings["variance_temperature"]* (2*random.random()-1)

        cool=False
        count=0

        while ((not cool) and (count<10)): 
            count+=1
            #generate gpt2
            raw_drift = self.gpt2_generation(context, current_settings)
            #remove  human context 
            raw_drift= raw_drift.replace(utterance, "", 1)
            cool=cool_judgement_enter_the_weird(seed, raw_drift)
            if not cool:
                self.log.info("UNCOOL was filtered out,"+ raw_drift)

        #TODO: Filter ot not?
        #good ending with punctuation
        drift=ending_with_punct(raw_drift)
        #grammar check: Not for here ?
        #drift=self.gingerParser.parse(drift)['result']
        
        self.log.info("=======================================================") 
        self.log.info("Step 3--Share the drift")
        self.log.info("=======================================================") 
        self.speak(drift)#
        self.log.info("***COOL and filtered ***"+drift)

        return drift
    
    def enter_the_weird(self, message):
        """
            Several gpt-2 drifts from the last utterance
        """
        #(0) Get the human utterance
        utterance = message.data.get("utterance")
        #(1) Choose the mode and possible seed and add it
        loopCount=0
        bla=utterance
        blabla=""
        while loopCount<self.settings["num_drifts"]:
            loopCount+=1
            self.log.info("Drift n° {loopCount}")
            bla=self.one_drift(bla) #Only keep last part as context else too big? >>>
            blabla+=bla

    def elsewhere_tunes(self, message):
        
    
        if self.sonor:
            # step 1: catch attention ? or just as a burp
            message=random.choice(self.MSG_LISTEN) #TODO: KEEP IT or not
            self.log.info(message)
            self.speak(message)

            # step 2: pick sound from collective memory
            sound_path=random.choice(os.listdir(COLLECTIVE_MEMORY_FOLDER))

            # step 3: playback the sound
            self.log.info("Playing one sound")
            self.audio_service.play(sound_path)
        else:
            #pick a message from the text memory
        
        
        #TODO: ENDING ? Ask how make you feel?


    def has_free_disk_space(self):
        #TODO: add free disk space later on
        return True


    def shutdown(self):
        """
            Remove the skill from list of fallback skills
        """
        self.remove_fallback(self.handle_routing)
        super(MergeFallback, self).shutdown()


##-----------------CREATE

def create_skill():
    return MergeFallback()

    