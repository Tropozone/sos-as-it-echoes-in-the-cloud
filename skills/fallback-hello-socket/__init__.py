# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############

#TODO: not a FALLBACK?, spontaneous trigger...
#TODO: some events require conversatioN!
# # #TODO: use regex for reading text file ? ore 
#https://github.com/galaxykate/tracery
#https://github.com/aparrish/pytracery

#********************************************INITIALIZATION***********


from mycroft.skills.core import FallbackSkill
import random
import pathlib
#******************************************PARAMETERS ****************************


words_path= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-hello-socket/data/"

WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]

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
    sliced_data=data.split('\n \n')#TODO: check ok
    #sliced_data=sliced_data.replace('\n', "")#if single ones remaining?
    return sliced_data

def load_objects():
    path_folder=str(pathlib.Path(__file__).parent.absolute())
    #self.log.info(str(pathlib.Path(__file__).parent.absolute()))
    return load_data_txt("/objects.txt", path_folder=path_folder)

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
    return load_data_kin("/yoko.txt", path_folder=path_folder)


def read_event(event_score, agent, dico):
    event_lines=event_score.split("/n")
    event=""
    for line in event_lines:
        neue_line=""
        line=line.replace("  ", " ")#in case double space by accident.
        line=line.replace("xxx", agent)
        units=line.split(" ")#split into units
        for unit in units:
            neue_unit=readUnit(unit, dico)
            neue_line+=neue_unit+" "
        neue_line=neue_line.replace(" .", ".")
        neue_line=neue_line.replace(" ,", ",")
        event+=neue_line+"\n"
    #TODO: more variation, generations...
    return event

def readUnit(unit, dico):
    if unit in WORDS_LISTS:
        neue=random.choice(dico[unit])#choose one randomly
   # elif unit=="Vg":
        #TODO
        # verb=random.choice(wordsDic["V"])
        # neue=lexeme(verb[0])[2]
        # if len(verb)>0:
        #     neue+=' '.join(verb[1:]        
    else:
        neue=unit
    return neue

#******************************MAIN PROCEDURE**********



class HelloSocketFallback(FallbackSkill):

    def __init__(self):
        super(HelloSocketFallback, self).__init__(name='Hello Socket Fallback Skill')

        # load events and objects
        self.log.info("Load events and objects...")
        self.events= load_makingkin()
        self.objects= load_objects()
        
        self.log.info("Load dictionary...")
        dico = {} #Dictionnary of list words
        for filename in WORDS_LISTS:
            dico[filename] = [line.rstrip('\n') for line in open(words_path+filename+'.txt')]

    def initialize(self):
        """
            Registers the fallback handler.
            The second argument is the priority associated to the request;
            Because there are several fallback skills available, priority helps
            to tell Mycroft how 'sensitively' this particular skill should be triggered.
            Lower number means higher priority, however number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_make_kin, 6) #NOTE: change priority of other fallback when want to test so no conflict?

    def handle_make_kin(self, message):
        """
            Make Kin practices
        """
        # step-0 Obtain what the human said
        utterance = message.data.get("utterance")#TODO: here not utterance...

        # step 1-- pick an object
        agent= random.choice(self.objects).strip("\n")
        self.log.info("=======================================================")
        self.log.info("step 1---Extracted object "+agent)
        self.log.info("=======================================================")

        # step 2--- pick a seed from file and replace if xxx by keyword
        event_score = random.choice(self.events)
        event=read_event(event_score, agent, self.dico) #define it.
        self.log.info("=======================================================")
        self.log.info("step 2---Created a Makin kin Event Score:"+"\n"+event)
        self.log.info("=======================================================")

        # step 3 --Speak generated text aloud
        self.speak(event)

        #TODO: wait for comment about it?
        #TODO: More interactive with VA, has to record it to send to network>>>

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

    