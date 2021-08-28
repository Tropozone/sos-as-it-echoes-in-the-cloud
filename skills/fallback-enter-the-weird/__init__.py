# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############

#--- NOW
#TODO: Clean this skill, as it is an old skill
#TODO: question Query TimeOut
# TODO: Too human filter
# TODO: Test with different versions homemade gpt2
# TODO: Use PERSONNA !

#--- LATER
#TODO: Use differentr seeds ?


# =============================================
# --------------INITIALIZATION---------------
# ======================================

# --------------IMPORTS----------------------
from mycroft.skills.core import FallbackSkill
import random
import transformers 
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import pathlib

#For NLP: no need (only for filter if...)
# import nltk
# #nltk.download('punkt') # to use the first time
# #nltk.download('wordnet') # to use the first time
# #nltk.download('wordnet_ic') # to use the first time
# from nltk import word_tokenize, sent_tokenize, pos_tag
# from nltk.corpus import wordnet
# from nltk.stem.wordnet import WordNetLemmatizer
# lemmatizer = WordNetLemmatizer()
#TOKENIZERS_PARALLELISM=False #TODO Check tokenizer parallelism hugging face. May need this.?

# --------------PARAMETERS to TUNE---------------------
MAX_LENGTH = 150
VARIANCE_LENGTH = 20
TEMPERATURE = 0.8
REPETITION_PENALTY = 1.4
NUMBER_DRIFTS=3

# --------------PARAMETERS ---------------------
my_ML_model = False  # If do have a fine-tuned model, set to True
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-MLdrift/gpt2_model'  # path to your fine tuned model


#******************************MAIN PROCEDURE**********

class MLdriftFallback(FallbackSkill):
    """
        A Fallback skill running some ML drits with gpt2, and a mode.
    """
    def __init__(self):
        super(MLdriftFallback, self).__init__(name='MLdrift')
        #self.moodySeed=""
        # Initialize model
        if my_ML_model:
            self.model = GPT2LMHeadModel.from_pretrained(my_ML_model_path)
        else:
            self.model=GPT2LMHeadModel.from_pretrained("gpt2")
        # Initialize tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # setting generation
        self.init_settings()

    def init_settings(self):
        # min free diskspace (MB)
        self.settings.setdefault("repetition_penalty", REPETITION_PENALTY)  
        self.settings.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
        self.settings.setdefault("max_length", MAX_LENGTH)
        self.settings.setdefault("variance_length", VARIANCE_LENGTH)
        self.settings.setdefault("num_drifts", NUM_DRIFTS)


    def initialize(self):
        """
            Registers the fallback handler.
            The second Argument is the priority associated to the request.
            Lower is higher priority. But number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_drift, 6)
        # Could register several handle

            

    def handle_one_drift(self, utterance):
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
        max_length= self.settings["max_length"]+random.randint(-self.settings["variance"], self.settings["variance"])
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

    #The method that will be called to potentially handle the Utterance
    #The method implements logic to determine if the Utterance can be handled and shall output speech if itcan handle the query.
    #For now, will handle all query.
    def handle_drift(self, message):
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
            bla=self.handle_one_drift(bla) #Only keep last part as context else too big? >>>
            blabla+=bla
        return True

    #the Skill creator must make sure the skill handler is removed when the Skill is shutdown by the system.
    def shutdown(self):
        """
            Remove this skill from list of fallback skills.
        """
        self.remove_fallback(self.handle_drift)
        super(MLdriftFallback, self).shutdown()

#***********************************************************************create SKILL***************************************************************************

def create_skill():
    return MLdriftFallback()



#***********************************************************************PRELIMINARIES***************************************************************************

    # def pickMoodySeed(self):
    #     """
    #        Choose a seed to potentially add as contaxt for the gpt-2 Drift
    #     """
    #     if randomMode: #if random Mode chosen only
    #         #From the dictionnary probaMode randomly pick a mode following their probability
    #         currentMode=random.choices(population=list(probaMode.keys()), weights=list(probaMode.values()), k=1)[0]
    #     else:
    #         currentMode=defaultMode
    #     if currentMode in modeSeeds.keys():#in case mode entered wrong by human to avoid error
    #         self.moodySeed=random.choice(modeSeeds[currentMode])
