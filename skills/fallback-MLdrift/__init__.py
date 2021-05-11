# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############


#TODO: Clean this skill, as it is an old skill
#TODO: question Query TimeOut
#TODO: Change path and where put model: in another folder where can share?

#*************************************INITIALIZATION***************

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

#******************************************PARAMETERS ****************************

######Classic gpt-2 parameters:
# Once you have your own model, adjust these accordingly
my_ML_model = True # If do have a fine-tuned model, set to True
my_ML_model_path = str(pathlib.Path(__file__).parent.absolute())+'/gpt2_model'  # path to your fine tuned model

# More parameters are available and more detail about gpt-2 parameters can be found here: https://huggingface.co/blog/how-to-generate
# Maximum length of the generated answer, counted in characters and spaces.
length_drift = 100
var_length = 20
# Increase the likelihood of high probability words by lowering the temperature (aka make it sound more 'normal')
temperature = 0.9
# Repetition penalty. In general makes sentences shorter and reduces repetition of words an punctuation.
repetition_penalty = 1.4
# Number successive generations:
nDrift=1

#*****************************OLD PARAMETERS for the ML Drift********************

# randomMode= True #if decide randomize moods
# defaultMode='neutral' #If not, here is the mode chosen

# ######## To slightly influence the gpt-2 outcome, so-called 'Mode'.
# #Below are only saturated example for better illustration. But you can tune them
# #Possible Modes for the ML Drift, with their probabilities.
# #Keeping the category neutral as such, with an empty string only, enable have the possibility of a neutral Mode, so unaltered ML drift.
# modeSeeds=dict()
# modeSeeds["curious"]=["Why are they", "Why do they", "How could we", "I wonder if", "I wonder how", "Why are there still", "What should we think of", "Is there something like"]
# modeSeeds["confrontational"]=["Maybe not.", "Yet, I feel this is wrong. ", "I would argue against this.", "I would prefer not to.", "What if this is bullshit?", "I don't believe in this. Listen,"]
# modeSeeds["thrilled"]=["Amazing.", "That is wonderful.", "How beautiful is this.", "That is incredible."]
# modeSeeds["emotional"]=["It makes me feel", "I feel like"]
# modeSeeds["appreciative"]=["Let us appreciate how", "Let us contemplate the", "Now, let us breathe and take a moment for", "Let us welcome the", "Let us appreciate what", "Instead of opposing, we shoud embrace", "I would like to thank the world for what"]
# modeSeeds["thrilled"]=["Amazing.", "That is wonderful.", "How beautiful is this.", "That is incredible."]
# modeSeeds["neutral"]=[""]

# #RProbabilities of the different Modes
# probaMode=dict()
# probaMode["curious"]=0.2
# probaMode["confrontational"]=0.2
# probaMode["thrilled"]=0.1
# probaMode["emotional"]=0.1
# probaMode["appreciative"]=0.1
# probaMode["thrilled"]=0.1
# probaMode["neutral"]=0.2

# global maxNonAlpha
# maxNonAlpha=5
# global maxRatio
# maxRatio=0.3


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

    def initialize(self):
        """
            Registers the fallback handler.
            The second Argument is the priority associated to the request.
            Lower is higher priority. But number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_drift, 6)
        # Could register several handle


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

        #  # step2---Say a splash phrase since the generation might take a while#TODO: keep?
        # splash_phrases = ["Lemme think for a minute", "Give me a minute to think about my answer",
        #                   "I need some time to think about this", "Hold on while I think this through"]
        # self.speak(random.choice(splash_phrases))

        #step3--- ML Drift according to parameters
        self.log.info("=======================================================")
        self.log.info("Step 3--gpt2 generation....")
        encoded_context= self.tokenizer.encode(context, return_tensors = "pt")
        max_length= length_drift+random.randint(-var_length,var_length)
        generated = self.model.generate(encoded_context, max_length = max_length , temperature= temperature, repetition_penalty = repetition_penalty, do_sample=True, top_k=10)
        self.log.info("Step 3--gpt2 generation....")
        drift = self.tokenizer.decode(generated.tolist()[0])
        self.log.info("gpt2 Response: "+ drift)
        self.log.info("=======================================================") 

        #step 4--- Check if too Human, if so regenerate
        #TODO: too_human filter
        if too_human:
            self.log.info("=======================================================")
            self.log.info("Step 3 bis--gpt2 re generation as first one was too human....")
            generated = self.model.generate(encoded_context, max_length = length_drift , temperature= temperature, repetition_penalty = repetition_penalty, do_sample=True, top_k=20)
            drift = self.tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
            #replace what human said if still there:
            drift = drift.replace(str(utterance), "", 1)
            self.log.info("gpt2 Response: "+ drift)
            self.log.info("=======================================================") 

        
        #step 5--- Filter the Drift i?#TODO: Wanna filter ?
        #Yet you are free to change the parameters, make it your own, by pass this step (comment out)
        #filtered_drift=filterText(drift, maxNonAlpha, maxRatio)

        #step 6 --- clean drift from original part and end
        self.log.info("=======================================================")
        self.log.info("Step 6--Cleaning drift")
        cleaned_drift=clean_text(utterance, drift)
        self.log.info("=======================================================")

        #step 7 --- Say the drift out loud
        self.speak(drift)#filtered_drift)

        return drift

    #The method that will be called to potentially handle the Utterance
    #The method implements logic to determine if the Utterance can be handled and shall output speech if itcan handle the query.
    #For now, will handle all query.
    def handle_drift(self, message):
        """
            Several gpt-2 drifts from the last utterance, with a possible mode
        """
        #TODO: as a converse?
        #(0) Get the human utterance
        utterance = message.data.get("utterance")
        #(1) Choose the mode and possible seed and add it
        loopCount=0
        while loopCount<nDrift:
            loopCount+=1
            self.log.info("Drift n° {loopCount}")
            blabla=self.handle_one_drift(utterance) #Only keep last part as context else too big? >>>

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
# simply cleans up machine-generated text
def clean_text(origin, generated):
    # remove origin text from the generated answer
    output = generated.replace(origin, '')
    # remove incomplete sencentes at the end, if any.
    output = output.rsplit('.', 1)[0] + '.'
    return output


# def alphabetRatio(inputString):
#     """
#         Return number and ratio of non alphabetic character (white spaces not included) in a sentence
#     """
#     count=0
#     ratio=0
#     for char in inputString:
#         if not char.isalpha() and not char==" ":
#             count+=1
#     if not len(inputString)==0:
#         ratio=count/len(inputString)
#     return ratio, count


# def filterText(blabla, maxNonAlpha, maxRatio):
#     """
#         Filter a text: remove sentences with higher non alphabetic number of character than the indicated max.
#        Remove sentence with higher non alphabetical character ratio too than the indicated one.
#        Output: Filtered text with the filteredRatio (between 0 and 1) measuring the amount of text which remains.

#        NB: Filtering procedures are a very specialised matter, and depend of the outcome you want to have.
#        You could check repetition of characters, or too long words.
#        Or even filter any sentence which does not make gramatical sense (yet, this may be too strong criteria).
#        You can filter also unrecognised words (yet depend if you have proper noun), etc.
#     """
#     sentences=nltk.tokenize.sent_tokenize(blabla)
#     filtered_bla=""
#     for i, sentence in enumerate(sentences):
#         ratio, count=alphabetRatio(sentence) #ratio non letter elements
#         if len(sentence)>3 and ratio<maxRatio and count<maxNonAlpha and i<len(sentences)-1:   #Test if not to many symbols and grammar ok
#                 filtered_bla+=sentence
#     filteredRatio = len(filtered_bla)/len(blabla) #. Ideally it's close to 1
#     self.log.info(filtered_bla)
#     return filtered_bla
