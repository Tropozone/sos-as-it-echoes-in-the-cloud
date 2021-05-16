import random
import pathlib
#from pattern.en import lexeme

#******************************************PARAMETERS ****************************


words_path= str(pathlib.Path(__file__).parent.parent.absolute())+'/fallback-hello-socket/data/'
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
    sliced_data=data.split('\n\n')#TODO: check ok
    return sliced_data

def load_objects():
    path_folder=str(pathlib.Path(__file__).parent.absolute())
    #print(str(pathlib.Path(__file__).parent.absolute()))
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
    #print(str(pathlib.Path(__file__).parent.absolute()))
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


print("Load events and objects...")
events= load_makingkin()
objects= load_objects()

print("Load dico...")
##CREATE DICTIONARY
filenames=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]
dico = {} #Dictionnary of list words
for filename in filenames:
    dico[filename] = [line.rstrip('\n') for line in open(words_path+filename+'.txt')]

agent= random.choice(objects).strip("\n")
print("step 1---Extracted object"+agent)


event_score = random.choice(events)

event=read_event(event_score, agent, dico) #define it.
print("***Making Kin practice****"+"\n"+ event)