import random
import pathlib
#from gingerit.gingerit import GingerIt
#gingerParser = GingerIt()  # for grammar

import nltk
from nltk import sent_tokenize
import re
from string import punctuation
import re



#Main sound library used, #cf https://github.com/carlthome/python-audio-effects
from pysndfx import AudioEffectsChain 
#Second library in use currently, for overlay
from pydub import AudioSegment 

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
######*********************** SOUND PROCEDURES ***********************************************
######*****************************************************************************************

EFFECTS={
    "lowpass": 0.3,
    "highpass": 0.3,
    "reverb": 0.4,
    "phaser": 0.2,
    "chorus": 0.3,
    "overdrive": 0.2,
    "pitch": 0.2,
    "tempo": 0.3,
    "tremolo": 0.3,
    "reverse": 0.4

}

def random_distortion(infile, outfile, infile2=None,  proba_overlay=0.8, min_gain_drop=4, max_gain_drop=8, max_length=0):
    """
    infile: adress of sound file 
    proba_overlay: probability of overlaying original sound with distored (when want to still hear...)
    gain: gain applied to distorted sound if overlay
    max_length: cut to a max length if not 0

    """

    fx = AudioEffectsChain()

    if random.random()<EFFECTS["lowpass"]:
        # lowshelf(gain=-20.0, frequency=100, slope=0.5) # "lowshelf takes 3 parameters: a signed number for gain or attenuation in dB, filter frequency in Hz and slope (default=0.5, maximum=1.0)."
        freq=random.randint(100, 500)
        print("Lowpass at {}".format(freq))
        fx=fx.lowshelf(frequency=freq)
       
    if random.random()<EFFECTS["highpass"]:
        #highshelf(self, gain=-20.0, frequency=3000, slope=0.5) 
        freq=random.randint(1000, 4000)
        print("Highpass at {}".format(freq))
        fx=fx.highshelf(frequency=freq)
    
    if random.random()<EFFECTS["reverb"]:
        # reverb(self, reverberance=50, hf_damping=50, room_scale=100, stereo_depth=100, pre_delay=20, wet_gain=0, wet_only=False) #reverb takes 7 parameters: reverberance, high-freqnency damping, room scale, stereo depth, pre-delay, wet gain and wet only (True orFalse)"""
        room_scale=random.randint(20, 100)
        reverberance=random.randint(20, 50)
        print("Reverb")
        fx=fx.reverb(reverberance=reverberance, room_scale=room_scale)

    if random.random()<EFFECTS["phaser"]:
        speed=random.randrange(0, 2)
        print("Phaser")
        #    phaser(self, gain_in=0.9, gain_out=0.8, delay=1, decay=0.25, speed=2, triangular=False)# phaser takes 6 parameters: input gain (max 1.0), output gain (max 1.0), delay, decay, speed and LFO shape=trianglar (which must be set to True or False)"""
        fx=fx.phaser(speed=speed)

    #TODO issue with decays form
    # if random.random()<EFFECTS["chorus"]:
    #     print("Chorus")
    #     #    chorus(self, gain_in, gain_out, decays)
    #     fx=fx.chorus(gain_in=0.2, gain_out=0.2, decays=[[2], [10], [6]])


    if random.random()<EFFECTS["overdrive"]:
        print("Overdrive")
        #    overdrive(self, gain=20, colour=20)  # overdrive takes 2 parameters: gain in dB and colour which effects the character of the distortion effet. Both have a default value of 20. TODO - changing color does not seem to have an audible effect
        fx=fx.overdrive()

    # if random.random()<EFFECTS["pitch"]:#TODO: Add
    #     print("Pitch")
    #     #    pitch(self, shift, use_tree=False, segment=82, search=14.68, overlap=12) #pitch takes 4 parameters: user_tree (True or False), segment, search and overlap."""
    #     fx=fx.pitch()


    if random.random()<EFFECTS["tempo"]:
        factor=random.randrange(0, 2)
        factor=max(factor, 0.1)
        print("Tempo")
        #tempo(self, factor, use_tree=False, opt_flag=None, segment=82, search=14.68, overlap=12)#tempo takes 6 parameters: factor, use tree (True or False), option flag, segment, search and overlap). This effect changes the duration of the sound without modifying pitch.
        fx=fx.tempo(factor=factor)

    if random.random()<EFFECTS["tremolo"]:
        freq=random.randint(500,2500)
        depth=random.randint(0,60)
        print("Tremolo")
        #    tremolo(self, freq, depth=40)#tremolo takes two parameters: frequency and depth (max 100)"""
        fx=fx.tremolo(freq=freq, depth=depth)
    
    if random.random()<EFFECTS["reverse"]:
        print("Reverse")
        fx=fx.reverse()

    # Apply phaser and reverb directly to an audio file.
    fx(infile, outfile)

    if random.random()<proba_overlay:
        print("Overlay")
        original = AudioSegment.from_file(infile)
        distorted = AudioSegment.from_file(outfile)
        length = min(len(original), len(distorted))
        if max_length>0:
            length=min(length, max_length)
        original=original-2
        min_gain_drop=max(min_gain_drop, 2)
        max_gain_drop=max(min_gain_drop+1, max_gain_drop)
        combined = original[:length].overlay(distorted[:length]- random.randrange(min_gain_drop, max_gain_drop), loop=True)
        combined.export(outfile, format='wav')
    elif max_length>0 and len(distorted)>max_length:
        print("Cut file to max length")
        distorted = AudioSegment.from_file(outfile)
        combined = distorted[:max_length]-2#also attenuate a bit
        combined.export(outfile, format='wav')
        
######*****************************************************************************************
######*********************** TEXT PROCEDURES ***********************************************
######*****************************************************************************************


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
    return load_data_txt("/data/objects.txt", path_folder=path_folder)

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
    return load_data_kin("/data/yoko.txt", path_folder=path_folder)



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
        neue=random.choice(dico[unit.replace("g", "")])
    elif "/" in unit:
        possible=unit.split("/")
        neue=readUnit(random.choice(possible), dico)
    else:
        neue=unit
    return neue

######*****************************************************************************************
######*********************** READ PROCEDURES to GENERATE STORY***********************************************
######*****************************************************************************************

def read(line, seeds=[], dico=None):
    sentence=""
    things=line.split(" ")
    for thg in things:
        elements=thg.split("//")#// means an or
        element=random.choice(elements)
        units=element.split("/")#/ means an AND
        for unit in units:
            bla, seeds=readUnit(unit.strip(), seeds=seeds, dico=dico)
            try: 
                sentence+=" "+ bla.strip()#Strip to remove if spaces
            except:
                print(bla)
    return sentence, seeds

def readUnit(unit, seeds=[], dico=None):
    #-----may use seeds----
    if unit in ["S", "N","N2", "Ns", "N2s", "N2p", "Np"]:
        #NOTE: here dont caree about plural !
        if len(seeds)>0:
            bla=seeds[0]
            seeds.pop(0)
        else:
            unit=unit.replace("s","")
            unit=unit.replace("p","")
            bla, w=read(random.choice(dico[unit]), dico=dico)
    #---------composite structures
    elif unit=="X" or unit=="Xs" or unit=="Xp":
        #has removed Duo//Duoa// compoared to old haiku
        bla, seeds=read("N//Na//Na/N2//N/and/N//N2/P0/N//Pf/Na//Na/P0/N//A/A/N//A/N//Ns/N2//N2//N//A/N//Ns/N2//N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//N//A/N//Ns/N2//A/N2//A/N2//A/N2", seeds=seeds, dico=dico)
    elif unit=="X+":#to add to "the X ""...Ex: which...
        bla, seeds=read("whose/Na/W0//which/W//better/Vtd/that/W0//than/Vtd//which/have/been/PR1a//which/have/been/PR1//which/W0//the/X/PR1//thought/as/Nfa//we/are/trying/to/Vt//that/W0//that/we/allow/to/W0//we/are/Vtg//that/Ad2/W0//that/V+//that/have/become/A//that/do/not/W0//that/you/should/not/Vt", seeds=seeds, dico=dico)
    elif unit=="Y":
        bla, seeds=read("Y0//Y0//Y0//Y0//Y0/PR1//Y0/PR1a//all/what/W//the/X/X+//everyone/X+//anything/X+//each/X/X+//X/Wg", seeds=seeds, dico=dico)
    elif unit=="Y0":
        bla, seeds=read("Nf//Nfa//Nf//Nfa//Nfa//Nfa//the/A/N//the/Na/P/N//the/Na/P/X//the/Ns/N2//the/A/Ns/N2//the/X/P/X//the/X/P0/X//the/Vg/X//X/,/X/and/X//both/X/and/X//the/X/that/W0", seeds=seeds, dico=dico)
    elif unit=="W":
        bla, seeds=read("W0//W0//W0//W0//W0//V+//V+//V+//could/W0//should/W0//would/W0//could/V+//Ad2/W0//Ad2/W0", seeds=seeds, dico=dico)
    elif unit=="W0":
        bla, seeds=read("V//V//Vt/X//Va//Va//V2//Vt/Y//Vt/Nfa", seeds=seeds, dico=dico)
    elif unit=="WA":
        bla, seeds=read("Ad2/V//Ad2/Vt/X//V/Ad3//Vt/X/Ad3", seeds=seeds, dico=dico)
    elif unit=="Wd":
        bla, seeds=read("Vd//Vd//Vtd/X//Vad//Vad//V2d//Vtd/Y//Vtd/Nfa", seeds=seeds, dico=dico)
    elif unit=="Wg":
        bla, seeds=read("Vg//Vg//Vtg/X//Vag//Vag//V2g//Vtg/Y//Vtg/Nfa", seeds=seeds, dico=dico)
    elif unit=="XWg": #NEED ?
        bla, seeds=read("X/Wg", seeds=seeds, dico=dico)
    elif unit=="PRO":
        bla, seeds=read("S/V//S/Vt/X//X/V//N/Vt/X//S/V/P0/X", seeds=seeds, dico=dico)

    #---not affecting seeds
    elif unit=="A":#removed A0//A0/A0//A0/A0//A0/A0/A0//
        bla, w=read("A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//A0//Ad2/A0//A0//Ad2/A0//Ad2/A0//still/A0//A0/yet/A0//yet/A0//soon/A0//somehow/A0//already/A0", dico=dico)
    elif unit=="A0":
        bla, w=read(random.choice(dico["A"]), dico=dico)
    elif unit=="PR10":
        bla, w=read(random.choice(dico["PR1"]), dico=dico)
    elif unit=="PR1":
        bla, w=read("PR10//PR10//PR10//PR10//PR10//PR10//Ad1/PR10//Ad2/PR10//Ad2/PR10", dico=dico)
    #--------verbs
    elif unit=="Vd" or unit=="Vad" or unit=="Vtd" or unit=="V2d":
        verb=random.choice(dico[unit.replace("d", "")]).split(" ")
        bla=verb[0]+"ed" #okay as after use grammar corrector
        if len(verb)>0:
            bla+=" "+' '.join(verb[1:])
        #NOTE: Previous library Python issue ? 3.6 or 2.7... find replacement...
        # bla=lexeme(verb[0])[4] #past
    elif unit=="Vag" or unit=="Vg" or unit=="Vtg" or  unit=="V2g":
        verb=random.choice(dico[unit.replace("g", "")]).split(" ")
        bla=verb[0]+"ing" #okay as after use grammar corrector
        if len(verb)>0:
            bla+=" "+' '.join(verb[1:])
        ## bla=lexeme(verb[0])[2] #present participe
        # #conjugate(verb[0], tense = "present",  person = 3,  number = "singular",  mood = "indicative", aspect = "progressive",negated = False)
    #----remaining stuff
    elif unit in dico.keys():
        bla, w=read(random.choice(dico[unit]), dico=dico)

    else:#mean just a word
        bla=unit

    return bla, seeds



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