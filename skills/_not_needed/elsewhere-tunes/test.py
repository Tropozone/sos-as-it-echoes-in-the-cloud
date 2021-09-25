#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# =============================================================================
# Initialisation
# =============================================================================


# imports
import random
from time import sleep
import os
from playsound import playsound

# path
dir_path = os.path.dirname(os.path.realpath(__file__))
memory_folder=dir_path +"/memory/"

# =============================================================================
# Procedure
# =============================================================================


def nobody_asked_this():
    # human_said = message.data.get('utterances')[0]
    
    #just sanity check
    print(os.listdir(memory_folder))

    # step 1: pick sound from collective memory
    sound_path=random.choice(os.listdir(memory_folder))
   
    # step 2: wait, in case skill triggered
    sleep(5)
    
    # step 3: extract keywords from the phrase and add search_context
    message="Listen."#TODO: Shall add a message for transition?
    print(message)

    # step 4: playback the sound
    playsound(memory_folder+sound_path)


# =============================================================================
# Run in Loop:
# =============================================================================


while True:
    nobody_asked_this()
