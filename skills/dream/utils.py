
import random
import re


######*****************************************************************************************
######*********************** LOAD PROCEDURES ***********************************************
######*****************************************************************************************


def load_data_txt(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.readlines()
    return data

######*****************************************************************************************
######*********************** STRING PROCEDURES ***********************************************
######*****************************************************************************************

def clean_text(data):
    # Text Cleanup
    sent = nltk.sent_tokenize(data)
    #remove last sentence in case not finish
    if len(sent) > 1:
        sent.pop()
    cut = TreebankWordDetokenizer().detokenize(sent)

    #remove punctuations strange characters...
    punct = """()-[]{};:'"\<>/@#$%^&*_~"""
    stripped = ''
    for char in cut:
        if char not in punct:
            stripped += char

    return stripped

def cut_extract(extract, maximum_char):
    """
    Cut a text extract if above a certain nb character
    """
    extract=" ".join(extract.split())#remove extra white space
    bound_extract=extract[:maximum_char]
    return bound_extract
    #TODO: NEED ADD self.crop_unfinished_sentence(bound_extract) ?


