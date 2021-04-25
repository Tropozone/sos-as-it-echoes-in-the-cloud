# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

######Description############
#
# FallBack Skill where...
#
######About############
#***********************************************************************LIBRARY IMPORT***************************************************************************

###IMPORT libraries
from mycroft.messagebus.message import Message
import numpy as np
import random
import re
import json
import time
import urllib.request
import os.path 
from os import path
import pathlib


###IMPORT general
import operator
#For semantic similarity
from sematch.semantic.similarity import WordNetSimilarity
wns = WordNetSimilarity()
#For NLP and Wikipedia
import nltk
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.corpus import words, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import wikipediaapi
wikipedia = wikipediaapi.Wikipedia('en')


import requests
from bs4 import BeautifulSoup #More beautiful to see html
import urllib.parse
import lxml
import cssselect
import sys
import subprocess 
from googleapiclient.discovery import build #METHOD 1 with BUILD and google_search function for previous scraper
from configparser import ConfigParser
import spacy
from string import punctuation
from googlesearch import search
import newspaper
from urllib.error import URLError


from mycroft.audio import wait_while_speaking
from transformers import GPT2Tokenizer, GPT2LMHeadModel
#Import from other scripts
#from .scraper import surf_google
from .utils import extractWiki, extractWordnet


#***********************************************************************PARAMETERS***************************************************************************

#####PARAMETERS WHICH EVOLVE#############
#TODO: EVOLVE both With size graph: nSelf=len(list(self.graph.keys()))
global threshold_similarity
threshold_similarity=0.1 # threshold when to consider 2 concepts as similar
global n_sim_concept
n_sim_concept=30 # when compare for words in self, this is a max number look for, else slow down too much
global FIRST_RUN
FIRST_RUN=False
######OTHER PARAMETERS TO BE TUNED##############
global TEMPERATURE
TEMPERATURE=1.0 #for ML model 
global TEMPERATURE_VARIANCE
TEMPERATURE_VARIANCE=0.3 #for ML model
global MIN_CHAR_SAVE
MIN_CHAR_SAVE=40
global SEED_LENGTH#BEWARE IN OPINION LENGTH TAKEN INTO ACCOUNT!
SEED_LENGTH=80#WOULD BE DOUBLED...
global OPINION_LENGTH
OPINION_LENGTH=500
global OPINION_LENGTH_VARIANCE
OPINION_LENGTH_VARIANCE=40
global MIN_CHAR_BIT
MIN_CHAR_BIT=80
global MIN_CHAR_BLOCK
MIN_CHAR_BLOCK=200
global BOUND_CHAR_EXTRACT
BOUND_CHAR_EXTRACT=400 
global BOUND_CHAR_EXTRACT_VARIANCE
BOUND_CHAR_EXTRACT_VARIANCE=100
global OPINION_TIMEOUT
OPINION_TIMEOUT=30
#################################FIXED PARAMETERS##############
global MAX_PICK_WORD
MAX_PICK_WORD=20 # When look for words bounded to a certain number to avoid too slow.
# Amounts to bound on found wikipediable word! When search from opinion, may be bigger.
global OWN_ML_MODEL
OWN_ML_MODEL=False
global path_ML_model
path_ML_model=str(pathlib.Path(__file__).parent.absolute())+'/gpt-2'
global SAVE_BLA
SAVE_BLA=True
global timeout_start
timeout_start=0

#TODO: SCRAP LESS
#TODO: cf ERROR file desktop with google api etc
#TODO: SCRAPER RETURN SMALL TEXTS?CHECK IT PARSER
EXCLUDED=['a', 'the', 'an', 'I', 'to', 'are', 'not', 'for', 'best','you', 'they', 'she', 'he', 'if', 'me', 'on', 'is', 'are', 'them', 'why', 'per', 'out', 'with', 'by'] #exclude these words to be looked upon

#***********************************************************************PARAMETERS INITIALIZATION***************************************************************************

####LOAD CONFIG PARAMETERS
config = ConfigParser()
config.read(str(pathlib.Path(__file__).parent.absolute())+'/data/config.ini') 
my_api_key = config.get('auth', 'my_api_key')
my_cse_id = config.get('auth', 'my_cse_id')

#OTHER PARAMETERS
page = 2
start = (page - 1) * 10 + 1
min_char_bit=80
min_char_block=200
maximum_char=1000

# there may be more elements you don't want, such as "style", etc. can check
blacklist = [
'[document]',
	'noscript',
	'header',
	'footer',
	'html',
	'meta',
	'head',
	'input',
	'script',
	'button',
    'cite',
	'style',
	'title',
	'form',
    'div',
    'img',
    'body',#, ok?
	'label',#, ok?
    'hgroup'#, ok?
	'section',# ok?
    'aside',#?
    'link',
    'svg',
    'span', # ok?
    'nav',
    'g',
    'picture',
    'figure',
    'figcaption',
    'main',
    'dd',#in a description list
    'dt',#in a description list
    'ul', #, unordered list
	'li'#, list
    #'strong', ? 
	#'ol',#, ordered list
	#'a',#, hyperlink to link one page to another?

]
#***********************************************************************MAIN CLASS***************************************************************************

#***********************************************************************INITIALIZATION MYCROFT***************************************************************************

from mycroft.skills.core import FallbackSkill

class AssociativeFallback(FallbackSkill):
    """
        A Fallback skill running some associative self quest, mapping the world
    """
    def __init__(self):
        super(AssociativeFallback, self).__init__()
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.log.info("Loading GPT2")
        if OWN_ML_MODEL:
            self.model=GPT2LMHeadModel.from_pretrained(path_ML_model)
        else:
            self.model=GPT2LMHeadModel.from_pretrained("gpt2") 
        self.log.info("GPT2 Loaded")
        self.data, self.graph=dict(),dict()
        self.load_self(FIRST_RUN, MAX_PICK_WORD, threshold_similarity)#loadSelf(FIRST_RUN, MAX_PICK_WORD, threshold_similarity)
        self.state_interaction="beginning"#ELSE "opinion.."
        self.concepts, self.extracts =[], []
        
        self.human_opinion=None
        

        #INIT and LOAD THE MESSAGE LIST
        self.MSG_ASKOPINION, self.MSG_COMETOGETHER, self.MSG_COMETOGETHER3, self.MSG_INTEREST, self.MSG_LETMETHINK, self.MSG_NOINTEREST, self.MSG_SHARE, self.MSG_NOTED=[], [], [],[], [], [],[], []
        self.load_message()

    def initialize(self):
        """
            Registers the fallback handler.
            The second Argument is the priority associated to the request.
            Lower is higher priority. But number 1-4 are bypassing other skills.
            Can register several handle
        """
        #self.reload_skill=False#avoid autoreload 
        self.register_fallback(self.handle_all, 1)#1 means always trigger it here
        #self.register_fallback(self.handle_associative, 1)#1 means always trigger it here
        # #self.register_fallback(self.handle_opinion, 2)#1 means always trigger it here
        #TODO: Have two different handle one for begin_interaction, other for opinion
        #self.register_fallback(self.handle_begin_interaction, 2)#1 means always trigger it here
        #self.register_fallback(self.handle_opinion, 3)#1 means always trigger it here


    def handle_all(self, message):
        """
            to handle the utterance. 
        """
        # global timeout_start
    
        #(0) Get the human utterance
        utterance = message.data.get("utterance")

        self.log.info("=======================================================")
        self.log.info("Associative skill, handler associative triggered by " + str(utterance))

        self.concepts,self.extracts=[], [] #init back
        human_bla =str(utterance)
        self.log.info("=======================================================")
        self.log.info(f'Caught Human Bla: "{utterance}"')
        if SAVE_BLA and len(human_bla)>MIN_CHAR_SAVE:
            with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_human.txt', "a") as f:#Add it to conversation historics
                f.write(human_bla + ". ")
                self.log.info("Saved Human bla")
        
        self.log.info("=======================================================")
        self.log.info("------------------INTERACT PART 1------------------")
        self.log.info("=======================================================")
        
        
        #(1) Chris update its lifetime, save it and ask the listener to be patient.
        self.log.info("=======================================================")
        self.log.info("Step 1--Preliminaries")
        self.speak(random.choice(self.MSG_LETMETHINK))
        self.data["lifetime"]+=1

        #(2) Chris extract one or two word from utterance
        # Look at words for which exist wikipedia Page and not in self.graph nor in self.memory. 
        self.log.info("=======================================================")
        self.log.info("Step 2- Extract words from human Bla") #NO GPt2 in default core QUEST i love trees etc check why printed
        self.log.info("=======================================================")
        #OKWords, self.graph=extractWiki(human_bla, self.graph, self.data["memory"], MAX_PICK_WORD)
        #TODO ALTERNATIVE EXTRACTION, CHOOSE WHICH ONE and if so replace
        OKWords =self.extract(human_bla, MAX_PICK_WORD) #ISSUE 1
        OKWords=["pecan", "tea"]
        self.log.info("Words extracted from human blabla with wordnet:"+",".join(OKWords))

        #(3) Pick one word from this list (if not empty)
        #And look for similar concept in self graph.
        self.log.info("=======================================================")
        self.log.info("Step 3--Look for a similar self-concept")
        self.log.info("=======================================================")
        no_new_concept, if_added_concept=False, False
        if OKWords==[]:
            no_new_concept=True
            self.log.info("Did not hear any new word interesting in human blabla.")
        else:
            new_concept=random.choice(OKWords)
            self.log.info("Picked a new concept:"+new_concept)
            if_added_concept, closer_concept=self.isSelf(new_concept, n_sim_concept,threshold_similarity)
            self.log.info("Closer concept in self-graph {}. If added it to self graph: {}".format(closer_concept, if_added_concept))
            self.data["memory"].append(new_concept)#update memory and save
            # with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfdata.txt', 'w') as outfile:
            #     json.dump(self.data, outfile)
            if if_added_concept:
                self.concepts=[new_concept,closer_concept]
                # with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfgraph.txt', 'w') as outfile:# update self graph:
                #     json.dump(self.graph, outfile)
                self.speak(random.choice(self.MSG_INTEREST))
            else:
                self.log.info("Did not find a concept similar enough.")

        # has not find a new concept interesting him. Will Look about two self concepts online. or one ?
        if no_new_concept or (not if_added_concept):
            self.speak(random.choice(self.MSG_NOINTEREST))
            self.log.info("selfgraph{}".format(self.graph))
            concepts=self.graph.keys()#his self-graph
            self.concepts=[random.choice(list(concepts))] #Or pick last?
            self.concepts.append(self.concepts[0])#append with same
            while self.concepts[0]==self.concepts[1]:#so not same#TODO and bound if no new concpt
                self.concepts[1]=random.choice(list(concepts))
        
        #(4) ONLINE SURF AND SCRAP 
        self.log.info("=======================================================")
        self.log.info("Step 4--Surf online space and Scrap")
        self.log.info("=======================================================")
        #Form query and Scrap online space
        query= self.concepts[0]+ " "+ self.concepts[1]
        come_together=random.choice(self.MSG_COMETOGETHER)
        come_together=come_together.replace("xxx",self.concepts[0])
        come_together=come_together.replace("yyy",self.concepts[1])
        self.speak(come_together)
        self.log.info(come_together+ "Now surfing the online space...")
        nb_char_extract=BOUND_CHAR_EXTRACT+random.randint(-BOUND_CHAR_EXTRACT_VARIANCE, BOUND_CHAR_EXTRACT_VARIANCE)
        scraped_data, extract_surf=[], "blue whales surfing USA" # JUST FOR TEST
        # scraped_data, extract_surf=self.surf_google(query, MIN_CHAR_BIT, MIN_CHAR_BLOCK, nb_char_extract) 
    
        self.extracts=[extract_surf]
        # #save data scraped
        # with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_online.txt', "a") as f:
        #     self.log.info("Saved scraped data")
        #     for text in scraped_data:
        #         f.write(text)

        # (5) Say a bit of the article about what found online
        self.log.info("=======================================================")
        self.log.info("step 5---Share what found:")
        self.log.info("=======================================================")
        self.log.info(self.extracts[0])
        self.speak(random.choice(self.MSG_SHARE))
        self.speak(self.extracts[0])
        # wait_while_speaking()
        
        self.log.info("=======================================================")
        self.log.info("------------------ASK FOR HUMAN OPINION------------------")
        self.log.info("=======================================================")
        
        #human_opinion=self.get_response("tell me what you think")#dialog='ask.opinion')#,num_retries=1) #self.get_response # dialog="ask.opinion"#cf dialog folder ! #random.choice(self.MSG_ASKOPINION)#TODO: RETURN OK ?  #data=None, validator=None,on_fail=None, num_retries=-1 CHECK PARAM GET RESPONSE
        human_opinion="Vytas is hot as a pepper"
        self.speak("Vytas is hot as a pepper")
        
        self.log.info("=======================================================")
        self.log.info("Current human opinion saved:{}".format(human_opinion))
  
        if human_opinion is not None:#do not need both, check new utterance not same than old one...
            self.log.info("=======================================================")
            self.log.info("==============YOUHOUUUU WE ARE HERE=====================")
            self.log.info("=======================================================")
            human_opinion = str(human_opinion)
            if human_opinion is not None:
                self.log.info("Caught human opinion:{}".format(human_opinion))
                self.speak(random.choice(self.MSG_NOTED))
                #save it
                # if SAVE_BLA and len(human_opinion)>MIN_CHAR_SAVE:
                #     with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_human.txt', "a") as f:#Add it to conversation historics
                #         f.write(human_opinion + ". ")
                #         self.log.info("Saved Human opinion")
        
                self.log.info("=======================================================")
                self.log.info("------------------INTERACT PART 2 FROM INTERACT PART 1------------------")
                self.log.info("=======================================================")
                self.interact_part2(human_opinion)
            else:
                self.log.info("Timeout. Human had no opinion. Ready for New Interaction Loop")
        else:
            self.log.info("Timeout. Human had no opinion. Ready for New Interaction Loop")
                    
        return True #IF HANDLED...


    def interact_part2(self, human_bla):
        """
            End of an interaction loop with an human. 
            At the end of this loop, the VA is listening still for a possible other loop.
        """
        self.log.info("=======================================================")
        self.log.info("step 7----Extract new concept from human opinion")
        self.log.info("=======================================================")

        #(7) Pick a new concept from human opinion: #TODO: could compare procedures
        #OKWords, self.graph=extractWiki(human_bla, self.graph, self.data["memory"], MAX_PICK_WORD)
        OKWords=self.extract(human_bla, MAX_PICK_WORD)
        self.log.info("Words extracted from human opinion with wordnet:"+",".join(OKWords))

        if len(OKWords)==0:#CASE A where empty: AS SUCH STILL WOULD GIVE HIS OPINION 
            self.log.info("Did not find anything interesting in this opinion.")
        
        else: #CASE B where found new concept
            new_concept=random.choice(OKWords)
            self.concepts.append(new_concept)
            #TODO: SHOULD ALSO TAKE A CONCEPT WHICH IS SIMILAR ENOUGH TEHRE?>>>>
            self.log.info("Picked a new concept:"+ new_concept)
            come_together=random.choice(self.MSG_COMETOGETHER3)
            come_together=come_together.replace("zzz",new_concept)
            come_together=come_together.replace("xxx",self.concepts[0])
            come_together=come_together.replace("yyy",self.concepts[1])
            self.speak(come_together)
            #Update self.memory with this concept and save data
            self.data["memory"].append(self.concepts[2])
            # with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfdata.txt', 'w') as outfile:
            #     json.dump(self.data, outfile)

            self.log.info("=======================================================")
            self.log.info("step 8----New Surf & Scrap.")
            self.log.info("=======================================================")
            #(9) New surf& scrap with these 3 concepts. and Save
            new_query= self.concepts[2] + " "+ self.concepts[0]+ " "+ self.concepts[1]
            self.log.info("Now surfing the online space looking for {} .".format(new_query))
            scraped_data_2, extract_surf=[], "rotten tomatoes"
            nb_char_extract=int(BOUND_CHAR_EXTRACT+BOUND_CHAR_EXTRACT_VARIANCE*random.uniform(-1,1))
            #scraped_data_2, extract_surf=self.surf_google(new_query, MIN_CHAR_BIT, MIN_CHAR_BLOCK, nb_char_extract)
            self.extracts.append(extract_surf)#IF NOT EMPTY...
            # with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_online.txt', "a") as f:#save data
            #     self.log.info("Save scraped data...")
            #     for text in scraped_data_2:
            #         f.write(text)
            self.log.info("=======================================================")
            self.log.info("step 9----Share what found online ")
            self.log.info("=======================================================")

            #(10) Say a bit of the article about what found online
            self.speak(random.choice(self.MSG_SHARE))
            self.speak(self.extracts[1])
        
        self.log.info("=======================================================")
        self.log.info("step 10----Give his own opinion")
        self.log.info("=======================================================")

        #(11) Give his own opinion: generate it with gpt-2
        if len(self.extracts)>1:
            seed=self.extracts[0][:SEED_LENGTH]+ " " + self.extracts[1][:SEED_LENGTH]
        else:
            seed=self.extracts[0][:SEED_LENGTH]
        context= seed+"\n"+"I think"#Or add sth?
        length_output=OPINION_LENGTH + random.randint(-OPINION_LENGTH_VARIANCE, +OPINION_LENGTH_VARIANCE)
        temperature_gpt2=TEMPERATURE+TEMPERATURE_VARIANCE*random.uniform(-1,1)
        self.log.info("Context to seed VA opinion:"+context)
        #TODO: gpt2 break but no i dont understand
        # #opinion = self.gpt2_text_generation(context, length_output, temperature_gpt2) 
        #opinion = opinion.replace(seed, "") #TODO: OK? REMOVED CONTEXT ? CHECK WITHOUT...
        #self.log.info("Opinion VA:"+opinion)

        self.log.info("Thanks for this interaction.")
        #self.log.info("listening...")
       

    def load_self(self, first_run, max_pick_word, threshold_similarity):
        """
            The VA loads his self.graph, memory, lifetime, as last saved. Or build it if first time.
        """
        if first_run:
            self.log.info("Hatching self in process...")
            self.graph, self.data, description=hatchSelf(max_pick_word, threshold_similarity)
        else:
            self.log.info("Loading self in process...")
            with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfgraph.txt', 'r') as json_file:
                self.graph = json.load(json_file)
            with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfdata.txt', "r") as json_file:
                self.data=json.load(json_file)
            self.log.info("I am here. My lifetime is {} interactions".format(self.data["lifetime"]))
        self.log.info("selfgraph {}".format(self.graph))
        self.log.info("selfgraph {}".format(self.graph.keys()))


    def semanticSimilarity(self, word1, word2):
        """
        Compute the semantic similarity between two words, as define by the library wnsm, and return score. Of course this is subjective. If word1 cmposed word: average similarity of its both elements.
        """
        score=0
        splitWord=word1.split()
            #Case of concepts made of several words
        if len(splitWord)>1:
            for elt in splitWord:
                score+=self.semanticSimilarity(elt, word2)
            score/=len(splitWord)
        else:#word1 has 1 component
            splitWord2=word2.split()
            if len(splitWord2)>1:#case word2 has 2 component or more
                for elt in splitWord2:#Else could take the max but would be non symmetic
                    score+=wns.word_similarity(word1, elt, 'li')
                score/=len(splitWord2)
            else:#case both concepts have only 1 word
                score=wns.word_similarity(word1, word2, 'li')
        #self.log.info('Similarity score between ' + word1 + ' and ' + word2 +": " + str(score))

        return score

    def isSelf(self, word, n_sim_concept, threshold_similarity):
        """
        Check if a word (not belonging to his self) is related to his self.graph.
        And pick a similar concept (any above the threshold of similarity).
        """
        nSelf=len(list(self.graph.keys()))
        #CASE in case graph becomes too big:
        indices=random.sample(range(0, nSelf), min(n_sim_concept, nSelf)) #Generate random list of indices where will look for
        self.graph[word]=[0,dict()]   #Add entry to dictionary for now
        ifConnected=False
        maxSim=0
        possible_simWord=[]
        simWord=""
        #Check similarity with other concepts in Self
        for i, wordSelf in enumerate(list(self.graph.keys())):
            if i in indices:
                similarity_score= self.semanticSimilarity(word,wordSelf)
                if similarity_score>threshold_similarity:
                    possible_simWord.append(wordSelf)
                    self.graph[word][1][wordSelf]=similarity_score#Add a connection if related enough.
                    self.graph[wordSelf][1][word]=similarity_score#Symmetric
                    ifConnected=True
                    #if similarity_score>maxSim:#IF WANT MAX SIMILARITY
                    #    maxSim=similarity_score
                    #    simWord=wordSelf
        
        #Conclude if related
        if not ifConnected: #Not related, ie no connection with SelfConcept was above a fixed threshold.
            del self.graph[word] #delete entry from SelfGraph therefore
        else: # if related
            #Pick a word above threshold similarity:
            simWord=random.choice(possible_simWord)
            self.graph[word][0]=maxSim*self.graph[simWord][0] #adjust the weight of the node
        return ifConnected, simWord



    def load_message(self):
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_askopinion.txt', 'r') as f:
            self.MSG_ASKOPINION = [line.rstrip('\n') for line in f]
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_cometogether.txt', 'r') as f:
            self.MSG_COMETOGETHER= [line.rstrip('\n') for line in f]
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_cometogether3.txt', 'r') as f:
            self.MSG_COMETOGETHER3 = [line.rstrip('\n') for line in f]
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_interest.txt', 'r') as f:
            self.MSG_INTEREST = [line.rstrip('\n') for line in f]
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_nointerest.txt', 'r') as f:
            self.MSG_NOINTEREST = [line.rstrip('\n') for line in f]
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_share.txt', 'r') as f:
            self.MSG_SHARE = [line.rstrip('\n') for line in f]
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_noted.txt', 'r') as f:
            self.MSG_NOTED = [line.rstrip('\n') for line in f]
        with open(str(pathlib.Path(__file__).parent.absolute())+'/messages/message_letmethink.txt', 'r') as f:
            self.MSG_LETMETHINK = [line.rstrip('\n') for line in f]
        



    def extract(self, blabla, max_pick_word):
        """
            Extract wordnet nouns (or proper noun) from a blabla, which are not on the memory, nor on the selGraph, nor in EXCLUDED
            TAKE ALSO WIKIPEDIA STILL
            Self Quest bounded to a maximum of max_pick_word to avoid too long wait. Beware, of found wikipediable word!
            Beware of upper or lower letters which can create conflicts.
            #TODO: Test Edge Cases and memorz
        
        """
        OKWordnet=[]
        wn_lemmas = set(wordnet.all_lemma_names())#TODO: SHALL LOAD IT ONLY ONCE???
        if len(blabla)==0: #empty
            print("No new words to grow from.")
        else:
            counter=0#count words added
            for word, pos in nltk.pos_tag(word_tokenize(blabla)):
                if counter<max_pick_word:#Stop once has enough words
                    if pos in ['NN', 'NNS','NNP']:
                        if not word.isupper():#To avoid turning words like AI lower case. Else turn to lower case. Ex: donald_trump
                            word=word.lower()
                        #TODO: Need Lemmatizer to avoid words which have same roots?
                        if ((word in wn_lemmas) or (wikipedia.page(word).exists())) and not (word in OKWordnet):
                            if word in self.graph.keys():#Word is there, augment its weight.
                                self.graph[word][0]=self.graph[word][0]*1.1
                            else: #TODO: Shall exclude memory ?
                                OKWordnet.append(word)
                                counter+=1
            #Special case of duo words for wikipedia, such as global_warming https://en.wikipedia.org/wiki/Global_warming
            #FOR THESE, use wikipedia!
            wordList=blabla.split()#then need word.strip(string.punctuation)
            token_list=nltk.pos_tag(word_tokenize(blabla))
            counter=0
            for token1, token2 in zip(token_list, token_list[1:]):#Consecutive token
                word1, pos1=token1
                word2, token2=token2
                if counter<max_pick_word and len(word1)>1 and len(word2)>1 and (word1 not in EXCLUDED) and (word2 not in EXCLUDED):#Stop once has enough words
                    if not word1.isupper(): #lower letter unless fully upper letter:check for proper noun
                        word1=word1.lower()
                    if not word2.isupper(): #lower letter unless fully upper letter
                        word2=word2.lower()
                    duo=word1+" "+word2
                    if wikipedia.page(duo).exists() and not (duo in OKWordnet):
                        if duo in self.graph.keys():
                            self.graph[duo][0]=self.graph[duo][0]*1.1
                        else:
                            OKWordnet.append(duo)
                            counter+=1
            print("New words to learn from", OKWordnet)
        return OKWordnet


#**********************************************************************SCRAPER**************************************************************************


    def surf_google(self,query, min_char_bit, min_char_block, maximum_char):
        """
        Main procedure to scrap google result of a query: will scrap the urls first, then the texts of the articles, parse the text and choose
        one of these extracts.

        """
        #TODO: If none result satisfying criteria (length etc), relaunch further pages? OR TAKE SMALLER TEXT
        ###(0) Scrap data from Google Search
        print("=======================================================")
        print("Scraping Google results and get urls")
        data = self.google_search(query, api_key=my_api_key, cse_id=my_cse_id)
        #retrieve_google_url(query, num_links=8)#TODO other scraper but issue?
        #print(data)
        ###(1) Get urls
        urls = self.get_urls(data)
        print("=======================================================")
        print("Getting urls")
        #print(urls)
        ###(2) Extract texts part
        print("=======================================================")
        print("Extracting the texts")
        scraped_data=self.parse_article(urls) #extract_text(urls, min_char_bit, min_char_block)
        #print(extracts)
        ###(3) Choose one extract
        print("=======================================================")
        print("Choosing one Extract")
        #TODO: Better choice there
        chosen_extract=self.choose_extract(scraped_data)
        #print(chosen_extract)
        ###(4) Cut extract
        print("=======================================================")
        print("Final Extract")
        final_extract=self.cut_extract(chosen_extract, maximum_char)
        print(final_extract)

        return scraped_data, final_extract

    #*******************************************************************PROCEDURES**************************************************************************

    def google_search(self,search_term, api_key, cse_id, **kwargs):
        """
            Use Google Search API to get Google results over a query
            Old procedure!
        """
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        #print(res)
        return res #python dictionarry ok?

    def get_urls(self,data):
        """
            Parse the data obtained from Google API to get the urls of these articles.
        """
        search_items = data.get("items")
        urls=[]
        for i, search_item in enumerate(search_items, start=1):
            title = search_item.get("title")
            link = search_item.get("link")
            urls.append(link)
        return urls

    def retrieve_google_url(self,query, num_links=8):
        #TODO: INCORPORATE ALTERNATIVE GOOGLE RETRIEVAL instead of above  two procedures?
        # query search terms on google
        # tld: top level domain, in our case "google.com"
        # lang: search language
        # num: how many links we should obtain
        # stop: after how many links to stop (needed otherwise keeps going?!)
        # pause: if needing multiple results, put at least '2' (2s) to avoid being blocked)
        try:
            online_search = search(query, tld='com', lang='en', num=num_links, stop=num_links, pause=2)
        except URLError:
            pass
        website_urls = []
        for link in online_search:
            website_urls.append(link)
        # returns a list of links
        return website_urls


    def parse_one_article(self,url):
        article=""
        try:
            # locate website
            article = newspaper.Article(url)
            # download website
            print('Downloading ' + url)
            article.download()
            article_downloaded = True
            # parse .html to normal text
            article.parse()
            # analyze text with natural language processing
            #article.nlp()
            print("==================Article Scraped=====================================")
            print(article)
            return article.text
        except requests.exceptions.RequestException:
            print("Article download failed.")
            return ""


    def parse_article(self,urls):
        """
        New procedure to extract text from articles.
        """
        articles=[]
        count=0
        for url in urls:
            if count<4:#only 4 working links
                try:
                    article=self.parse_one_article(url)
                    if article is not None and not article=="":
                        articles.append(article)
                        count+=1
                except:
                    continue

        return articles


    def choose_extract(self,extracts):
        """
        Choose an extract of text among several. 
        First filter it by a "is cool" procedure, to select only nice texts. (todo, cf. below)
        Then, pick up randomly among the 3 longer cool extracts
        """
        cool_extracts=[]
        cool_length=[]
        for extract in extracts:
            #if isCool(extract):
            cool_extracts.append(extract)
            cool_length.append(len(extract))
        #Get 3 longer cool extracts
        nb_pick=min(3, len(cool_extracts))#Will pick 3 if nb cool exctracts >=3
        longer_extracts=sorted(zip(cool_length, cool_extracts), reverse=True)[:nb_pick]#as sorted by default order from first argument when tuple
        #Pick one randomly
        chosen_extract=random.choice(longer_extracts)
        return chosen_extract[1]#text part (first element is score)

    def isCool(self,text):
        """
        Has to try to judge if a text extract is cool.
        #TODO: Do this procedure. if too much space between lines, bad, paragraph condensed are better or if too many special characters may be bad etc.
        #notably if too much of : </div>
        #For now temporary: count <> and if bigger than 20, say not cool. But need to implement filter_html first
        """
        #nb_bad_stuff=text.count("<")
        return True #bool(nb_bad_stuff<4)#CHECK THIS




    def crop_unfinished_sentence(text):
        """
        Remove last unfinished bit from text. 
        """
        #SELECT FROM THE RIGHT rindex s[s.rindex('-')+1:]  
        stuff= re.split(r'(?<=[^A-Z].[.!?]) +(?=[A-Z])', text)

        new_text=""
        for i in range(len(stuff)):
            if i<len(stuff)-1:
                new_text+= " " + stuff[i]
            elif stuff[i][-1] in [".", ":", "?", "!", ";"]:#only if last character ounctuation keep
                new_text+= " " + stuff[i]

        return new_text

    def cut_extract(extract, maximum_char):
        """
        Cut a text extract if above a certain nb character
        """
        bound_extract=extract[:maximum_char]
        return  crop_unfinished_sentence(bound_extract)

#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#**************





    #the Skill creator must make sure the skill handler is removed when the Skill is shutdown by the system.
    def shutdown(self):
        """
            Remove this skill from list of fallback skills.
        """
        self.remove_fallback(self.handle_all)
        #self.remove_fallback(self.handle_opinion)
        #self.remove_fallback(self.handle_associative)
        #self.remove_fallback(self.handle_beginning)
        super(AssociativeFallback, self).shutdown()


    def gpt2_text_generation(self, context, length_output, TEMPERATURE): 
        """
            One ML drift with gpt-2, with a context. Printed and said by VA.
            With some stochasticity
        """
        process = self.tokenizer.encode(context, return_tensors = "pt")
        generator = self.model.generate(process, max_length = length_output, TEMPERATURE = TEMPERATURE, repetition_penalty = 2.0, do_sample=True, top_k=20)
        drift = self.tokenizer.decode(generator.tolist()[0])
        self.speak(drift)
        return drift




#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#***********************************************************************create SKILL***************************************************************************

def create_skill():
    return AssociativeFallback()

#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#************************************************************************************************************************************
#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#**********************************************************************EXTRACT**************************************************************************


#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#**************************************************************************************************************************************************
#***********************************************************************OLD STUFF**************************************************************************





    # def interact_part1(self, human_bla):
    #     """
    #         Interaction with the VA.
    #     """

    #     global timeout_start
        
    #     #(1) Chris update its lifetime, save it and ask the listener to be patient.
    #     self.log.info("=======================================================")
    #     self.log.info("Step 1--Preliminaries")
    #     self.speak(random.choice(self.MSG_LETMETHINK))
    #     self.data["lifetime"]+=1

    #     #(2) Chris extract one or two word from utterance
    #     # Look at words for which exist wikipedia Page and not in self.graph nor in self.memory. 
    #     self.log.info("=======================================================")
    #     self.log.info("step 2- Extract words from humam Bla") #NO GPt2 in default core QUEST i love trees etc check why printed
    #     #OKWords, self.graph=extractWiki(human_bla, self.graph, self.data["memory"], MAX_PICK_WORD)
    #     #TODO ALTERNATIVE EXTRACTION, CHOOSE WHICH ONE and if so replace
    #     OKWords, self.graph=extract(human_bla, self.graph, self.data["memory"], MAX_PICK_WORD)
    #     #self.log.info("Words extracted from human blabla with wiki:", OKWords)
    #     self.log.info("Words extracted from human blabla with wordnet:"+",".join(OKWords))


    #     #(3) Pick one word from this list (if not empty)
    #     #And look for similar concept in self graph.
    #     self.log.info("=======================================================")
    #     self.log.info("Step 3--Look for a similar self-concept...or pick his own")
    #     no_new_concept, if_added_concept=False, False
    #     if OKWords==[]:
    #         no_new_concept=True
    #         self.log.info("Did not hear any new word interesting in human blabla.")
    #     else:
    #         new_concept=random.choice(OKWords)
    #         self.log.info("Picked a new concept:"+new_concept)
    #         self.graph, if_added_concept, closer_concept=isSelf(self.graph, new_concept, n_sim_concept,threshold_similarity)
    #         self.log.info("Closer concept in self-graph {}. If added it to self graph: {}".format(closer_concept, if_added_concept))
    #         self.data["memory"].append(new_concept)#update memory and save
    #         with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfdata.txt', 'w') as outfile:
    #             json.dump(self.data, outfile)
    #         if if_added_concept:
    #             self.concepts=[new_concept,closer_concept]
    #             with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfgraph.txt', 'w') as outfile:# update self graph:
    #                 json.dump(self.graph, outfile)
    #             self.speak(random.choice(self.MSG_INTEREST))
    #         else:
    #             self.log.info("Did not find a concept similar enough.")
    #     #Has not find a new concept interesting him. Will Look about two self concepts online. or one ?
    #     if no_new_concept or (not if_added_concept):
    #         self.speak(random.choice(self.MSG_NOINTEREST))
    #         concepts=self.graph.keys()#his self-graph
    #         self.concepts=[random.choice(list(concepts))] #Or pick last?
    #         self.concepts.append(self.concepts[0])#append with same
    #         while self.concepts[0]==self.concepts[1]:#so not same#TODO and bound if no new concpt
    #             self.concepts[1]=random.choice(list(concepts))
        

    #     #(4) ONLINE SURF AND SCRAP 
    #     self.log.info("=======================================================")
    #     self.log.info("step 4--Surf online space and Scrap")
    #     #Form query and Scrap online space
    #     query= self.concepts[0]+ " "+ self.concepts[1]
    #     come_together=random.choice(self.MSG_COMETOGETHER)
    #     come_together=come_together.replace("xxx",self.concepts[0])
    #     come_together=come_together.replace("yyy",self.concepts[1])
    #     self.speak(come_together)
    #     self.log.info(come_together+ "\n"+ "Now surfing the online space...")
    #     nb_char_extract=BOUND_CHAR_EXTRACT+random.randint(-BOUND_CHAR_EXTRACT_VARIANCE, BOUND_CHAR_EXTRACT_VARIANCE)
    #     #scraped_data, extract=[], "blue whales surfing USA "
    #     scraped_data, extract_surf=surf_google(query, MIN_CHAR_BIT, MIN_CHAR_BLOCK, nb_char_extract) 
    #     #all_data_scraped="////////////////////////////////////////////".join(scraped_data)
    #     #self.log.info(all_data_scraped)
    #     self.extracts=[extract_surf]

    #     #SAVE DATA THAT WAS SCRAPED 
    #     with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_online.txt', "a") as f:
    #         self.log.info("Saved scraped data")
    #         for text in scraped_data:
    #             f.write(text)

    #     #(6) Say a bit of the article about what found online
    #     self.log.info("=======================================================")
    #     self.log.info("step 5---Share what found:")
    #     self.log.info(self.extracts[0])
    #     self.speak(random.choice(self.MSG_SHARE))
    #     self.speak(self.extracts[0])
        

    # def handle_associative(self, message):
    #     """
    #         to handle the utterance. 
    #     """
    #     global timeout_start
    
    #     #(0) Get the human utterance
    #     utterance = message.data.get("utterance")
    #     self.log.info("-----------CHECK HANDLER ASSOCIATIVE-------------")

    #     if (utterance is not None) and (self.state_interaction=="beginning") and (self.human_opinion is None):#TODO: SECOND CONDITION NEEDED ?
    #         self.log.info("=======================================================")
    #         self.log.info("Associative skill, handler associative triggered by " + str(utterance))
    #         #(1) LOOK IF TIMEOUT OPINION : #TODO:NOT NEEDED A PRIORI
    #         #timeout=time.time()-timeout_start
    #         #self.log.info(timeout)
    #         #self.log.info(timeout_start)
    #         #self.log.info(self.state_interaction)
    #         #if self.state_interaction=="opinion" and timeout>OPINION_TIMEOUT:
    #         #    self.state_interaction="beginning"
    #         #    self.log.info("Timeout. Human had no opinion. Launch New Interaction Loop")

    #         ###(2) INITIALISATION: if beginning....
    #         #if self.state_interaction=="beginning":
    #         self.concepts,self.extracts=[], [] #init back
    #         human_bla =str(utterance) #str(utterance[0])#TODO: ISSUE want all utterance ?
    #         self.log.info("=======================================================")
    #         self.log.info(f'Caught Human Bla: "{utterance}"')
    #         #self.log.info(f'Extract human said "{str(utterance[0])}"')
    #         if SAVE_BLA and len(human_bla)>MIN_CHAR_SAVE:
    #             with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_human.txt', "a") as f:#Add it to conversation historics
    #                 f.write(human_bla + ". ")
    #                 self.log.info("Saved Human bla")
    #         #LAUNCH INTERACT LOOP PART 1
    #         self.state_interaction="opinion"#in prevention
    #         self.log.info("=======================================================")
    #         self.log.info("------------------INTERACT PART 1------------------")
    #         self.log.info("=======================================================")
    #         self.interact_part1(human_bla)
    #         self.state_interaction="opinion"#once done
            
            
    #         self.log.info("=======================================================")
    #         self.log.info("------------------ASK FOR HUMAN OPINION------------------")
    #         self.log.info("=======================================================")
    #         #timeout_start=time.time()
    #         wait_while_speaking()
    #         self.state_interaction="opinion"
    #         human_opinion=self.get_response("What do you think?",num_retries=1) #dialog="ask.opinion"#cf dialog folder ! #random.choice(self.MSG_ASKOPINION)#TODO: RETURN OK ?  #data=None, validator=None,on_fail=None, num_retries=-1 CHECK PARAM GET RESPONSE
    #         self.log.info(self.state_interaction)
    #         #check if empty or none ?
    #         # if human_opinion is not None and not human_opinion=="":
    #         #     self.log.info("Caught human opinion "+ human_opinion)
    #         #     self.speak(random.choice(self.MSG_NOTED))
    #         #     if SAVE_BLA and len(human_opinion)>MIN_CHAR_SAVE:
    #         #         with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_human.txt', "a") as f:#Add it to conversation historics
    #         #             f.write(human_opinion + ". ")
    #         #             self.log.info("Saved Human opinion")
    #         #     #LAUNCH INTERACT LOOP PART 2
    #         #     self.interact_part2(human_opinion)
    #         #timeout_start=time.time() OLD STUFFD REMOVE
    #         #self.log.info("Waiting for human opinion (or anything)...")

    #         # #Possible New Utterance 
    #         #new_utterance = message.data.get("utterance")
    #         self.log.info("=======================================================")
    #         self.log.info("Current human opinion saved:{}".format(human_opinion))
    #         #self.log.info("Current utterance:{}".format(new_utterance))
    #         #new_utterance = message.data.get("utterance")
    #         if human_opinion is not None:#do not need both, check new utterance not same than old one...
    #             self.log.info("=======================================================")
    #             self.log.info("==============NON EMPTY OPINION=====================")
    #             human_opinion = str(human_opinion) #self.human_opinion)
    #             if human_opinion is not None:
    #                 self.log.info("Caught human opinion:" + human_opinion)
    #                 self.speak(random.choice(self.MSG_NOTED))
    #                 if SAVE_BLA and len(human_opinion)>MIN_CHAR_SAVE:
    #                     with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_human.txt', "a") as f:#Add it to conversation historics
    #                         f.write(human_opinion + ". ")
    #                         self.log.info("Saved Human opinion")
    #                 #LAUNCH INTERACT LOOP PART 2
    #                 self.log.info("=======================================================")
    #                 self.log.info("------------------INTERACT PART 2 FROM INTERACT PART 1------------------")
    #                 self.log.info("=======================================================")
    #                 self.interact_part2(human_opinion)
    #             else:
    #                 self.log.info("Timeout. Human had no opinion. Ready for New Interaction Loop")
    #         else:
    #             self.log.info("Timeout. Human had no opinion. Ready for New Interaction Loop")
            
    #         self.state_interaction="beginning"#ELSE "opinion.."
    #         self.human_opinion=None
            
    #         return True #IF HANDLED...
    #     else:
    #         return False
            


    # def handle_opinion(self, message):
    #     """
    #         to handle the utterance for second part interaction. 
    #     """
    #     global timeout_start
    #     #(0) Get the human utterance
    #     utterance = message.data.get("utterance")
    #     self.log.info("=======================================================")
    #     self.log.info("-----------CHECK HANDLER OPINION---------------")
    #     if self.state_interaction=="opinion" and utterance is not None:#Can utterance be none?
    #         self.log.info("=======================================================")
    #         self.log.info("Associative skill, Handler Opinion triggered by " + str(utterance))
    #         human_opinion = str(utterance) #str(utterance[0])
    #         if human_opinion is not None:#NEEDED?
    #             self.log.info("Caught human opinion:" + human_opinion)
    #             self.speak(random.choice(self.MSG_NOTED))
    #             if SAVE_BLA and len(human_opinion)>MIN_CHAR_SAVE:
    #                 with open(str(pathlib.Path(__file__).parent.absolute())+'/data/heard_human.txt', "a") as f:#Add it to conversation historics
    #                     f.write(human_opinion + ". ")
    #                     self.log.info("Saved Human opinion")
    #             #LAUNCH INTERACT LOOP PART 2
    #             self.log.info("=======================================================")
    #             self.log.info("------------------INTERACT PART 2------------------")
    #             self.log.info("=======================================================")
    #             self.interact_part2(human_opinion)
    #         else:
    #             self.log.info("Timeout. Human had no opinion. Ready for New Interaction Loop")
    #         self.state_interaction="beginning"
    #         return True
    #     else:
    #         self.log.info("Timeout. Human had no opinion. Ready for New Interaction Loop")
    #         #reinit state
    #         self.state_interaction="beginning"
    #         return False #IF HANDLED...

