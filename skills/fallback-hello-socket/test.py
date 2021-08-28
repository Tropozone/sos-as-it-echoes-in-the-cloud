import random
import pathlib
#from pattern.en import lexeme

#******************************************PARAMETERS ****************************


from .utils import load_makingkin, load_objects, read_event
WORDS_PATH= str(pathlib.Path(__file__).parent.parent.absolute())+"/fallback-hello-socket/data/"


print("Load events and objects...")
events= load_makingkin()
objects= load_objects()

print("Load dico...")
dico = {} #Dictionnary of list words
for filename in WORDS_LISTS:
    dico[filename] = [line.rstrip('\n') for line in open(WORDS_PATH+filename+'.txt')]

agent= random.choice(objects).strip("\n")
print("step 1---Extracted object"+agent)


event_score = random.choice(events)

event=read_event(event_score, agent, dico) #define it.
print("***Making Kin practice****"+"\n"+ event)