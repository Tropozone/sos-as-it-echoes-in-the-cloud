# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############


# ============================================
# ------------------TODO--------------------
# =========================================

#--- NOW
#TODO: Issue with cut one sentence
#TODO: tructure of a fabulation instead, query only gpt2 for words?  or use generator without ML?
#TODO: ML PATH share
#TODO: More interaction with human? Ask its reaction, opintion ?

#--- LATER
#TODO: Rethink which sentences work well!
#TODO: SHare some utils proc betweemn skills
#TODO: Add grammar check?

# More parameters are available and more detail about gpt-2 parameters can be found here: https://huggingface.co/blog/how-to-generate


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
import re
import spacy

from .utils import extract_keywords, load_whatif, cut_one_sentence, clean_text

#import os
#os.environ['KMP_DUPLICATE_LIB_OK']='True' #ONLY IF ERROR MESSAGE

# --------------PARAMETERS to TUNE---------------------
MAX_LENGTH = 80
TEMPERATURE = 0.8
REPETITION_PENALTY = 1.4

# --------------PARAMETERS ---------------------
my_ML_model = False  # If do have a fine-tuned model, set to True
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-MLdrift/gpt2_model'  # path to your fine tuned model
# ===========================================
# -------------- SKILL ---------------
# ======================================

class WhatIfWeBucketFallback(FallbackSkill):

    def __init__(self):
        super(WhatIfWeBucketFallback, self).__init__(name='What If We Bucket Fallback Skill')

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
        self.keyworder = spacy.load("en_core_web_sm")

        # load
        self.whatif = load_whatif()

        # setting generation
        self.init_what_if()

    def init_what_if(self):
        # min free diskspace (MB)
        self.settings.setdefault("repetition_penalty", REPETITION_PENALTY)  
        self.settings.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
        self.settings.setdefault("max_length", MAX_LENGTH)

    def initialize(self):
        """
            Registers the fallback handler.
            The second argument is the priority associated to the request;
            Because there are several fallback skills available, priority helps
            to tell Mycroft how 'sensitively' this particular skill should be triggered.
            Lower number means higher priority, however number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_fantasize, 6)




    def handle_fantasize(self, message):
        """
            Several gpt-2 drifts from the last utterance, with a possible mode
        """
        # step 0 --Obtain what the human said
        utterance = message.data.get("utterance")

         # step 1-- extract a keyword from what human said
        keyword= extract_keywords(utterance, self.keyworder)
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

        # step 4 --- #TODO: Filter text cut, ?
        response=raw_response
        self.speak(response)

        return True

    # Required: Skill creator must make sure the skill is removed when the Skill is shutdown by the system.
    def shutdown(self):
        """
            Remove the skill from list of fallback skills
        """
        self.remove_fallback(self.handle_fantasize)
        super(WhatIfWeBucketFallback, self).shutdown()

    

##-----------------CREATE

def create_skill():
    return WhatIfWeBucketFallback()

