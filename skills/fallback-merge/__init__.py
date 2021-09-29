# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

# =============================================
# --------------ABOUT ---------------
# ======================================
# 
# Fallback skill developped by Tropozone Collective.
# This Fallback is merging different other subskills,
# such as: Hello socket, what if we bucket, ElsewhereTunes, Enter the Weird
# 
# tbc
#
# 



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
#for gpt2
import torch
import transformers 
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from datetime import datetime, date
from datetime import timedelta
# for grammar
#from gingerit.gingerit import GingerIt
import language_tool_python

# other scrips in utils
from .utils import load_storylines, read_line, forget_one_memory, random_distortion, split_into_sentences, ending_with_punct_manual, cool_judgement_enter_the_weird, cool_judgement_what_if, load_data_txt, load_makingkin, load_objects, read_event, extract_keywords, cut_one_sentence, remove_context, ending_with_punct



# ============================================
# ------------------TODO-----------------------
# =============================================

# TODO: Grammar procedure where cut in small; Check if grammar correct resilient bigger texts ?
# TODO: What if We Bucket: Tune ML Param. Too human filter, bad token, HomeMade gpt2
# TODO: ENTER THE WEIRD: Tune ML Param. Too human filter, bad token. HomeMade gpt2
# TODO: Hello Socket : Add Object//Events
# TODO: Hello Socket: Recording Time ? Fix or ? Can make longer and cut sound?
# TODO: Hello Socket : Replace in EventsLocation and Temporalities and objects to fit Expo in Public space
#TODO: SOund distortion: Replace file by distorted version so more and mnore distorted ?
#TODO: SOUND Distortion: need integrate main script? Apply also Quinoa COllapse ?
#TODO: SOUND Distortion: More fade in and out accross time
#TODO  SOUND Distortion: Normalise sound ?  normalize(self) "normalize has no parameters, boosts level so that the loudest part of your file reaches maximum, without clipping.
#TODO: SOUND Distortion: Add more effects such as: (and the ones commented out below)
# equalizer(frequency, q=1.0, db=-3.0)  #"frequency in Hz, q or band-width (default=1.0)"
# bandpass(frequency, q=1.0)  #"frequency in Hz, q or band-width (default=1.0)"
# bandreject(frequency, q=1.0) #"frequency in Hz, q or band-width (default=1.0)"
# compand(self, attack=0.2, decay=1, soft_knee=2.0, threshold=-20, db_from=-20.0, db_to=-20.0) #"""compand takes 6 parameters: attack (seconds), decay (seconds), soft_knee (ex. 6 results  in 6:1 compression ratio), threshold (a negative value  in dB), the level below which the signal will NOT be companded  (a negative value in dB), the level above which the signal will    NOT be companded (a negative value in dB). This effect   manipulates dynamic range of the input file.
# #delay(self, gain_in=0.8, gain_out=0.5, delays=None,decays=None, parallel=False)         #"delay takes 4 parameters: input gain (max 1), output gain and then two lists, delays and decays . Each list is a pair of comma seperated values within parenthesis.
# speed(self, factor, use_semitones=False)# s"speed takes 2 parameters: factor and use-semitones (True or False).When use-semitones = False, a factor of 2 doubles the speed and raises the pitch an octave. The same result is achieved with factor = 1200 and use semitones = True.

# -------------PARAMETERS to check----------------------
# --FOR ML MODEL
my_ML_model = True  # If do have a fine-tuned model, set to True
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-merge/gpt2_model'  # path to your fine tuned model
#----Folder Collective Memory
COLLECTIVE_MEMORY_FOLDER="/home/pi/collective_memory/"#NOTE: Match path with where collective memory resides...
#"/home/pi/.mycroft/skills/Collective Memory Skill/
#---- If can Use sound with VA:
SONOR=True #NOTE: For a text-based VA, put false !

# --------------PARAMETERS to TUNE---------------------

##----For MERGE: Likelihood different skills
#0--->Hello Socket
#1----> What if we Bucket
#2----> Enter the Weird
#3----> Elsewhere Tunes
LIKELIHOOD_SKILLS=[20,10,50,20]

#----OR HELLO SOCKET
WAITING_TIME=5 

#----FOR WHAT IF WE BUCKET gpt2 param
MAX_LENGTH = 100
TEMPERATURE = 0.9
REPETITION_PENALTY = 1.4
TOP_K=70
TOP_P=0.3
SAMPLING="default"# betweem nucleus, or topk, or default sampling (not greedy)
#TODO; Max length deprecated ? 

#----FOR ENTER THE WEIRD gpt2 generation param
MAX_LENGTH_WEIRD = 120
VARIANCE_LENGTH_WEIRD = 40
TEMPERATURE_WEIRD = 0.9
VARIANCE_TEMPERATURE_WEIRD = 0.2
REPETITION_PENALTY_WEIRD = 1.4
NUM_DRIFTS_WEIRD=1
TOP_K_WEIRD=500
TOP_P_WEIRD=0.3
SAMPLING_WEIRD="topk" # between nucleus, topk, or default sampling

##FOR COLLECTIVE MEMORY
MAX_MEMORY=100

#--- FOR POST PROCESSING FILTER and for FILTER GENERATION GPT"...
#TODO Experiment with more filters, different for the generation and the post processing Do several words may be forbodden ?
SOME_QUOTE_TOKEN=["\”", "\"","\'", ",\”",",\'", "\”.", "\".","\'.", ".\”", ".\"",".\'"]
MORE_QUOTE_TOKEN=['"', "'", 'Ġ"', "'t", '."', ',"', "Ġ'", '":', '",', '?"', '".', '":"', '","', '!"', '="', ".'", "',", ",'", "'.", '{"', '")', '">', 'Ġ("', "''", '("', '\\"', '";', "?'", '":{"', '},{"', '"]', '},"', '..."', 'âĢ¦"', "Ġ''", "':", "('", '").', ':"', '.\'"', "')", "='", '"},{"', '"),', 'Ġ"/', 'Ġ"[', '"},"', ".''", 'Ġ""', "!'", '"?', ",''", 'Ġ["', '["', '"âĢĶ', '");', '":"/', '""', ',\'"', ')"', "';", '],"', '=\\"', "['", '"[', 'Ġ"$', '"(', '."[', 'âĢĶ"', "Ġ('", "-'", '.")', 'Ġ{"', 'Ġ\\"', "']", '":[', '"}', '-"', ')."', '"><', 'Ġ."', '"]=>', '"></', 'Ġ"\'', "');", '"âĢ¦', '>"', 'Ġ"#', '="#', '"},', ';"', '"...', '":["', "'/", '"/>', '"-', '?\'"', 'Ġ".', '),"', 'Ġ"-', "').", 'Ġ"...', "'-", ']."', 'Ġ"âĢ¦', "Ġ'(", '\'"', '\\":', '/"', '"\'', 'Ġ"(', '?!"', '\'."', ']"', "'?", "Ġ'/", 'Ġ"$:/', ":'", '.""', '":[{"', ")'", '"],', '=""', 'Ġ",', '.",', 'Ġ"<', "'),", '"],"', "Ġ\\'", '\\",', '":"","', '?",', "''.", 'Ġ..."', '="/', 'Ġ"%', '}"', 'Ġ"\\', '!!"', 'Ġ"""', "Ġ['", '"""', '\\">', "''''", '%"', '\',"', '"!', '!",', '.","', "','", ')",', '!?"', '"}],"', 'Ġ,"', '".[', "\\'", '?".', 'Ġ"+', "'>", 'Ġ"@', '.,"', "Ġ'[", "'';", 'Ġ"{', "Ġ'.", 'Ġ"_', "Ġ',", 'ĠâĢ¦"', '":""},{"', '":-', '!".', '"))', '!\'"', "]'", ".''.", 'âĢ¦."']
TOO_HUMAN_TOKEN=['ĠHe','He','he','Ġhe', 'He','She', 'She','ĠShe', 'ĠShe', "he", "she", "He", "She", "her", "his", "Obama","boy", "girl", "woman", "wife", "husband", "children","blog", "John", "Mary", "Peter", "servant", "God"] #TODO but remove words including he and she...
BAD_TOKEN=["http", "in this book", "in this chapter","(See", "in this section", "in this paper", "book", "chapter", "section", "New York", "in Section", "in Chapter", "Fig.", "in Fig.", "Photograph by", "in this volume", "Jew"]
FORBIDDEN_TOKEN=SOME_QUOTE_TOKEN+MORE_QUOTE_TOKEN+TOO_HUMAN_TOKEN+BAD_TOKEN

#---- For Recording (hello socket and elsewhere tunesY
DEFAULT_RECORDING_TIME=10 
MAX_RECORDING_TIME=60

TEXT_LIKELIHOOD=0.2#if collective memory has audio, likelihood get a text. 
SISTER_LIKELIHOOD=0.5#percentage of text which are sister node info


MAX_CHAR_MEMORY=280

# -------------OTHER PARAMETERS ----------------------
WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-merge/data/words/"
WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]


# =============================================
# ------------------MERGE FALLBACK---------------
# =============================================

class MergeFallback(FallbackSkill):

    def __init__(self):
        super(MergeFallback, self).__init__(name='Merge Fallback Skill')    
        self.log.info("*****INIT FALLBACK MERGE ****")
        self.SUBSKILLS=["Hello Socket", "What if we bucket", "Enter the Weird", "Elsewhere Tunes"]
        self.NUM_SUBSKILLS=len(self.SUBSKILLS)
        self.settings_what_if=dict()
        self.settings_enter_the_weird=dict()
        #self.gingerParser = GingerIt()
        self.grammarParser=language_tool_python.LanguageTool('en-US')

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

        #
        self.FORBIDDEN_TOKEN_SET=set(FORBIDDEN_TOKEN)
        self.FORBIDDEN_TOKEN_ids=self.get_bad_words_ids(FORBIDDEN_TOKEN)
        
    
    def load_messages(self):
        """
        Load Messages to speak out for transitions.
        """
        path_folder=str(pathlib.Path(__file__).parent.absolute())+'/messages/'
        self.MSG_TELL=load_data_txt("message_tell.txt", path_folder=path_folder)
        self.MSG_LISTEN=load_data_txt("message_listen.txt", path_folder=path_folder)
        self.MSG_THANKS=load_data_txt("message_thanks.txt", path_folder=path_folder)
        self.MSG_TRAVEL=load_data_txt("message_travel.txt", path_folder=path_folder)
        self.MSG_PATIENT=load_data_txt("message_patient.txt", path_folder=path_folder)
        self.MSG_RITUAL=load_data_txt("message_ritual.txt", path_folder=path_folder)
        self.MSG_SISTER_START=load_data_txt("message_sister_start.txt", path_folder=path_folder)
        

    def init_recording_settings(self):
        # TODO: Add min free diskspace (MB) ?
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
        self.whatif = load_data_txt("/data/whatif.txt", path_folder=path_folder)
        self.whatif_nokey = load_data_txt("/data/whatif_nokey.txt", path_folder=path_folder)
        self.storylines = load_storylines("/data/fabulations.txt", path_folder=path_folder)
        self.settings_what_if.setdefault("repetition_penalty", REPETITION_PENALTY)  
        self.settings_what_if.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
        self.settings_what_if.setdefault("max_length", MAX_LENGTH)
        self.settings_what_if.setdefault("top_k", TOP_K)
        self.settings_what_if.setdefault("top_p", TOP_P)
        self.settings_what_if.setdefault("sampling", SAMPLING)

    def get_bad_words_ids(self, words):
        bad_ids=[]
        for word in words:
            bad_ids.append(self.tokenizer(word, add_prefix_space=True).input_ids)
        return bad_ids

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
        self.settings_enter_the_weird.setdefault("top_p", TOP_P_WEIRD)
        self.settings_enter_the_weird.setdefault("sampling", SAMPLING_WEIRD)

        
    def init_elsewhere_tunes(self):
        self.text_likelihood=TEXT_LIKELIHOOD
        self.sister_likelihood=SISTER_LIKELIHOOD
        self.MAX_CHAR_MEMORY=MAX_CHAR_MEMORY

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
            output=self.make_kin(message)
        elif rand==1:
            self.log.info("***Redirecting to What if We Bucket***")
            self.log.info("=======================================================")
            output=self.what_if(message)
        elif rand==2:
            self.log.info("***Redirecting to Enter the Weird***")
            self.log.info("=======================================================")
            output=self.enter_the_weird(message) 
        elif rand==3:
            self.log.info("***Redirecting to Elsewhere Tunes***")
            self.log.info("=======================================================")
            output=self.elsewhere_tunes(message)
        else:
            raise NotImplementedError

        self.log.info("---Saving the data---")
        today = date.today()
        today_str = today.strftime("%d%m%Y") # dd/mm/YY
        #save output and message in text file #NOTE: here separate log file per day
        log_file=COLLECTIVE_MEMORY_FOLDER+"trace/"+today_str+".txt"
        with open(log_file, 'a+') as f:
            f.write("\n")
            f.write(utterance)
            f.write("\n")
            f.write(output)
            f.write("\n")
        self.log.info("=======================================================")
        self.log.info("---END of this INTERACTION")
        self.log.info("=======================================================")
    
        return True


    def make_kin(self, message):
        """
            Make Kin practices
        """
        
        # start message
        ritual_start=random.choice(self.MSG_RITUAL)
        self.speak(ritual_start)

        #pick object
        self.log.info("step 1---Pick Object")
        agent= random.choice(self.objects).strip("\n")
        
        #make king event score
        self.log.info("step 2---Create a Makin kin Event Score:")
        event_score = random.choice(self.eventscores)
        event=read_event(event_score, agent, self.dico)
        event=self.parse_text(event)
        #event=self.gingerParser.parse(event)['result']

        #share event
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
                time.sleep(recording_time) #NOTE: NEEDED?  #TODO: RECORD TRANSCRIPTION STILL!, as converse do
                self.log.info("***RECORDING ENDED***")
                thanks=random.choice(self.MSG_THANKS)
                self.speak(thanks)
            
        return event

       #TODO: Ending Message ? 
        

    def what_if(self, message):
        """
            What if Skill...
        """
        #---patience
        be_patient=random.choice(self.MSG_PATIENT)
        self.speak(be_patient)

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
        MAX_TRY=3

        while ((not cool) and (count<MAX_TRY)): 
            count+=1
            raw_response = self.gpt2_generation(seed, self.settings_what_if)
            #judge answer:
            cool=cool_judgement_what_if(seed, raw_response, self.FORBIDDEN_TOKEN_SET)
            if not cool:
                self.log.info("***UNCOOL answer filtered out:***"+ raw_response)
               

        # step 4 ---
        self.log.info("step 4---final output")
        response=self.parse_text(raw_response)
        #response=self.gingerParser.parse(response)['result']
        self.log.info("***COOL and filtered ***"+response)
        self.speak(response)
        self.log.info("=======================================================")
        
        return response

    def fabulate(self, critter, keyword):

        """
        Args: 
            #TODO: TEST!!, integrate what if
        """
        
        #---generate Story line by line
        story=""
        for lines in self.storylines:
            #-pick a story line 
            line=random.choices(lines.split("\n"))
            #- replace xxx , yyy and cc
            line=line.replace("xxx", critter)
            line=line.replace("yyy", keyword)
            line=line.replace("cc", str(random.randint(0,9))+str(random.randint(0,9)))
            #--read it
            bla=read_line(line, dico=self.dico)

            #---complete with gpt2  a few sentences
            #TODO: Try feed whole context? TEST!
            raw=self.gpt2_generation(bla, self.settings_what_if)
            
            #--- cut it to a sentence 
            bla=self.parse_text(raw)

            #--- add it to story
            story+=bla + "\n"
        self.log.info("Generated Story: \n"+ story)

        return story


    def gpt2_generation(self, seed, settings):
        #More parameters ? 
        #  #early_stopping=True, no_repeat_ngram_size=repetition_penalty,
        encoded_context = self.tokenizer.encode(seed, return_tensors="pt")
        #TODO: Bad Token id for generation. Works ? but quotes too?
        #different sampling:
        if settings["sampling"]=="nucleus":
            generated = self.model.generate(encoded_context,bad_words_ids=self.FORBIDDEN_TOKEN_ids, max_length = settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_p=settings["top_p"], top_k=0)
        elif settings["sampling"]=="topk":#top k sampling
            generated = self.model.generate(encoded_context,bad_words_ids=self.FORBIDDEN_TOKEN_ids, max_length = settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=settings["top_k"])
        else:#base sampling
            generated = self.model.generate(encoded_context,bad_words_ids=self.FORBIDDEN_TOKEN_ids, max_length = settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=0)
        #early_stopping=True, no_repeat_ngram_size=repetition_penalty,
        raw_response = self.tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
        return raw_response

    def one_drift(self, utterance):
        """
            One gpt-2 drift from the last blabla
        """
        BAD=False
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
        MAX_TRY=3#TODO: adjust this

        while ((not cool) and (count<MAX_TRY)): 
            count+=1
            #generate gpt2
            raw_drift = self.gpt2_generation(context, current_settings)
            #remove  human context 
            raw_drift= raw_drift.replace(utterance, "", 1)
            cool=cool_judgement_enter_the_weird(raw_drift, self.FORBIDDEN_TOKEN_SET)
            if not cool:
                self.log.info("UNCOOL{} was filtered out,".format(count)+ raw_drift)

        #TODO: Filter ot not?
        self.log.info("=======================================================") 
        self.log.info("Step 3--Share the drift")
        self.log.info("=======================================================") 
        self.speak(drift)#
        self.log.info("***COOL and filtered ***"+drift)

        return drift


    def parse_text(self, bla):
        #good ending with punctuation
        bla=ending_with_punct_manual(bla)
        #grammar check:
        #drift=self.gingerParser.parse(drift)['result']
        split=split_into_sentences(bla)
        #split=[self.gingerParser.parse(_)['result'] for _ in split]
        split=[self.grammarParser.correct(_) for _ in split]

        return " ".join(split)
   
    def enter_the_weird(self, message):
        """
            Several gpt-2 drifts from the last utterance
        """
        #---patience
        be_patient=random.choice(self.MSG_PATIENT)
        self.speak(be_patient)

        #(0) Get the human utterance
        utterance = message.data.get("utterance")
        #(1) Choose the mode and possible seed and add it
        loopCount=0
        bla=utterance
        blabla=""
        while loopCount<self.settings_enter_the_weird["num_drifts"]:
            loopCount+=1
            self.log.info("Drift n° {loopCount}")
            bla=self.one_drift(bla) #Only keep last part as context else too big? >>>
            blabla+=bla

        return blabla

    def elsewhere_tunes(self, message):
                
        #Even if sonor, small likelihood say text memory currently...
        self.log.info("=======================================================") 
        output=""
        if self.sonor and random.uniform(0, 1)<(1-self.text_likelihood):
            self.log.info("Sonor tunes")
            self.log.info("=======================================================") 
            self.sonor_tunes(message)
        elif random.uniform(0, 1)<self.sister_likelihood:
            self.log.info("Sister Node tunes")
            self.log.info("=======================================================") 
            self.sister_node_tunes(message) 
        else:
            self.log.info("Text tunes")
            self.log.info("=======================================================") 
            output=self.text_tunes(message) 
            
        
            #TODO: indicative to say it it not him?
            
        self.log.info("=======================================================") 
        #TODO: ENDING ? Ask how make you feel?
        #TODO: It can loop back into it and try to answer this memory
        return output
        

    def sonor_tunes(self, message):
        
        self.log.info("Step 1--Catch Attention")
        # step 1: catch attention ? or just as a burp
        travel=random.choice(self.MSG_TRAVEL)
        self.speak(travel)
        message_listen=random.choice(self.MSG_LISTEN) #TODO: KEEP IT or not
        self.speak(message_listen)

        self.log.info("Step 2--Pick the sound")
        # step 2: pick sound from collective memory
        sound_file_name=random.choice(os.listdir(COLLECTIVE_MEMORY_FOLDER+"sound/"))
        sound_path=COLLECTIVE_MEMORY_FOLDER+"sound/"+sound_file_name
        
        self.log.info("Step 3--Share the title")
        # step 3: catch name file and say it loud 
        #name_file=os.path.basename(sound_path).split(".")[0]
        name_file=sound_file_name.split(".")[0]#remove extension
        name_file=name_file.replace("_", " ")#replace space
        self.log.info("***Memory Burps*** "+name_file)
        self.speak(name_file)


        # step 4: Distort the sound
        output_path= COLLECTIVE_MEMORY_FOLDER+"temp.wav" #here just a temporary path
        #TODO: Max length
        random_distortion(sound_path, output_path, proba_overlay=0.8, min_gain_drop=4, max_gain_drop=8, max_length=0)

        # step 5: playback the sound
        self.log.info("Step 4--Play the sound")
        self.log.info("Playing one sound...")
        self.audio_service.play(output_path)
        

    def text_tunes(self, message):
        #TODO: Turn them into sounds>>>

        self.log.info("Step 1--Pick a memory")
        #pick random text file from the memory
        text_file_name=random.choice(os.listdir(COLLECTIVE_MEMORY_FOLDER+"text/"))
        text_path=COLLECTIVE_MEMORY_FOLDER+"text/"+text_file_name

        #little message
        travel=random.choice(self.MSG_TRAVEL)
        self.speak(travel)

        self.log.info("Step 2--Share the text")
        # step 3: say the text
        with open(text_path, 'r') as f:
            lines = f.readlines()
        memory=" ".join(lines)[:self.MAX_CHAR_MEMORY]
        memory=self.parse_text(memory)

        self.log.info(memory)
        self.speak(memory)

        return memory


    def sister_node_tunes(self, message):

        NODES=["1", "2", "3", "666"]

        #pick a node and load data
        #TODO: Shall check not same node ?
        sister_node=random.choice(NODES)
        sister_node_path=str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-merge/nodes/"+sister_node+"/"
        with open(sister_node_path+"id.json","r") as json:
            sister_node_id=json.load()
        with open(sister_node_path+"about.txt","r") as f:
            sister_node_about=f.read()
        sister_node_about.split("/n")

        #little message
        sister_start=random.choice(self.MSG_SISTER_START)
        self.speak(sister_start)

        #say something about the node
        #TODO: say more about id ? List species?
        about=""
        while len(about)<10: #to avoid emnoty
            about=random.choice(sister_node_about)
        self.speak(about)
        self.log.info(about)


        #TODO: Ask opinion?



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

    