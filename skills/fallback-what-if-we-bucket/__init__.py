# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############



#TODO: or structure of a fabulation instead, query only gpt2 for words? 
#TODO: or use generator without ML?
#TODO: Rethink which sentences work well!

#*********************************************INITIALIZATION***********


from mycroft.skills.core import FallbackSkill
import random
import transformers 
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import pathlib
import re

#import os
#os.environ['KMP_DUPLICATE_LIB_OK']='True' #ONLY IF ERROR MESSAGE

#******************************************PARAMETERS ****************************

# GPT-2 parameters
# Once you have your own model, adjust these accordingly
my_ML_model = False  # If do have a fine-tuned model, set to True
# Global path_finetuned_ML_model #TODO: CHange path... here placed in another skill
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-MLdrift/gpt2_model'  # path to your fine tuned model

# More parameters are available and more detail about gpt-2 parameters can be found here: https://huggingface.co/blog/how-to-generate
# Maximum length of the generated answer, counted in characters and spaces.
length_drift = 80
var_drift=20
# Increase the likelihood of high probability words by lowering the temperature (aka make it sound more 'normal')
temperature = 0.8
# Repetition penalty. In general makes sentences shorter and reduces repetition of words an punctuation.
repetition_penalty = 1.4


#*****************************UTILS **********

# #TODO: ok to be there?

#TODO COMMON FOR DIFFERENT ML SKILLS!
# simply cleans up machine-generated text
def clean_text(question, generated):
    # remove the question text from the generated answer
    output = generated.replace(question, '')
    # remove incomplete sencentes at the end, if any.
    output = output.rsplit('.', 1)[0] + '.'
    return output


def cut_one_sentence(generated):
    output = re.split('.|?|!', generated)[0]+"."
    return output


#TODO COMMON FOR DIFFERENT SKILLS!
def extract_keywords(input):
    # we're looking for proper nouns, nouns, and adjectives
    pos_tag = ['PROPN', 'NOUN', 'ADJ']
    # tokenize and store input
    phrase = keyworder(input.lower())
    keywords = []
    # for each tokenized word
    for token in phrase:
        # if word is a proper noun, noun, or adjective;
        if token.pos_ in pos_tag:
            # and if NOT a stop word or NOT punctuation
            if token.text not in keyworder.Defaults.stop_words or token.text not in punctuation:
                keywords.append(token.text)
    # convert list back to string
    key_string = " ".join(keywords)

    return key_string

def load_whatif():
    path_folder=str(pathlib.Path(__file__).parent.absolute())
    #self.log.info(str(pathlib.Path(__file__).parent.absolute()))
    return load_data_txt("/whatif.txt", path_folder=path_folder)

def load_data_txt(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.readlines()
    return data
    
#******************************MAIN PROCEDURE**********


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
        # load
        self.whatif = load_whatif()

    def initialize(self):
        """
            Registers the fallback handler.
            The second argument is the priority associated to the request;
            Because there are several fallback skills available, priority helps
            to tell Mycroft how 'sensitively' this particular skill should be triggered.
            Lower number means higher priority, however number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_fantasize, 6)

    def fantasize(self, question):
        """
            Fabulate
        """
        #TODO: think about specific questions?

        # step 1-- extract a keyword from what human said
        keyword= extract_keywords(human_bla)
        self.log.info("=======================================================")
        self.log.info("step 1---Extracted keyword"+keyword)
        self.log.info("=======================================================")

        # step 2--- pick a seed from file and replace if xxx by keyword
        seed = random.choice(self.whatif)
        seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
        self.log.info("=======================================================")
        self.log.info("step 2---Seed used"+seed)
        self.log.info("=======================================================")

        #  # step2---Say a splash phrase since the generation might take a while#TODO: keep?
        # splash_phrases = ["Lemme think for a minute", "Give me a minute to think about my answer",
        #                   "I need some time to think about this", "Hold on while I think this through"]
        # self.speak(random.choice(splash_phrases))

        # step 3--Generate machine learning text based on parameters
        self.log.info("=======================================================")
        self.log.info("step 3---gpt2 generation..."+seed)
        
        encoded_context = self.tokenizer.encode(seed, return_tensors="pt")
        #early_stopping=True, no_repeat_ngram_size=repetition_penalty,
        generated = self.model.generate(encoded_context, max_length = length_drift , temperature= temperature, repetition_penalty = repetition_penalty, do_sample=True, top_k=20)
        response = self.tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
        self.log.info(response)
        self.log.info("=======================================================")

        #step 4 --- #TODO: Filter ?
        # Text cleaning function to go here
        # cleaned_output = clean_text(question, output)
        #response=cut_one_sentence(response)#TODO: CUt or not? ISSUE with this cut!

        # step 5 --Speak generated text aloud
        self.speak(response)

    def handle_fantasize(self, message):
        """
            Several gpt-2 drifts from the last utterance, with a possible mode
        """
        # Obtain what the human said
        utterance = message.data.get("utterance")

        self.fantasize(utterance)

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

