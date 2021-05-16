# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

#TODO: or structure of a fabulation instead, query only gpt2 for words? 
#TODO: or use generator without ML?
#TODO: Rethink which sentences work well!


import random
import transformers 
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import pathlib
import re

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

my_ML_model_path = str(pathlib.Path(__file__).parent.absolute())+'/gpt2_model'  # path to your fine tuned model

# Maximum length of the generated answer, counted in characters and spaces.
length_drift = 80
# Increase the likelihood of high probability words by lowering the temperature (aka make it sound more 'normal')
temperature = 0.9
# Repetition penalty. In general makes sentences shorter and reduces repetition of words an punctuation.
repetition_penalty = 1.4


def cut_one_sentence(generated):
    output = re.split('.|!|/?', generated)[0]+"."#\! #|?
    return output
print(cut_one_sentence("hello ! How are you?"))#TODO: ISSUE


#Load model and tokenizer
print("Loading own gpt2 model")
#model=GPT2LMHeadModel.from_pretrained(my_ML_model_path)#TO TEST! but beware, need change where is gpt2 path...
model=GPT2LMHeadModel.from_pretrained("gpt2")
print("Loading tokenizer")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")


#*****************************UTILS **********

#TODO COMMON FOR DIFFERENT SKILLS!
def extract_keywords(input):
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

def load_whatif():
    path_folder=str(pathlib.Path(__file__).parent.absolute())
    #print(str(pathlib.Path(__file__).parent.absolute()))
    return load_data_txt("/whatif.txt", path_folder=path_folder)

def load_data_txt(filename, path_folder="", mode="r"):
    """
    for messages in skill, load txt
    """
    with open(path_folder+filename,  mode=mode) as f:
        data = f.readlines()
    return data

keyword="storm"
whatif = load_whatif()

#SEVERAL GPT2 gene to test some answers:
seed = random.choice(whatif)
seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
print("gpt2 generation from "+ seed)
encoded_context = tokenizer.encode(seed, return_tensors="pt")
generated = model.generate(encoded_context, max_length = length_drift , temperature= temperature, repetition_penalty = repetition_penalty, do_sample=True, top_k=10)
response = tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
print("cut response", cut_one_sentence(response))

seed = random.choice(whatif)
seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
print("gpt2 generation from "+ seed)
encoded_context = tokenizer.encode(seed, return_tensors="pt")
generated = model.generate(encoded_context, max_length = length_drift , temperature= temperature, repetition_penalty = repetition_penalty, do_sample=True, top_k=10)
response = tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
print("response", response)

seed = random.choice(whatif)
seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
print("gpt2 generation from "+ seed)
encoded_context = tokenizer.encode(seed, return_tensors="pt")
generated = model.generate(encoded_context, max_length = length_drift , temperature= temperature, repetition_penalty = repetition_penalty, do_sample=True, top_k=10)
response = tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
print("response", response)

print("*****Done!*******") 