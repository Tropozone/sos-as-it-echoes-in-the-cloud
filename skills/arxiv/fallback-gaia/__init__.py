# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

from mycroft.skills.core import FallbackSkill
import random
#Parameters for the ML Drift
from . import parametersDrift
import filtering #Script to clean the data
#For the ML Drift
import transformers
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
#Import script
import coreGaia

class GaiaFallback(FallbackSkill):
    """
        A Fallback skill running some ML drits with gpt2, and a mood.
    """
    def __init__(self):
        super(GaiaFallback, self).__init__(name='Gaia')
        #Parameters for the gpt2-drif, are uploaded from file parametersDrift.py
        self.mood=parametersDrift.currentMood
        self.lengthDrift=parametersDrift.lengthDrift
        self.nDrift=parametersDrift.nDrift
        self.randomizeMood=parametersDrift.randomizeMood
        self.moodSeeds=parametersDrift.moodSeeds
        self.probaMood=parametersDrift.probaMood
        self.temperature=parametersDrift.temperature
        self.repetition_penalty=parametersDrift.repetition_penalty
        self.moodySeed=""
        self.finetuned_ML_model=parametersDrift.finetuned_ML_model
        self.path_finetuned_ML_model=parametersDrift.path_finetuned_ML_model

        self.minText=300 # >>choose minimum char not to reject text
        # Initialize machine learning
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        if self.finetuned_ML_model:
            self.model = GPT2LMHeadModel.from_pretrained(self.path_finetuned_ML_model) 
        else:
            self.model=GPT2LMHeadModel.from_pretrained("gpt2")


    def initialize(self):
        """
            Registers the fallback handler. 
            The second Argument is the priority associated to the request. 
            Lower is higher priority. But number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_Gaia, 1) #here choose to bypass everything
        # Could register several handle

   
    def pickMoodySeed(self):
        """
           Choose a moody seed to potentially add as contaxt for the gpt-2 Drift
        """
        if self.randomizeMood: #if randomize Mood chosen only
            #From the dictionnary probaMood randomly pick a mood following their probability
            self.mood=random.choices(population=list(self.probaMood.keys()), weights=list(self.probaMood.values()), k=1)[0]
        if self.mood in self.moodSeeds.keys():#in case mode entered wrong by human to avoid error
            self.moodySeed=random.choice(self.moodSeeds[self.mood])

    def updateParam(self):
        """
           Update parameters for the gpt-2 drift
        """
        self.mood=parametersDrift.currentMood
        self.lengthDrift=parametersDrift.lengthDrift
        self.nDrift=parametersDrift.nDrift
        self.randomizeMood=parametersDrift.randomizeMood
        self.moodSeeds=parametersDrift.moodSeeds
        self.probaMood=parametersDrift.probaMood
        self.temperature=parametersDrift.temperature
        self.repetition_penalty=parametersDrift.repetition_penalty
        self.moodySeed=""
        self.finetuned_ML_model=parametersDrift.finetuned_ML_model
        self.path_finetuned_ML_model=parametersDrift.path_finetuned_ML_model


    def handle_Gaia(self, message):
        #(0)Update the parameters according to the file.
        self.updateParam()
        #(1) Get the human utterance
        utterance = message.data.get("utterance")
        #(2) Extract the Nouns in the utterance
        nouns=coreGaia.extractNouns(utterance)
        #(3) Do a climate Check on one of them, and say result loud 
        #for now pick one but later on should look for the best>>>
        if len(nouns)>0:
            title, outputNet=coreGaia.scrapOne(nouns[0], self.minText) 
            speakOut="You talk about {} I am not sure what you mean. But I heard something about it.".format(nouns[0])
            speakOut+= title + outputNet
            self.speak(speakOut)
            #(4) Generate ML Drift from it, filter it and say it
            blabla=self.handle_ML(outputNet)
            return True #has handled it
        else:
            return False

    def handle_ML(self, blabla):
        """
            One gpt-2 drift from the last blabla
        """

        #(1) Choose the mood and possible seed and add it after the blabla
        self.pickMoodySeed()
        blabla=blabla+ " " + self.moodySeed

        #(2) ML Drift according to parameters
        process = self.tokenizer.encode(blabla, return_tensors = "pt")
        generator = self.model.generate(process, max_length = self.lengthDrift, temperature = self.temperature, repetition_penalty = self.repetition_penalty)
        drift = self.tokenizer.decode(generator.tolist()[0])
        print(drift)

        #(3) Filter the Drift. Here a small filtering procedure. 
        #Yet you are free to change the parameters, make it your own, by pass this step (comment out)
        filtered_drift=filtering.filterText(drift, maxNonAlpha=15, maxRatio=0.3)
        
        #(4) Say the drift out loud
        self.speak(filtered_drift)

        return filtered_drift


    #the Skill creator must make sure the skill handler is removed when the Skill is shutdown by the system.
    def shutdown(self):
        """
            Remove this skill from list of fallback skills.
        """
        self.remove_fallback(self.handle_Gaia)
        super(GaiaFallback, self).shutdown()


def create_skill():
    return GaiaFallback()
