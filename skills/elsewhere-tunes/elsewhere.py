#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""

Keep running in loop in background
- Either Say something about another node information
- Or Play something has recorded prior
"""

# =============================================================================
# TODO
# =============================================================================
# NOW 
# TODO: Informatipn about other node  LIVE or NOT LIVE ? GOOGÖE?>>>>>
# TODO: More things that trigger spontaneously like tgis.
# TODO: Share folder collective memory: dropbox ?

# LATER
# TODO: Trigger when mycroft recognize a sound lound enough? or what?


# =============================================================================
# Initialisation
# =============================================================================


# imports
from mycroft_bus_client import MessageBusClient, Message
from mycroft.skills.audioservice import AudioService
import random
from time import sleep
import os
from playsound import playsound

# path
dir_path = os.path.dirname(os.path.realpath(__file__))
memory_folder=dir_path +"/memory/"

# import Message Bus client to communicate with Mycroft's guts
print("Setting up connection to Mycroft client")
client = MessageBusClient()

# =============================================================================
# Procedure
# =============================================================================


def nobody_asked_this(message):
    # human_said = message.data.get('utterances')[0]

    # step 1: pick sound from collective memory
    sound_path=random.choice(os.listdir(memory_folder))

    # step 2: wait, in case skill triggered
    sleep(15)
    
    # step 3: extract keywords from the phrase and add search_context
    message="Listen."#TODO: Shall add a message for transition?
    client.emit(Message('speak', data={'utterance': message}))

    # step 4: playback the sound
    playsound(sound_path)


# =============================================================================
# Run in Loop:
# =============================================================================


#TODO: Currently being trigger 5 seconds after each message, but could be linked to external event or sound
# waits for messages from Mycroft via websocket
client.on('recognizer_loop:utterance', nobody_asked_this)

# basically runs this script in a loop
client.run_forever()
