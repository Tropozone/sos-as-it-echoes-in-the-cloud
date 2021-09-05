# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############

# =============================================
# --------------INITIALIZATION---------------
# ======================================

# --------------IMPORTS----------------------
from mycroft.skills.core import FallbackSkill
import random
import pathlib
import time
from .utils import load_makingkin, load_objects, read_event, extract_keywords, load_whatif, cut_one_sentence, clean_text

import re
import os
#import spacy #Temporarily desactivate spacy
import torch
import transformers 
from transformers import GPT2Tokenizer, GPT2LMHeadModel


from mycroft.skills.audioservice import AudioService


# --------PARAMETERS TO TUNE-----------------------
WAITING_TIME=5 #waiting time in seconds where will wait for human...

# -------------OTHER PARAMETERS----------------------
WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-merge/data/"
WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]


# --------------PARAMETERS to TUNE---------------------
MAX_LENGTH = 80
TEMPERATURE = 0.8
REPETITION_PENALTY = 1.4

# --------------PARAMETERS ---------------------
my_ML_model = False  # If do have a fine-tuned model, set to True
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-merge/gpt2_model'  # path to your fine tuned model


#TODO: OTHER PARAM FOR ENTER THE WEIRD...
MAX_LENGTH = 100
VARIANCE_LENGTH = 20
TEMPERATURE = 0.8
REPETITION_PENALTY = 1.4
NUM_DRIFTS=1



memory_folder=os.path.dirname(os.path.realpath(__file__)) +"/memory/"


# =============================================
# ------------------SKILL---------------
# =============================================

class MergeFallback(FallbackSkill):

    def __init__(self):
        super(MergeFallback, self).__init__(name='Merge Fallback Skill')    
        self.log.info("*****INIT FALLBACK MERGE ****")
        #Merge Fallback reroute to the following skills: hello socket, what if we bucket, ELsewhereTunes, Enter the ")
        self.SUBSKILLS=["Hello Socket", "What if we bucket", "Enter the Weird", "Elsewhere Tunes"]
        #TODO: ADD elsewhere tunes...

        self.init_hello_socket()
        self.init_what_if_we_bucket()
        self.init_enter_the_weird()
        self.init_elsewhere_tunes()


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
        self.log.info("Init What if We Bucket - in fallback-merge")
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
        # self.keyworder = spacy.load("en_core_web_sm") #temporarily desactivated
        # load
        self.whatif = load_whatif()

        self.settings.setdefault("repetition_penalty", REPETITION_PENALTY)  
        self.settings.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
        self.settings.setdefault("max_length", MAX_LENGTH)

        
    def init_enter_the_weird(self):
        self.log.info("Init Enter the Void - in fallback-merge")
        #TODO: DIFFERENT VALUES
        # min free diskspace (MB)
        self.settings.setdefault("repetition_penalty", REPETITION_PENALTY)  
        self.settings.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
        self.settings.setdefault("max_length", MAX_LENGTH)
        self.settings.setdefault("variance_length", VARIANCE_LENGTH)
        self.settings.setdefault("num_drifts", NUM_DRIFTS)

        
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
        
        rand= random.randint(0,3)
        if rand==0:
            self.log.info("***Redirecting to Hello Socket***")
            #"Hello Socket"
            self.make_kin(message)

        elif rand==1:
            self.log.info("***Redirecting to What if We Bucket***")
            #"What if we bucket"
            self.what_if(message)

        elif rand==2:
            self.log.info("***Redirecting to Enter the Weird***")
            #"Enter the Weird
            self.enter_the_weird(message)

            
        elif rand==3:
            self.log.info("***Redirecting to Elsewhere Tunes***")
            #Elsewhere Tunes
            self.elsewhere_tunes(message)
        
        else:
            raise NotImplementedError


        
        return True




    def make_kin(self, message):
        """
            Make Kin practices
        """
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
        



    def what_if(self, message):
        """
            Several gpt-2 drifts from the last utterance, with a possible mode
        """
        # step 0 --Obtain what the human said
        utterance = message.data.get("utterance")

         # step 1-- extract a keyword from what human said
        # keyword= extract_keywords(utterance, self.keyworder) #TODO: Reenable this once spacy issue fine
        keyword = "petrol"
        self.log.info("step 1---Extracted keyword"+keyword)
        self.log.info("=======================================================")

        # step 2--- pick a seed from file and replace if xxx by keyword
        seed = random.choice(self.whatif)
        seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
        encoded_context = self.tokenizer.encode(seed, return_tensors="pt")
        self.log.info("step 2---Seed used"+seed)
        self.log.info("=======================================================")

        # step 3--Generate machine learning text based on parameters
        self.log.info("step 3---gpt2 generation...")
        generated = self.model.generate(encoded_context, max_length = self.settings["max_length"], temperature=self.settings["temperature"], repetition_penalty = self.settings["repetition_penalty"], do_sample=True, top_k=20)
        #early_stopping=True, no_repeat_ngram_size=repetition_penalty,
        raw_response = self.tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
        self.log.info(raw_response)
        self.log.info("=======================================================")

        # step 4 --- #TODO: Filter text cut ?
        response=raw_response
        self.speak(response)



    def one_drift(self, utterance):
        """
            One gpt-2 drift from the last blabla
        """
        too_human=False

        # step 1--- Choose the mode and possible seed and add it after the blabla
        # self.pickMoodySeed()
        # blabla=blabla+ " " + self.moodySeed

        seed="" #TODO: May want to change context
        context = utterance + seed

        self.log.info("=======================================================")
        self.log.info("Step 1--context:"+context )
        self.log.info("=======================================================") 

        
        #step 2--- ML Drift according to parameters
        self.log.info("=======================================================")
        self.log.info("Step 2--gpt2 generation....")
        encoded_context= self.tokenizer.encode(context, return_tensors = "pt")
        max_length= self.settings["max_length"]+random.randint(-self.settings["variance_length"], self.settings["variance_length"])
        generated = self.model.generate(encoded_context, max_length = max_length , temperature= self.settings["temperature"], repetition_penalty = self.settings["repetition_penalty"], do_sample=True, top_k=10)
        self.log.info("Step 3--gpt2 generation....")
        drift = self.tokenizer.decode(generated.tolist()[0])
        self.log.info("gpt2 Response: "+ drift)
        self.log.info("=======================================================") 

        #step 3--- Check if too Human, if so regenerate
        #TODO: too_human filter
        if too_human:
            self.log.info("=======================================================")
            self.log.info("Step 3 bis--gpt2 re generation as first one was too human....")
            generated = self.model.generate(encoded_context, max_length = max_length ,temperature= self.settings["temperature"], repetition_penalty = self.settings["repetition_penalty"], do_sample=True, top_k=10)
            drift = self.tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
            #replace what human said if still there:
            drift = drift.replace(str(utterance), "", 1)
            self.log.info("gpt2 Response: "+ drift)
            self.log.info("=======================================================") 
        
        #step 5--- Filter the Drift i?
        # #TODO: Filter // Clean
        filtered_drift=drift

        #step 6 --- Say the drift out loud
        self.speak(filtered_drift)#

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


        # step 1: pick sound from collective memory
        sound_path=random.choice(os.listdir(memory_folder))

        # # step 2: wait, in case skill triggered
        # sleep(15)
        
        # step 3: catch attention
        message="Listen."#TODO: Shall add a message for transition?
        self.log.info(message)
        self.speak(message)

        # step 4: playback the sound
        self.log.info("Playing one sound")
        self.audio_service.play(sound_path)




    def shutdown(self):
        """
            Remove the skill from list of fallback skills
        """
        self.remove_fallback(self.handle_routing)
        super(MergeFallback, self).shutdown()


##-----------------CREATE

def create_skill():
    return MergeFallback()

    