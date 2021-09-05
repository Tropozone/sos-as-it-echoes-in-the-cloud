import random
import pathlib
#from pattern.en import lexeme
import time

from utils import load_makingkin, load_objects, read_event

WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]

WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-hello-socket/data/"
WAITING_TIME=5

#******************************************PARAMETERS ****************************



print("Load events and objects...")
events= load_makingkin()
print("Number different Events score:", len(events))
objects= load_objects()

print("Load dico...")
dico = {} #Dictionnary of list words
for filename in WORDS_LISTS:
    dico[filename] = [line.rstrip('\n') for line in open(WORDS_PATH+filename+'.txt')]


print("=======================================================")
print("step 1---Extract object ")
print("=======================================================")
# step 1-- pick an object
agent= random.choice(objects).strip("\n")

print("=======================================================")
print("step 2---Created a Makin kin Event Score:")
print("=======================================================")
# step 2--- pick a seed from file and replace if xxx by keyword
event_score = random.choice(events)
event=read_event(event_score, agent, dico)

print("Event: "+ "\n" + event)

print("=======================================================")
print("step 3---Possibly record what human share")
print("=======================================================")
# step 3 -- If has asked the human to share something, then wait for answer and record...
if ("tell me" in event) or ("Tell me" in event) or ("Share your thoughts with me." in event):
    #record NOW
    print("Recording Human Answer...")
elif ("Narrate me" in event) or ("I let you think about it a moment." in event):
    #TODO: Waiting time parameter ?
    #record after a lil pause to let person to think
    print("About to record Human Answer in 5 seconds")
    time.sleep(WAITING_TIME)
    print("Recording Human Answer...")
else:
    print("******Interaction Ended******")