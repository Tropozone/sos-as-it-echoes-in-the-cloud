# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############

#TODO: not a FALLBACK?, spontaneous trigger...
# #TODO: use regex for reading text file

#*********************************************INITIALIZATION***********


from mycroft.skills.core import FallbackSkill
import random
import transformers 
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import pathlib

#******************************************PARAMETERS ****************************

# GPT-2 parameters
# Once you have your own model, adjust these accordingly
my_ML_model = False  # If do have a fine-tuned model, set to True
# Global path_finetuned_ML_model #TODO: CHange path... here placed in another skill
my_ML_model_path = str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-MLdrift/gpt2_model'  # path to your fine tuned model


# More parameters are available and more detail about gpt-2 parameters can be found here: https://huggingface.co/blog/how-to-generate
# Maximum length of the generated answer, counted in characters and spaces.
length_drift = 200 #TODO: stochastic
# Increase the likelihood of high probability words by lowering the temperature (aka make it sound more 'normal')
temperature = 0.8
# Repetition penalty. In general makes sentences shorter and reduces repetition of words an punctuation.
repetition_penalty = 1.4



##-**************** UTILS 

#TODO COMMON FOR DIFFERENT ML SKILLS!
# simply cleans up machine-generated text
def clean_text(question, generated):
    # remove the question text from the generated answer
    output = generated.replace(question, '')
    # remove incomplete sencentes at the end, if any.
    output = output.rsplit('.', 1)[0] + '.'
    return output


def load_data_kin(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.read() #here string with '\n' in it
    #cut into list when jump lines
    sliced_data=data.slice ('\n \n')#TODO: check ok
    sliced_data=sliced_data.replace('\n', "")#if single ones remaining?
    return sliced_data

def load_objects():
    path_folder=str(pathlib.Path(__file__).parent.absolute())
    #self.log.info(str(pathlib.Path(__file__).parent.absolute()))
    return load_data_txt("objects.txt", path_folder=path_folder)

def load_data_txt(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.readlines()
    return data

def load_makingkin():
    path_folder=str(pathlib.Path(__file__).parent.absolute())
    #self.log.info(str(pathlib.Path(__file__).parent.absolute()))
    return load_data_kin("yoko.txt", path_folder=path_folder)

def read_event(event_score, agent):
    
    event=event_score.replace("xxx", agent)#replace xxx (if exist w/ keyword)
    #TODO: more variation, generations...
    return event

#******************************MAIN PROCEDURE**********



class HelloSocketFallback(FallbackSkill):

    def __init__(self):
        super(HelloSocketFallback, self).__init__(name='Hello Socket Fallback Skill')

        # load events and objects
        self.events= load_makingkin()
        self.objects= load_objects()

    def initialize(self):
        """
            Registers the fallback handler.
            The second argument is the priority associated to the request;
            Because there are several fallback skills available, priority helps
            to tell Mycroft how 'sensitively' this particular skill should be triggered.
            Lower number means higher priority, however number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_make_kin, 6)

    def make_kin(self):
        """
            Fabulate
        """

        # step 1-- pick an object
        agent= random.choice(self.objects)
        self.log.info("=======================================================")
        self.log.info("step 1---Extracted object"+agent)
        self.log.info("=======================================================")

        # step 2--- pick a seed from file and replace if xxx by keyword
        event_score = random.choice(self.events)
        event=read_event(event_score, agent) #define it.
        self.log.info("=======================================================")
        self.log.info("step 2---Event:"+event)
        self.log.info("=======================================================")

        # step 3 --Speak generated text aloud
        self.speak(event)

        #TODO: wait for comment about it?
        #TODO: More interactive with VA, has to record it to send to network>>>

    def handle_make_kin(self, message):
        """
            Several gpt-2 drifts from the last utterance, with a possible mode
        """
        # Obtain what the human said
        utterance = message.data.get("utterance")#TODO: here not utterance...

        self.make_kin(utterance)

        return True

    # Required: Skill creator must make sure the skill is removed when the Skill is shutdown by the system.
    def shutdown(self):
        """
            Remove the skill from list of fallback skills
        """
        self.remove_fallback(self.handle_make_kin)
        super(HelloSocketFallback, self).shutdown()


##-----------------CREATE

def create_skill():
    return HelloSocketFallback()

    