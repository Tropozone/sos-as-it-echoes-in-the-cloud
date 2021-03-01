# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######About############
#Toucan skill
#


#***********************************************************************PARAMETERS***************************************************************************
global myName
myName="claire"
global keepThreshold
keepThreshold=50

#***********************************************************************INITIALIZATION***************************************************************************

from mycroft.skills.core import FallbackSkill
import random
import os

from mycroft_bus_client import MessageBusClient, Message

print('Setting up client to connect to a local mycroft instance')

#***********************************************************************PRELIMINARIES***************************************************************************


#***********************************************************************MAIN CLASS***************************************************************************

class toucanFallback(FallbackSkill):
    """
        A Fallback skill running some ML drits with gpt2, and a mode.
    """
    def __init__(self):
        super(toucanFallback, self).__init__(name='toucan')
        self.community=dict() # self.community[agent1] would be later list of last interactions agent1 had with her/his VA
        self.community['yuxi'] = [] # would be later list of last interactions yuxi had with her VA
        self.pathFolder="/home/chris/Dropbox/community/"
        #Get all names of community members: (have to have files nameAgent.txt in directory)
        names = [x for x in os.listdir(self.pathFolder) if x.endswith(".txt")]
        for agent in names:
            if agent==myName:
                self.community[agent] = []
                with open(self.pathFolder+ agent +".txt", "w") as f: #erase own text file before interaction
                    pass
            else:
                with open(self.pathFolder+ agent +".txt", "r") as f:#load interactions of other agents in self.community
                    self.community[agent]=[line.rstrip('\n') for line in f]


    def initialize(self):
        """
            Registers the fallback handler.
            The second Argument is the priority associated to the request.
            Lower is higher priority. But number 1-4 are bypassing other skills.
        """
        self.register_fallback(self.handle_community, 1) #Pass before every Skill
        self.client = MessageBusClient()
        self.client.run_in_thread()
            

    ##Differentiate what has been said by machine or VA>>>. Also limit on number person ?
    def share_community(nameSelf):
        for agent in self.community.keys():
            if not agent==nameSelf:#apart itself
                interaction = random.choice(self.community[agent])#pick one interaction with one agent
                print("Agent:", agent)
                print("picked up interaction:", interaction)
                message= agent + " was recently wondering the following: " + interaction
                client.emit(Message('speak', data={'utterance': message}))


    #The method that will be called to potentially handle the Utterance
    #The method implements logic to determine if the Utterance can be handled and shall output speech if itcan handle the query.
    #For now, will handle all query.
    def handle_community(self, message):
        """
            Answer by sounds
        """
        #(0) Get the human utterance
        utterance = message.data.get("utterance")                
        with open(self.pathFolder+ myName +".txt", "a") as f:#add it to own historics
            f.write(utterance + ". ")
            print("Recorded Human intervention to file.")

        #(1) Answer via message bus to the request
        message=Message("recognizer_loop:utterance", {'utterances':[utterance],'lang':'en-us'})
        #time.sleep(sleepTime) #ok Work ?
        self.client.emit(message)
        answer=message.data.get('utterance')
        if len(answer)>keepThreshold:#Differentiate human bla from VA bla >
            with open(self.pathFolder+ myName +".txt", "a") as f:#add it to own historics
                f.write(answer)
                print("Recorded VA intervention to file.")

        #(2) Pick people of the community and say pick one of their random interaction to say out loud. 
        #>>avoid repetition, removed from memory ?
        share_community(myName)

        return True

    #the Skill creator must make sure the skill handler is removed when the Skill is shutdown by the system.
    def shutdown(self):
        """
            Remove this skill from list of fallback skills.
        """
        self.remove_fallback(self.handle_community)
        super(toucanFallback, self).shutdown()

#***********************************************************************create SKILL***************************************************************************

def create_skill():
    return toucanFallback()
