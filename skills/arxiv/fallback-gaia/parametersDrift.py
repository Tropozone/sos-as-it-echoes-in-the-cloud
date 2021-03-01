# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

############## Parameters chosen for the ML Drift################

#For ML model
finetuned_ML_model= False
path_finetuned_ML_model='./workshop/models/gpt-2' 

#Length of ML Drift:
lengthDrift=200

#Number of ML Drifts:
nDrift=1

#Temperature Drift
temperature = 1.0

#Repetition Penalty drift
repetition_penalty = 2

#If decide randomize moods:
randomizeMood=True
#If not, here is the mood chosen:
currentMood='neutral'

#Possible moods for the ML Drift, with their probabilities.
#Keeping the category neutral as such, with an empty string only, enable have the possibility of a neutral mood, so unaltered ML drift.
moodSeeds=dict()
moodSeeds["engaged"]=["Yes, but I wonder if it is sustainable.", "but have you heard about climate collapse?", "Do you ask yourself what is the environmental impact of it?", "I wonder what is the ecological footprint of this?", "But I would like to know how do you face climate change.", "How do you feel in times of global warming?", "I like to think in terms of gestures for ecological care.", "Where is the green in this.", "Is climate change the elephant in the room?"]
moodSeeds["nonHuman"]=["Yes, but what about the non human?", "Yes, but can we think broader than our human pond?", "Yet, we live on a symbiotic planet.", "You know, insects are wonderful.", "Let's befriend virus and micro organisms.", "Let's focus on the living together.", "Do you feel all these multispecies entanglements?", "Let's appreciate ecological assemblages.", "Look at plants!", "Mushrooms are amazing","Animals are not here for us.", "All life evolve from the smallest life form of all, bacteria."]
moodSeeds["bleakJoy"]=["Will it last?", "Earth is wonderful. How can we deserve it?", "Isn't it an autodestructive behavior?", "Does it really matter what we think?", "Do we still care for this?", "Will humanity survive?", "Is it waste?", 'What would a societal collapse mean?', 'Shall we talk about tipping point?', "May I talk about ressource depletion?", 'May I mention planetary boundary?']
moodSeeds["neutral"]=[""]

#Randomize the Moods:
probaMood=dict()
probaMood["engaged"]=0.2
probaMood["nonHuman"]=0.2
probaMood["bleakJoy"]=0.2
probaMood["neutral"]=0.4