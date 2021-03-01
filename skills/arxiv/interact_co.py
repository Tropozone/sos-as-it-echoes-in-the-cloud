# !/usr/local/bin/python3
# -*- coding: utf-8 -*-


######Description############
#
# Main Script for the Interaction between you and your voice assistant
#
######About############
# This script was created for the workshop Unfamiliar Virtual Convenient - Growing your Voice Assistant
# led by Vytautas Jankauskas and Claire Glanois through School of Machines, Make & believe, in spring 2020.
#
# Feel free to tune, or reshape it according to your project.


#***********************************************************************PARAMETERS***************************************************************************
keepThreshold=50
ifShare=True#if share your own interaction with other member of the community

community=dict()
community['yuxi'] = [] # would be later list of last interactions yuxi had with her VA
community['guillaume'] = []


#***********************************************************************INITIALIZATION***************************************************************************

###IMPORT libraries
import fire
import numpy as np
import random
import re

#Import for Mycroft
import os.path
from os import path
from mycroft_bus_client import MessageBusClient, Message
from mycroft.audio import wait_while_speaking

# Initialise Mycroft Message Bus
client = MessageBusClient()

print("\n")
print('Setting up client to connect to a local mycroft instance. ')
print("\n")
print("=======================================================")
print('Human, please say something after you see ~~Connected~~')
print("=======================================================")
print("\n")

#Load last interaction other members of the commmunity
with open('/home/chris/Dropbox/community/yuxi.txt', "r") as f:
    community['yuxi']=[line.rstrip('\n') for line in f]
with open('/home/chris/Dropbox/community/guillaume.txt', "r") as f:
    community['guillaume']=[line.rstrip('\n') for line in f]
#Empty claire File >>>
#with open('./workshop/community/claire.txt', "w") as f: #Put back
    #f.write("")


#Global variables
global humanBla
humanBla=""
global VABla
VABla=""
global savedBla
savedBla=""

#***********************************************************************PRELIMINARIES*************************************************************************


##Differentiate what has been said by machine or VA>>>
def shareCommunity():
    for agent in community.keys():
        interaction = random.choice(community[agent])#pick one interaction with one agent
        print("Agent:", agent)
        print("picked up interaction:", interaction)
        message= agent + " was recently wondering the following: " + interaction
        client.emit(Message('speak', data={'utterance': message}))



def record_human_utterance(message, ifShare=ifShare):
    """
        Record utterance of human to a string.
    """
    humanBla = str(message.data.get('utterances')[0])
    print(f'Human said "{humanBla}"')

    if ifShare:
        with open('/home/chris/Dropbox/community/claire.txt', "a") as f:#Add it to conversation historics
            f.write(humanBla + ". ")
            print("Recorded Human")


def record_VA_utterance(message, ifShare=ifShare):
    """
        Record utterance of what the VA say
    """
    VABla = message.data.get('utterance')
    print('VA said "{}"'.format(VABla))

    shareCommunity()

    if ifShare and len(VABla)>keepThreshold:
        with open('/home/chris/Dropbox/community/claire.txt', "a") as f:#Add it to conversation historics
            f.write(VABla + ". ")
            print("Recorded VA")



#***********************************************************************MAIN INTERACTION*************************************************************************


def interactLoop():
    """
        Interaction with the VA
    """
    #(0) Catch what the human is saying
    client.on('recognizer_loop:utterance', record_human_utterance)

    #(1) Catch what the VA is answering
    client.on('speak', record_VA_utterance) #recording the VA bla is given as a handler for speak message.
    ## wait while Mycroft is speaking
    ## wait_while_speaking()

    client.run_forever()





#***********************************************************************END*************************************************************************

#Direct Launch Interact
if __name__ == '__main__':
    fire.Fire(interactLoop)
