import random
import pathlib
#from gingerit.gingerit import GingerIt
#gingerParser = GingerIt()  # for grammar

import nltk
from nltk import sent_tokenize
import re
from string import punctuation
import re


import os
import os.path, time
import numpy as np

######*****************************************************************************************
######*********************** AGE MEMORY ***********************************************
######*****************************************************************************************

def age_memory(folder_memory):
    ages=[]

    memory_paths=os.listdir(folder_memory+"sound/")#TODOfolder_memory

    for file_name in memory_paths:
        ages.append(os.path.getctime(folder_memory+"sound/"+file_name))
        #print("Created: %s" % time.ctime(os.path.getctime("requirements.txt")))

    return memory_paths, np.array(ages)


def forget_one_memory(folder_memory):


    #compute age element memory
    memory_paths, ages=age_memory(folder_memory)

    #compute probability: normalise such that sum is 1; here, linear ? 
    ages=ages / np.sum(ages)

    #sample file along probability
    forgotten=np.random.choice(memory_paths, 1, p=ages)

    #delete it
    os.remove(folder_memory+"sound/"+forgotten)
    

   
######*****************************************************************************************
######*********************** TEXT PROCEDURES ***********************************************
######*****************************************************************************************


WORDS_LISTS=["A", "Ad1", "Ad2", "Ad3", "V", "Vt", "P", "P0", "PR0", "PR1", "N", "N2", "Na", "S", "Sc", "Sp", "V", "Vt"]


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

def load_making_kin(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.read() #here string with '\n' in it
    #cut into list when jump lines
    sliced_data=data.split('\n\n')#TODO: check ok
    #sliced_data=sliced_data.replace('\n', "")#if single ones remaining?
    return sliced_data


def load_data_txt(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.readlines()
    return data




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
        #neue_line=gingerParser.parse(neue_line)['result']  #grammar check
        event+=neue_line+"\n"
    return event

def readUnit(unit, dico):
    if unit in WORDS_LISTS:
        neue=random.choice(dico[unit])#choose one randomly
    elif unit=="Vg" or unit=="Vtg":
        neue=random.choice(dico[unit.replace("g", "")])+"ing"
    elif "/" in unit:
        possible=unit.split("/")
        neue=readUnit(random.choice(possible), dico)
    else:
        neue=unit
    return neue

######*****************************************************************************************
######*********************** READ PROCEDURES to GENERATE STORY***********************************************
######*****************************************************************************************

def read_line(line, seeds=[], dico=None):
    sentence=""
    things=line.split(" ")
    for thg in things:
        elements=thg.split("//")#// means an or
        element=random.choice(elements)
        units=element.split("/")#/ means an AND
        for unit in units:
            bla =read_one(unit.strip(), seeds=seeds, dico=dico)
            try: 
                sentence+=" "+ bla.strip()#Strip to remove if spaces
            except:
                print(bla)
    return sentence, seeds

def read_one(unit, seeds=[], dico=None):
    #TODO: Here do not use seeds, can remove

    if unit=="PR0":
        neue, seeds=read_line(random.choice(dico[unit]), seeds=seeds, dico=dico)
    elif unit in WORDS_LISTS:
        neue=random.choice(dico[unit])#choose one randomly
    
    #VERBS
    elif unit=="Vg" or unit=="Vag" or unit=="Vtg" or unit=="V2g":
        verb=random.choice(dico[unit.replace("g", "")]).split(" ")
        neue=verb[0]+"ing" #okay as after use grammar corrector
        if len(verb)>0:
            neue+=" "+' '.join(verb[1:])

    elif unit=="Vd" or unit=="Vad" or unit=="Vtd" or unit=="V2d":
        verb=random.choice(dico[unit.replace("d", "")]).split(" ")
        neue=verb[0]+"ed" #okay as after use grammar corrector
        if len(verb)>0:
            neue+=" "+' '.join(verb[1:])
    
    #Other SPECIALS
    elif unit=="X" or unit=="Xs" or unit=="Xp":
        neue, seeds=read_line("N//Na//Na/N2//N/and/N//N2/P0/N//Pf/Na//Na/P0/N//A/A/N//A/N//Ns/N2//N2//N//A/N//Ns/N2//N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//A/N2//A/N2//A/N2", seeds=seeds, dico=dico)
    elif unit=="Y":
        neue, seeds=read_line("Y0//Y0//Y0//Y0//Y0/PR1//all/what/W//the/X//each/X//X/Wg", seeds=seeds, dico=dico)
    elif unit=="Y0":
        bla, seeds=read_line("Nf//Nfa//Nf//Nfa//Nfa//Nfa//the/A/N//the/Na/P/N//the/Na/P/X//the/Ns/N2//the/A/Ns/N2//the/X/P/X//the/X/P0/X//the/Vg/X//X/,/X/and/X//both/X/and/X", seeds=seeds, dico=dico)
    elif unit=="Wd":
        bla, seeds=read_line("Vd//Vd//Vtd/X//Vad//Vad//V2d//Vtd/Y//Vtd/Nfa", seeds=seeds, dico=dico)
    elif unit=="Wg":
        bla, seeds=read_line("Vg//Vg//Vtg/X//Vag//Vag//V2g//Vtg/Y//Vtg/Nfa", seeds=seeds, dico=dico)

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

def yake_extract_keyword(input, keyworder):

    keywords = keyworder.extract_keywords(input)
    if len(keywords)>0:
        output=keywords[0]
    else:
        output=None

    return output


def extract_keywords(input, keyworder):
    # we're looking for proper nouns, nouns, and adjectives
    pos_tag = ['PROPN', 'NOUN']#, 'ADJ']
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

    # convert list back to string
    keyword = random.choice(keywords)
    #TODO: not very good... as any word... check other keyword extractors ?, check good word etd
    #TODO: extract one key word

    return keyword




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

def load_storylines(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.read()
    storylines=data.split("\n\n")
    return storylines


# ---------------------------------------------
# --------------FILTER PROCEDURE ---------------
# ------------------------------------


def cool_judge(text, uncool_words=None, uncool_string=None, id_skill=""):
    cool=True
    
    #TODO Do more specific filters depending in skills

    #look at uncool words
    words=set(text.split())
    intersection=uncool_words & words #check intersection with uncool
    uncool_score=len(intersection)

    #look at uncool strings
    for st in uncool_string:
        if st in text:
            uncool_score+=1

    if uncool_score > 1:
        cool=False

    if id_skill=="what_if":
        #--1---test if seed is well integrated in sentence, ie not followed by capital letter, or "..." or "\n"
        stripped_text=text.lstrip()#remove space beginning
        BAD_TRANSITION=["\n", "  ", "...", ".", "?", ";", "!"]#TODO: CUrrently removing the \n too!
        #print("character look at:", stripped_text[0])
        cool_=(not(stripped_text[0].isupper())) and (not stripped_text[0] in BAD_TRANSITION)

        cool= bool(cool and cool_)

    return cool, uncool_score
