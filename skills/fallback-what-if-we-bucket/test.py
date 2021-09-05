# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

import random
import transformers 
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import pathlib
import re

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

from utils import extract_keywords, load_whatif, cut_one_sentence, clean_text

my_ML_model_path = str(pathlib.Path(__file__).parent.absolute())+'/gpt2_model'  # path to your fine tuned model

# --------------PARAMETERS to TUNE---------------------
MAX_LENGTH = 80
TEMPERATURE = 0.8
REPETITION_PENALTY = 1.4

settings=dict()
settings.setdefault("repetition_penalty", REPETITION_PENALTY)  
settings.setdefault("temperature", TEMPERATURE)  # recording channels (1 = mono)
settings.setdefault("max_length", MAX_LENGTH)

#Load model and tokenizer
print("Loading own gpt2 model")
#model=GPT2LMHeadModel.from_pretrained(my_ML_model_path)#TO TEST! but beware, need change where is gpt2 path...
model=GPT2LMHeadModel.from_pretrained("distilgpt2")
print("Loading tokenizer")
tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")


#*****************************UTILS **********


keyword="storm"
whatif = load_whatif()

#SEVERAL GPT2 gene to test some answers:
print("*******************************")
seed = random.choice(whatif)
seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
print("gpt2 generation from "+ seed)
encoded_context = tokenizer.encode(seed, return_tensors="pt")
generated = model.generate(encoded_context, max_length = settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=10)
response = tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
print("response", response)
print("*******************************")

print("*******************************")
seed = random.choice(whatif)
seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
print("gpt2 generation from "+ seed)
encoded_context = tokenizer.encode(seed, return_tensors="pt")
generated = model.generate(encoded_context, max_length = settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=10)
response = tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
print("response", response)
print("*******************************")

print("*******************************")
seed = random.choice(whatif)
seed=seed.replace("xxx", keyword)#replace xxx (if exist w/ keyword)
print("gpt2 generation from "+ seed)
encoded_context = tokenizer.encode(seed, return_tensors="pt")
generated = model.generate(encoded_context, max_length = settings["max_length"], temperature=settings["temperature"], repetition_penalty = settings["repetition_penalty"], do_sample=True, top_k=10)
response = tokenizer.decode(generated.tolist()[0], clean_up_tokenization_spaces=True, skip_special_tokens=True)
print("response", response)
print("*******************************")
print("*****End!*******") 