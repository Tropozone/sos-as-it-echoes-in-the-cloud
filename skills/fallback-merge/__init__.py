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
os.environ["TOKENIZERS_PARALLELISM"] = "false" # Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false) hugging face...
from os.path import exists
from datetime import datetime, date
from datetime import timedelta

#for gpt2
import torch
import transformers 
from transformers import GPT2Tokenizer, GPT2LMHeadModel, AutoModelForCausalLM, AutoTokenizer

#######  #TODO: KEYWORDER CHOICE: https://towardsdatascience.com/keyword-extraction-process-in-python-with-natural-language-processing-nlp-d769a9069d5c
import yake #https://github.com/LIAAD/yake
#import spacy #NOTE: Temporarily desactivate spacy for reapsberry 4 #NOTE: USE NOW YAKE
#cf doing python3 -m spacy download en_core_web_sm

#### #TODO: GRAMMAR CHECK CHOICE ?
#from gingerit.gingerit import GingerIt
import language_tool_python

# other scrips in utils
from .utils import load_storylines, yake_extract_keyword, read_line, forget_one_memory, split_into_sentences, ending_with_punct_manual, cool_judge, load_data_txt, load_making_kin, read_event, extract_keywords, cut_one_sentence, remove_context, ending_with_punct

#DISACTIVATE TEMPORARILY
#from .sound import random_distortion

# ============================================
# ------------------TODO-----------------------
# =============================================

#TODO: Tune Filters ...Tune ML generation for Enter the Weird, Fabulate, What if we Bucket? max_new_tokens instead of max_length when feed context !
#https://huggingface.co/transformers/main_classes/model.html?highlight=generate

#TODO: ERASE sound IF SILENCE in collective Memory?
#TODO: Hello Socket: Recording Time ? Fixed  ? Can make longer and cut sound?
#TODO: SOUND Distortion: Add more effects such as: (and the ones commented out below)
# equalizer(frequency, q=1.0, db=-3.0)  #"frequency in Hz, q or band-width (default=1.0)"
# bandpass(frequency, q=1.0)  #"frequency in Hz, q or band-width (default=1.0)"
# bandreject(frequency, q=1.0) #"frequency in Hz, q or band-width (default=1.0)"
# compand(self, attack=0.2, decay=1, soft_knee=2.0, threshold=-20, db_from=-20.0, db_to=-20.0) #"""compand takes 6 parameters: attack (seconds), decay (seconds), soft_knee (ex. 6 results  in 6:1 compression ratio), threshold (a negative value  in dB), the level below which the signal will NOT be companded  (a negative value in dB), the level above which the signal will    NOT be companded (a negative value in dB). This effect   manipulates dynamic range of the input file.
# #delay(self, gain_in=0.8, gain_out=0.5, delays=None,decays=None, parallel=False)         #"delay takes 4 parameters: input gain (max 1), output gain and then two lists, delays and decays . Each list is a pair of comma seperated values within parenthesis.
# speed(self, factor, use_semitones=False)# s"speed takes 2 parameters: factor and use-semitones (True or False).When use-semitones = False, a factor of 2 doubles the speed and raises the pitch an octave. The same result is achieved with factor = 1200 and use semitones = True.


#####LATER ?
#TODO  SOUND Distortion: Normalise sound ?  normalize(self) "normalize has no parameters, boosts level so that the loudest part of your file reaches maximum, without clipping.
#TODO: SOUND Distortion: More fade in and out accross time
#TODO: Sound distortion: Replace file by distorted version in memory so more and mnore distorted ?
#TODO Experiment with more filters, different for the generation and the post processing Do several words may be forbodden ?
# TODO: What / When save collective memory

# -------------GENERAL PARAMETERS to check----------------------
# --FOR ML MODEL
my_ML_model = True  # If do have a fine-tuned model, set to True
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-merge/gpt2_model'  # path to your fine tuned model
#----Folder Collective Memory
COLLECTIVE_MEMORY_FOLDER="/root/sos-as-it-echoes-in-the-cloud/collective_memory/"#NOTE: Match path with where collective memory resides...
#"/home/pi/.mycroft/skills/Collective Memory Skill/
#---- If can Use sound with VA:
SONOR=False #NOTE: For a text-based VA, put false !


DDW=True #for DDW exhibit, adjust event / objects
# --------------PARAMETERS to TUNE---------------------

##----For MERGE: Likelihood different skills
#0---> Hello Socket
#1----> What if we Bucket
#2----> Enter the Weird
#3----> Elsewhere Tunes
#4----> Fabulate
#5----> Wonder
LIKELIHOOD_SKILLS=[10,15,35,10,15,15]

MINIMAL_LENGTH_UTTERANCE_TO_BOTHER=9

#----HELLO SOCKET PARAMETERS
WAIT_FOR_HUMAN=5 

#----FOR WHAT IF WE BUCKET PARAMETERS
MIN_LENGTH = 10
MAX_LENGTH = 80
MAX_LENGTH_FABULATE = 40 #here is per bit...
VARIANCE_FABULATE = 10 #here is per bit...
TEMPERATURE = 0.9
REPETITION_PENALTY = 1.4
TOP_K=70
TOP_P=0.3
SAMPLING="default"# betweem nucleus, or topk, or default sampling (not greedy)

#----ENTER THE WEIRD PARAMETERS
MIN_LENGTH_WEIRD = 24
MAX_LENGTH_WEIRD = 100
VARIANCE_LENGTH_WEIRD = 50
TEMPERATURE_WEIRD = 0.9
VARIANCE_TEMPERATURE_WEIRD = 0.2
REPETITION_PENALTY_WEIRD = 1.4
NUM_DRIFTS_WEIRD=1
TOP_K_WEIRD=500
TOP_P_WEIRD=0.3
SAMPLING_WEIRD="topk" # between nucleus, topk, or default sampling
MAX_TRY_REGENERATE=3 #OK?
FEEDBACK_PROBA_WEIRD=0.1

#-------- POST PROCESSING FILTER PARAMETERS
SOME_QUOTE_TOKEN=["\”", "\"","\'", ",\”",",\'", "\”.", "\".","\'.", ".\”", ".\"",".\'"]
MORE_QUOTE_TOKEN=['"', "'", 'Ġ"', "'t", '."', ',"', "Ġ'", '":', '",', '?"', '".', '":"', '","', '!"', '="', ".'", "',", ",'", "'.", '{"', '")', '">', 'Ġ("', "''", '("', '\\"', '";', "?'", '":{"', '},{"', '"]', '},"', '..."', 'âĢ¦"', "Ġ''", "':", "('", '").', ':"', '.\'"', "')", "='", '"},{"', '"),', 'Ġ"/', 'Ġ"[', '"},"', ".''", 'Ġ""', "!'", '"?', ",''", 'Ġ["', '["', '"âĢĶ', '");', '":"/', '""', ',\'"', ')"', "';", '],"', '=\\"', "['", '"[', 'Ġ"$', '"(', '."[', 'âĢĶ"', "Ġ('", "-'", '.")', 'Ġ{"', 'Ġ\\"', "']", '":[', '"}', '-"', ')."', '"><', 'Ġ."', '"]=>', '"></', 'Ġ"\'', "');", '"âĢ¦', '>"', 'Ġ"#', '="#', '"},', ';"', '"...', '":["', "'/", '"/>', '"-', '?\'"', 'Ġ".', '),"', 'Ġ"-', "').", 'Ġ"...', "'-", ']."', 'Ġ"âĢ¦', "Ġ'(", '\'"', '\\":', '/"', '"\'', 'Ġ"(', '?!"', '\'."', ']"', "'?", "Ġ'/", 'Ġ"$:/', ":'", '.""', '":[{"', ")'", '"],', '=""', 'Ġ",', '.",', 'Ġ"<', "'),", '"],"', "Ġ\\'", '\\",', '":"","', '?",', "''.", 'Ġ..."', '="/', 'Ġ"%', '}"', 'Ġ"\\', '!!"', 'Ġ"""', "Ġ['", '"""', '\\">', "''''", '%"', '\',"', '"!', '!",', '.","', "','", ')",', '!?"', '"}],"', 'Ġ,"', '".[', "\\'", '?".', 'Ġ"+', "'>", 'Ġ"@', '.,"', "Ġ'[", "'';", 'Ġ"{', "Ġ'.", 'Ġ"_', "Ġ',", 'ĠâĢ¦"', '":""},{"', '":-', '!".', '"))', '!\'"', "]'", ".''.", 'âĢ¦."']
TOO_HUMAN_TOKEN=['ĠHe','He','he','Ġhe', 'He','She', 'She','ĠShe', 'ĠShe', "he", "she", "He", "She", "her", "his", "Obama","boy", "girl", "woman", "wife", "husband", "children","blog", "John", "Mary", "Peter", "servant", "soldier", "counsin", "aunt", "uncle","Sharia", "Coran", "nephew", "war", "God", "muslim", "christian"]
BAD_TOKEN=["http", "in this book", "in this chapter","(See", "in this section", "in this paper", "book", "chapter", "section", "New York", "in Section", "in Chapter", "Fig.", "in Fig.", "Photograph by", "in this volume", "Jew", "Jews", "stupid", "page", "on page"]
FORBIDDEN_TOKEN=SOME_QUOTE_TOKEN+MORE_QUOTE_TOKEN+TOO_HUMAN_TOKEN+BAD_TOKEN
UNCOOL_WORDS=["She", "he", "she", "He", "his", "Obama","boy", "girl", "woman", "wife", "husband", "children","blog", "John", "Mary", "Peter", "servant", "soldier", "war", "God", "book", "chapter", "section", "Section", "Chapter", "Fig.", "in Fig.", "Jew", "muslim", "christian", "Sharia", "Coran", "19", "(19", "20", "(20"]
UNCOOL_WORDS_SET=set(UNCOOL_WORDS)
UNCOOL_STRING=["\”", "\"","\'", "A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "J.", "K.", "L.", "M.", "N.", "Q.", "R.", "S.", "T.", "U.", "V.", "W.", "X", "Fig.", "in Fig.", "Photograph by", "http"]
#-----------------------------
##--------- RECORDING PARAMETERS (hello socket and elsewhere tunesY
DEFAULT_RECORDING_TIME=10 #in seconds
MAX_PLAY_SOUND=20000#in ms for pydub
MAX_CHAR_MEMORY=300
MAX_RECORDING_TIME=15

##--------- ELSEWHERE TUNES PARAMETERS
SOUND_LIKELIHOOD=0.0#if collective memory has audio, likelihood get a text. 
SISTER_LIKELIHOOD=0.0#percentage of text which are sister node info

##--------- CHAT PARAMETERS
MAX_TOKEN_HISTORICS=50
CHAT_TEMPERATURE=2.0 #https://huggingface.co/transformers/main_classes/model.html
CHAT_TOPK=50
CHAT_MAX_LENGTH=40
CHAT_MIN_LENGTH=10
SAMPLING_CHAT="topk"

#----------------COLLECTIVE MEMORY PARAMETERS
MAX_MEMORY=100
global LOG_FULL
LOG_FULL=False
MIN_CHAR_MEMORY=22

#----------------WAITING TIME BETWEEN SENDING 2 utterance to server
WAIT_TIME_SHORT=1
WAIT_TIME_MEDIUM=2
WAIT_TIME_LONG=3

# ----------------------------------
# ------------- FIXED  PARAMETERS ----------------------
WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-merge/data/words/"
WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "PR0", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]


FEEDBACK_PROBA_WONDER=0.5


#TODO: yadda yadda yadda
# =============================================
# ------------------MERGE FALLBACK---------------
# =============================================

class MergeFallback(FallbackSkill):

    def __init__(self):
        super(MergeFallback, self).__init__(name='Merge Fallback Skill')    
        self.log.info("*****INIT FALLBACK MERGE ****")
        self.SUBSKILLS=["Hello Socket", "What if we bucket", "Enter the Weird", "Elsewhere Tunes", "Fabulate", "Wonder"]
        self.NUM_SUBSKILLS=len(self.SUBSKILLS)
        self.log.info("Init MERGE FALL BACK with {} subskills".format(self.NUM_SUBSKILLS)+ ",".join(self.SUBSKILLS))
        self.settings_what_if=dict()
        self.settings_enter_the_weird=dict()
        #self.gingerParser = GingerIt()
        self.grammarParser=language_tool_python.LanguageTool('en-US')

        self.fresh_historics=""

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

        #for simple dialog >
        self.dialoTokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.dialoGPT = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

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
        self.MSG_ELSEWHERE_START=load_data_txt("message_elsewhere_start.txt", path_folder=path_folder)
        self.MSG_ELSEWHERE_END=load_data_txt("message_elsewhere_end.txt", path_folder=path_folder)
        self.MSG_PATIENT=load_data_txt("message_patient.txt", path_folder=path_folder)
        self.MSG_RITUAL_START=load_data_txt("message_ritual_start.txt", path_folder=path_folder)
        self.MSG_RITUAL_END=load_data_txt("message_ritual_end.txt", path_folder=path_folder)
        self.MSG_SISTER_START=load_data_txt("message_sister_start.txt", path_folder=path_folder)
        self.MSG_INTERESTING=load_data_txt("message_interesting.txt", path_folder=path_folder)
        self.MSG_FEEDBACK=load_data_txt("message_feedback.txt", path_folder=path_folder)#NOTE: Not used ?
        self.MSG_WHAT_IF_END=load_data_txt("message_what_if_end.txt", path_folder=path_folder)
        self.MSG_FABULATE_END=load_data_txt("message_fabulate_end.txt", path_folder=path_folder)
        self.MSG_WONDER_START=load_data_txt("message_wonder_start.txt", path_folder=path_folder)
        self.MSG_WONDER_END=load_data_txt("message_wonder_end.txt", path_folder=path_folder)


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
        path_folder=str(pathlib.Path(__file__).parent.absolute())
        if DDW:
            self.eventscores= load_making_kin("/data/yoko_DDW.txt", path_folder=path_folder)
            self.objects= load_data_txt("/data/objects_DDW.txt", path_folder=path_folder)
        else:
            self.eventscores= load_making_kin("/data/yoko.txt", path_folder=path_folder)
            self.objects= load_data_txt("/data/objects.txt", path_folder=path_folder)
        self.log.info("Loaded {} event score and {} objects".format(len(self.eventscores), len(self.objects)))

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
        # initialise keyworder  #TODO: Check deduplication_threshold = 0.9... numOfKeywords
        numOfKeywords = 3
        self.keyworder=yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=numOfKeywords, features=None)
        #self.keyworder = spacy.load("en_core_web_sm") #NOTE: temporarily desactivated for raspberry pi
        # load
        path_folder=str(pathlib.Path(__file__).parent.absolute())
        self.critters = load_data_txt("/data/critters.txt", path_folder=path_folder)
        self.wonders = load_data_txt("/data/wonders.txt", path_folder=path_folder)
        self.whatif = load_data_txt("/data/whatif.txt", path_folder=path_folder)
        self.whatif_nokey = load_data_txt("/data/whatif_nokey.txt", path_folder=path_folder)
        self.storylines = load_storylines("/data/fabulations.txt", path_folder=path_folder)
        self.settings_what_if.setdefault("repetition_penalty", REPETITION_PENALTY)  
        self.settings_what_if.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
        self.settings_what_if.setdefault("max_length", MAX_LENGTH)
        self.settings_what_if.setdefault("min_length", MIN_LENGTH)
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
        self.settings_enter_the_weird.setdefault("min_length", MIN_LENGTH_WEIRD)
        self.settings_enter_the_weird.setdefault("variance_length", VARIANCE_LENGTH_WEIRD)
        self.settings_enter_the_weird.setdefault("variance_temperature", VARIANCE_TEMPERATURE_WEIRD)
        self.settings_enter_the_weird.setdefault("num_drifts", NUM_DRIFTS_WEIRD)
        self.settings_enter_the_weird.setdefault("top_k", TOP_K_WEIRD)
        self.settings_enter_the_weird.setdefault("top_p", TOP_P_WEIRD)
        self.settings_enter_the_weird.setdefault("sampling", SAMPLING_WEIRD)

        
    def init_elsewhere_tunes(self):
        self.sound_likelihood=SOUND_LIKELIHOOD
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
        recording_id = now.strftime("%H%M%S") #TODO: Add id NOde in collective memory ?
        recording_path=COLLECTIVE_MEMORY_FOLDER+"sound/"+recording_id+".wav" 
        self.log.info("Recording path:"+recording_path)
       
        #---check if has free disk space
        has_free_disk_space=self.has_free_disk_space()

        #----also check if memory has maximum recording number, else erase
        memory_paths=os.listdir(COLLECTIVE_MEMORY_FOLDER+"sound/")#
        while len(memory_paths)>=MAX_MEMORY:
            forget_one_memory(COLLECTIVE_MEMORY_FOLDER)
            memory_paths=os.listdir(COLLECTIVE_MEMORY_FOLDER+"sound/")#


        recording_time=int(recording_time)
        return recording_time, recording_id, recording_path, has_free_disk_space

    def handle_routing(self, message):
        """
            Make Kin practices
        """
     
        utterance = str(message.data.get("utterance"))
        length_utterance=len(utterance)

        self.log.info("=======================================================")
        self.log.info("step 0---Randomly redirect to other skills")
        self.log.info("=======================================================")
        
        #-------Sampling
        #weighted random sampling so some skills mlore likely than other
        rand=random.choices(range(self.NUM_SUBSKILLS), weights=LIKELIHOOD_SKILLS, k=1)[0]

        #----Chat depending which skill would be triggered, and depending length sentence
        chat_output=""
        output=""

        shortcut=(length_utterance<=MINIMAL_LENGTH_UTTERANCE_TO_BOTHER) and (not utterance.lower().rstrip()=="hello")

        if (rand in [0,3,4, 5]) or shortcut:
            self.log.info("=======================================================")
            self.log.info("step 1-First small Chatbot interaction")
            self.log.info("=======================================================")
            chat_output=self.chat(utterance, historics=self.fresh_historics)#TODO: historics historics_id=None
            time.sleep(WAIT_TIME_MEDIUM)

        if shortcut:
            #------Rrerouting to skill
            self.log.info("=======================================================")
            if rand==0:
                self.log.info("***Redirecting to Hello Socket***")
                self.log.info("=======================================================")
                output=self.make_kin()
            elif rand==1:
                self.log.info("***Redirecting to What if We Bucket***")
                self.log.info("=======================================================")
                output=self.what_if(utterance)
            elif rand==2:
                self.log.info("***Redirecting to Enter the Weird***")
                self.log.info("=======================================================")
                output=self.enter_the_weird(utterance, historics=self.fresh_historics) 
            elif rand==3:
                self.log.info("***Redirecting to Elsewhere Tunes***")
                self.log.info("=======================================================")
                output=self.elsewhere_tunes()
            elif rand==4:
                self.log.info("***Redirecting to Fabulates***")
                self.log.info("=======================================================")
                output=self.fabulate()
            elif rand==5:
                self.log.info("***Redirecting to Wonder***")
                self.log.info("=======================================================")
                output=self.wonder()

            else:
                raise NotImplementedError

        self.log.info("---Saving the data---")
        
        today = date.today()
        today_str = today.strftime("%d%m%Y") # dd.mm.YYYY
        now = datetime.now()
        now_str=now.strftime("%H%M%S")

        #TODO: Could add there to collective memory?
        human_txt_file=COLLECTIVE_MEMORY_FOLDER+"text/"+"human_"+now_str+".txt"
        if len(utterance)>MIN_CHAR_MEMORY:
            with open(human_txt_file, 'w+') as f:
                f.write(utterance)

        global LOG_FULL
        #save output and message in text file #NOTE: here separate log file per day
        log_file=COLLECTIVE_MEMORY_FOLDER+"trace/"+today_str+".txt"
        if LOG_FULL:
            log_file=COLLECTIVE_MEMORY_FOLDER+"trace/"+today_str+"_2.txt"
        #---check size file sometimes 1/10 times
        if not LOG_FULL:
            rr=random.random()
            if rr<0.1 and os.path.exists(log_file):
                size = os.path.getsize(log_file) 
                if size > 4000: # in bytes 
                    LOG_FULL=True

        with open(log_file, 'a+') as f:
            f.write("¤¤¤hü¤¤¤"+ utterance+ "¤¤¤")
            f.write("\n")
            if len(chat_output)>3:
                f.write("¤¤¤vð¤¤¤"+chat_output+"¤¤¤")
                f.write("\n")
            f.write("¤¤¤vð¤¤¤"+output+"¤¤¤")
            f.write("\n\n")
        
        self.fresh_historics= utterance+ "\n" + output+ "\n"
        self.log.info("=======================================================")
        self.log.info("---END of this INTERACTION")
        self.log.info("=======================================================")

        return True


    def make_kin(self):
        """
            Make Kin practices
        """
        
        # start message
        ritual_start=random.choice(self.MSG_RITUAL_START)
        self.speak(ritual_start)
        time.sleep(WAIT_TIME_SHORT)

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
                    time.sleep(WAIT_FOR_HUMAN)
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
                    self.enclosure.eyes_color(255, 0, 0)  # set color red #WHAT FOR ?
                    self.last_index = 24
                    #self.schedule_repeating_event(self.recording_feedback, None, 1,
                    #                                name='RecordingFeedback')
                else:
                    self.speak_dialog("audio.record.disk.full")
                
                time.sleep(recording_time) #NOTE: NEEDED?  #TODO: RECORD TRANSCRIPTION STILL!, as converse do
  
                self.log.info("***RECORDING ENDED***")
                #thanks=random.choice(self.MSG_THANKS)
                #self.speak(thanks)

        time.sleep(WAIT_TIME_MEDIUM)
        #----Ending, ask back about the agent 
        ritual_end=random.choice(self.MSG_RITUAL_END)
        ritual_end=ritual_end.replace("xxx", agent)
        self.speak(ritual_end)

        return event

        


    def what_if(self, utterance):
        """
            What if Skill...
        """

         # step 1-- extract a keyword from what human said
        keyword= yake_extract_keyword(utterance, self.keyworder) #NOTE: May have issue with raspberry 4 with spacy?
        self.log.info("step 1---Extracted keyword"+keyword)
        self.log.info("=======================================================")

        # step 2--- pick a seed from file and replace if xxx by keyword
        if keyword=="":
            #reroute to enter the weird
            return self.enter_the_weird(utterance, historics=self.fresh_historics)
        else:
            #-----say it is interesting...
            interesting=random.choice(self.MSG_INTERESTING)
            interesting=interesting.replace("xxx", keyword)
            self.speak(interesting)

            seed = random.choice(self.whatif)
            seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
            self.log.info("step 2---Seed used"+seed)
            self.log.info("=======================================================")

            # step 3--Generate with gpt2 until okay
            self.log.info("step 3---gpt2 generation until pass the filter")
            cool=False
            count=0

            while ((not cool) and (count<MAX_TRY_REGENERATE)): 
                count+=1
                raw_response = self.gpt2_generation(seed, self.settings_what_if, remove_context=True)
                #judge answer:
                cool, uncool_score=cool_judge(raw_response, uncool_words=UNCOOL_WORDS_SET, uncool_string=UNCOOL_STRING, id_skill="what_if")
                if not cool:
                    self.log.info("***UNCOOL answer filtered out:***"+ raw_response)

            # step 4 ---
            self.log.info("step 4---final output")
            response=self.parse_text(seed+" "+ raw_response)
            #response=self.gingerParser.parse(response)['result']
            self.log.info("***COOL and filtered ***"+response)
            self.speak(response)
            self.log.info("=======================================================")
            #time.sleep(WAIT_TIME_MEDIUM)

            #step 4---closing: ask feedback 
            #feedback=random.choice(self.MSG_WHAT_IF_END)
            #self.speak(feedback)

            return response


    def fabulate(self):
        """
        Args: 
        """
        # step 2-- extract critter
        critter=random.choice(self.critters)
        self.log.info("step 2---Extracted critter"+critter)

        #TODO: Currently story without keyword as too rare close >>> could check similarity

        #---step 3 generate Story line by line
        story=""
        bla=""
        i=0
        for lines in self.storylines:
            i+=1
            #-pick a story line 
            line=random.choice(lines.split("\n"))
            #- replace xxx , yyy and cc
            line=line.replace("xxx", critter)
            line=line.replace("yyy", critter)
            line=line.replace("cc", str(random.randint(0,9))+str(random.randint(0,9)))
            #--read it
            seed, w=read_line(line, dico=self.dico)

            #---complete with gpt2  a few sentences
            cool=False
            count=0
            if i==1:
                MAX_TRY=MAX_TRY_REGENERATE
            else:
                MAX_TRY=1
            context=bla+seed #NOTE: Feed previous bla as context + seed
            
            while ((not cool) and (count<MAX_TRY)): 
                count+=1
                temp_settings=self.settings_what_if.copy()
                temp_settings["max_length"]=random.randint(MAX_LENGTH_FABULATE-VARIANCE_FABULATE, MAX_LENGTH_FABULATE+VARIANCE_FABULATE)
                
                #generate gpt2
                raw=self.gpt2_generation(context, temp_settings, remove_context=True)
                #if cool generation
                cool, uncool_score=cool_judge(raw, uncool_words=UNCOOL_WORDS_SET, uncool_string=UNCOOL_STRING)

            #--- cut it to a sentence 
            bla=self.parse_text(seed+" "+raw)

            #--- add it to story
            story+=bla + "\n"

        self.speak(story)
        self.log.info("Generated Story: \n"+ story)
        
        time.sleep(WAIT_TIME_MEDIUM)
        #step 4---closing: ask feedback 
        feedback=random.choice(self.MSG_FABULATE_END)
        feedback=feedback.replace("xxx", critter)
        self.speak(feedback)

        return story


    def wonder(self):
        """
        Args: 
        """
        #step 1---wonder start
        msg=random.choice(self.MSG_WONDER_START)
        self.speak(msg)
        time.sleep(WAIT_TIME_SHORT)

        # step 2-- extract critter
        critter=random.choice(self.critters)
        self.log.info("step 2---Extracted critter"+critter)


        #---step 3 pick stuff
        seed = random.choice(self.wonders)
        seed = seed.replace("xxx", critter)#replace xxx (if exist w/ ecological critter
        self.log.info("step 3---Seed used for generation"+seed)
        
        count=0
        cool=False

        while ((not cool) and (count<MAX_TRY_REGENERATE)): 
            count+=1
            #generate gpt2
            raw=self.gpt2_generation(seed, self.settings_what_if, remove_context=False) #TODO: Other settings ?
            #if cool generation
            cool, uncool_score=cool_judge(raw, uncool_words=UNCOOL_WORDS_SET, uncool_string=UNCOOL_STRING)

        #--- process it 
        wonder=self.parse_text(raw)
        self.speak(wonder)
        self.log.info("Generated:"+ wonder)
        
        rr=random.random()
        if rr<FEEDBACK_PROBA_WONDER:
            time.sleep(WAIT_TIME_MEDIUM)
            #step 4---closing: ask feedback 
            feedback=random.choice(self.MSG_WONDER_END)
            self.speak(feedback)

        return wonder


    def chat(self, utterance, historics=None):
        # ---1---encode the new user input, add the eos_token and return a tensor in Pytorch
        new_input_ids = self.dialoTokenizer.encode(utterance + self.dialoTokenizer.eos_token, return_tensors='pt')
        
        # -3---append the new user input tokens to the chat history
        if (historics is None) or (len(historics)<3):
            input_ids = new_input_ids
        else:
            #--2---for historics: replace all "\n" by EOS
            historics = historics.replace("\n", self.dialoTokenizer.eos_token)
            #token historics
            historics_id = self.dialoTokenizer.encode(historics + self.dialoTokenizer.eos_token, return_tensors='pt')
            #cut to amaximum length
            historics_id=historics_id[:, -MAX_TOKEN_HISTORICS:]
            input_ids = torch.cat([historics_id, new_input_ids], dim=-1)
        
        ctxt_len=input_ids.shape[-1]

        #-4----- generate chat 
        output=""
        count=0
        cool=False
        while (len(output)<8 or not cool) and count<3:
            count+=1
            # generated a response while limiting the total chat history to 1000 tokens, #ADD bad_words_ids=FORBIDDEN_TOKEN_ids,
            output_id = self.dialoGPT.generate(input_ids, min_length=CHAT_MIN_LENGTH, bad_words_ids=self.FORBIDDEN_TOKEN_ids, length_penalty=2, max_length=ctxt_len+CHAT_MAX_LENGTH, pad_token_id=self.dialoTokenizer.eos_token_id, temperature=CHAT_TEMPERATURE, repetition_penalty = 1.2, do_sample=True, top_k=CHAT_TOPK)#max_length=1000,
            #length_penalty >1 encourage generate longer sentences

            output= self.dialoTokenizer.decode(output_id[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
            #cut punctuation and check grammar
            output=self.parse_text(output)

            #TODO: use uncool score then 
            cool, uncool_score=cool_judge(output, uncool_words=UNCOOL_WORDS_SET, uncool_string=UNCOOL_STRING)

        if len(output)>3:
            self.speak(output)
            self.log.info(output)
            return output
        else:
            output=random.choice(self.MSG_PATIENT)
            self.speak(output)
            return output

    def gpt2_generation(self, seed, settings, remove_context=False, historics=None):
        #More parameters ? 
        #  #early_stopping=True, no_repeat_ngram_size=repetition_penalty,
        encoded_context = self.tokenizer.encode(seed, return_tensors="pt")
        
        if (historics is not None) and (len(historics)>2):
            #--for historics: replace all "\n" by EOS
            #historics = historics.replace("\n", dialoTokenizer.eos_token)#TODO: this also ok for gpt2?
            historics_id = self.tokenizer.encode(historics, return_tensors='pt')#+ dialoTokenizer.eos_token
            #cut to amaximum length
            encoded_context = torch.cat([historics_id, encoded_context], dim=-1)[:, -MAX_TOKEN_HISTORICS:]
        
        ctxt_len=encoded_context.shape[-1]

        #different sampling:
        if settings["sampling"]=="nucleus":
            generated = self.model.generate(encoded_context,bad_words_ids=self.FORBIDDEN_TOKEN_ids, min_length= settings["min_length"], max_length = ctxt_len+settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_p=settings["top_p"], top_k=0)
        elif settings["sampling"]=="topk":#top k sampling
            generated = self.model.generate(encoded_context,bad_words_ids=self.FORBIDDEN_TOKEN_ids, min_length= settings["min_length"], max_length = ctxt_len+settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=settings["top_k"])
        else:#base sampling
            generated = self.model.generate(encoded_context,bad_words_ids=self.FORBIDDEN_TOKEN_ids, min_length=settings["min_length"], max_length = ctxt_len+settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=0)
        #early_stopping=True, no_repeat_ngram_size=repetition_penalty,
        
        if remove_context:#remove both seed + historics, ie start from ctxt_len...
            raw_response = self.tokenizer.decode(generated.tolist()[0][ctxt_len:], clean_up_tokenization_spaces=True, skip_special_tokens=True)
            #return raw_response.replace(seed + historics, "")
        else:
            raw_response = self.tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
        
        return raw_response

    def one_drift(self, utterance, historics=None):
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

        while ((not cool) and (count<MAX_TRY_REGENERATE)): 
            count+=1
            #generate gpt2
            raw_drift = self.gpt2_generation(context, current_settings, remove_context=True, historics=historics)
            #if cool generation
            cool, uncool_score=cool_judge(raw_drift, uncool_words=UNCOOL_WORDS_SET, uncool_string=UNCOOL_STRING)
            if not cool:
                self.log.info("UNCOOL{} was filtered out,".format(count)+ raw_drift)


        self.log.info("=======================================================") 
        self.log.info("Step 3--Share the drift")
        self.log.info("=======================================================") 
        drift=self.parse_text(raw_drift)
        self.speak(drift)#
        self.log.info("***COOL and filtered ***"+drift)

        return drift


    def parse_text(self, bla):
        
        #replace I by We
        bla=bla.replace("I've", "We have")
        bla=bla.replace("I'd", "We had")
        bla=bla.replace("I'm", "We are")
        bla=bla.replace("I’m", "We are")
        bla=bla.replace("I am ", "We are ")
        bla=bla.replace("am I ", "are we ")
        bla=bla.replace("Am I ", "Are we ")
        bla=bla.replace("I'll", "We will")
        bla=bla.replace("I ", "We ")

        #good ending with punctuation
        bla=ending_with_punct_manual(bla)
        #grammar check:
        #drift=self.gingerParser.parse(drift)['result']
        split=split_into_sentences(bla)
        #split=[self.gingerParser.parse(_)['result'] for _ in split]
        split=[self.grammarParser.correct(_) for _ in split]

        return " ".join(split)
   
    def enter_the_weird(self, utterance, historics=None):
        """
            Several gpt-2 drifts from the last utterance
        """
        #---(0) patience
        be_patient=random.choice(self.MSG_PATIENT)
        self.speak(be_patient)
    

        #(1) Choose the mode and possible seed and add it
        loopCount=0
        bla=utterance+"\n"
        blabla=""
        while loopCount<self.settings_enter_the_weird["num_drifts"]:
            loopCount+=1
            self.log.info("Drift n° {loopCount}")
            if loopCount==1:
                bla=self.one_drift(bla, historics=historics)
            else:
                bla=self.one_drift(bla)
            blabla+=bla

        #step 4---closing: ask feedback #NOTE: probabilistically here
        rr=random.random()
        if rr<FEEDBACK_PROBA_WEIRD:
            time.sleep(WAIT_TIME_LONG)
            feedback=random.choice(self.MSG_FEEDBACK)
            self.speak(feedback)
        
        return blabla

    def elsewhere_tunes(self):
                
        #Even if sonor, small likelihood say text memory currently...
        self.log.info("=======================================================") 
        output=""
        if random.random()<self.sound_likelihood:
            self.log.info("Sonor tunes")
            self.log.info("=======================================================") 
            self.sonor_tunes()
        # elif random.uniform(0, 1)<self.sister_likelihood:
        #     self.log.info("Sister Node tunes")
        #     self.log.info("=======================================================") 
        #     self.sister_node_tunes() 
        else:
            self.log.info("Text tunes")
            self.log.info("=======================================================") 
            output=self.text_tunes() 
            
        self.log.info("=======================================================") 
        
        time.sleep(WAIT_TIME_MEDIUM)
        #step 4---closing: ask feedback 
        feedback=random.choice(self.MSG_ELSEWHERE_END)
        self.speak(feedback)

        return output
        

    def sonor_tunes(self):
        
        self.log.info("Step 1--Catch Attention")
        # step 1: catch attention ? or just as a burp
        travel=random.choice(self.MSG_ELSEWHERE_START)
        self.speak(travel)
        time.sleep(WAIT_TIME_SHORT)
        message_listen=random.choice(self.MSG_LISTEN)
        self.speak(message_listen) #For Website to play it 

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
        #output_path= COLLECTIVE_MEMORY_FOLDER+"temp.wav" #here just a temporary path
        #TODO: Temporarily disactivated because potential issues  
        #random_distortion(sound_path, output_path, proba_overlay=0.8, min_gain_drop=4, max_gain_drop=8, max_length=MAX_PLAY_SOUND)

        # step 5: playback the sound
        self.log.info("Step 4--Play the sound")
        #self.audio_service.play(output_path)
        self.audio_service.play(sound_path) #TODO: Temporarily, raw



    def text_tunes(self):

        self.log.info("Step 1--Pick a memory")
        #pick random text file from the memory
        text_file_name=random.choice(os.listdir(COLLECTIVE_MEMORY_FOLDER+"text/"))
        text_path=COLLECTIVE_MEMORY_FOLDER+"text/"+text_file_name

        #little message
        travel=random.choice(self.MSG_ELSEWHERE_START)
        self.speak(travel)
        time.sleep(WAIT_TIME_SHORT)

        self.log.info("Step 2--Share the text")
        # step 3: say the text
        with open(text_path, 'r') as f:
            lines = f.readlines()
        memory=" ".join(lines)[:self.MAX_CHAR_MEMORY]
        output= "\""+self.parse_text(memory)+"\""

        self.log.info(output)
        self.speak(output)

        return output


    def sister_node_tunes(self):

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
        #TODO: Ask feedback?



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

    