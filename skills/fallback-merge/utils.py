import random
import pathlib
from gingerit.gingerit import GingerIt
gingerParser = GingerIt()  # for grammar

import nltk
from nltk import sent_tokenize
import re
from string import punctuation
import re

WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]


alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences



######*****************************************************************************************
######*********************** LOAD PROCEDURES ***********************************************
######*****************************************************************************************

def load_data_kin(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.read() #here string with '\n' in it
    #cut into list when jump lines
    sliced_data=data.split('\n\n')#TODO: check ok
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



######*****************************************************************************************
######*********************** READ EVENT PROCEDURES ***********************************************
######*****************************************************************************************


def read_event(event_score, agent, dico):
    event_lines=event_score.split("/n")
    event=""
    for line in event_lines:
        neue_line=""
        #in case there is a // in the line: choose one of them
        possible=line.split("//")
        line=random.choice(possible)
        line=line.replace("  ", " ")#in case double space by accident.
        line=line.replace("xxx", agent)
        units=line.split(" ")#split into units
        for unit in units:
            neue_unit=readUnit(unit, dico)
            neue_line+=neue_unit+" "
        neue_line=neue_line.replace(" .", ".")
        neue_line=neue_line.replace(" ,", ",")
        neue_line=gingerParser.parse(neue_line)['result']  #grammar check
        event+=neue_line+"\n"
    return event

def readUnit(unit, dico):
    if unit in WORDS_LISTS:
        neue=random.choice(dico[unit])#choose one randomly
    elif unit=="Vg" or unit=="Vtg":
        neue=random.choice(dico[unit.replace("g", "")])
    elif "/" in unit:
        possible=unit.split("/")
        neue=readUnit(random.choice(possible), dico)
    else:
        neue=unit
    return neue

######*****************************************************************************************
######*********************** LOAD PROCEDURES ***********************************************
######*****************************************************************************************


# ---------------------------------------------
# --------------STRING PROCEDURES---------------
# ------------------------------------


def ending_with_punct(data):
    punct = [";", ":", "!", ".", "?"]
    # Text Cleanup
    sent = nltk.sent_tokenize(data)
    #remove last sentence in case not finished
    if len(sent) > 1:
        if sent[-1][-1] not in punct:
            sent.pop()
    final=" ".join(sent)
    return final

def ending_with_punct_manual(data):
    punct = [";", ":", "!", ".", "?"]
    idx_last=0
    #if not 
    #    str.endswith(data)
    for sign in punct:
        idx_temp=data.rfind(sign) #last occurence sign on the righ
        idx_last=max(idx_last,idx_temp)

    if idx_last==0:#case no punctuation
        return data
    else: 
        return data[:idx_last+1]

def remove_context(question, generated):
    # remove the question text from the generated answer
    output = generated.replace(question, '')
    # remove incomplete sencentes at the end, if any.
    output = output.rsplit('.', 1)[0] + '.'
    return output


def cut_one_sentence(generated):
    output = re.split('.|?|!', generated)[0]+"."
    return output


def extract_keywords(input, keyworder):
    # we're looking for proper nouns, nouns, and adjectives
    pos_tag = ['PROPN', 'NOUN', 'ADJ']
    # tokenize and store input
    phrase = keyworder(input.lower())
    keywords = []
    # for each tokenized word
    for token in phrase:
        # if word is a proper noun, noun, or adjective;
        if token.pos_ in pos_tag:
            # and if NOT a stop word or NOT punctuation
            if token.text not in keyworder.Defaults.stop_words or token.text not in punctuation:
                keywords.append(token.text)
    # convert list back to string
    key_string = " ".join(keywords)

    return key_string



# ---------------------------------------------
# --------------LOAD PROCEDURE ---------------
# ------------------------------------


def load_data_txt(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.readlines()
    return data
    
# ---------------------------------------------
# --------------FILTER PROCEDURE ---------------
# ------------------------------------


def cool_judgement_enter_the_weird(text, uncool_set):
    text_set=set(text.split()) #turn into set
    cool=True
    intersection=uncool_set & text_set #check intersection with uncool
    #print(intersection)

    if len(intersection)>=1:
        cool=False

    #TODO Filter if proper nound or Regenerate ?
    #TODO: More filtering?

    return cool

def cool_judgement_what_if(seed, text, uncool_set):
    
    #--1---test if seed is well integrated in sentence, ie not followed by capital letter, or "..." or "\n"
    stripped_text=text.replace(seed, "")
    stripped_text=stripped_text.lstrip()#remove space beginning
    BAD_TRANSITION=["\n", "...", ".", "?", ";", "!"]#TODO: CUrrently removing the \n too!
    #print("character look at:", stripped_text[0])
    cool1=(not(stripped_text[0].isupper())) and (not stripped_text[0] in BAD_TRANSITION)

    #--2--- test if "he", "she", names, Dialogue#TODO: Keep this ?
    #cool2=cool_judgement_enter_the_weird(text, uncool_set)

    #TODO: more filtering

    return cool1 #bool(cool1 and cool2)