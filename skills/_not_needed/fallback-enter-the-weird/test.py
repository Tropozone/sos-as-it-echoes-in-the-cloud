# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

#*************************************INITIALIZATION***************

import random
import transformers 
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import pathlib

# simply cleans up machine-generated text
def clean_text(origin, generated):
    # remove origin text from the generated answer
    output = generated.replace(origin, '')
    # remove incomplete sencentes at the end, if any.
    output = output.rsplit('.', 1)[0] + '.'
    return output



my_ML_model_path = str(pathlib.Path(__file__).parent.absolute())+'/gpt2_model'  # path to your fine tuned model

# Maximum length of the generated answer, counted in characters and spaces.
length_drift = 10
var_drift=20
# Increase the likelihood of high probability words by lowering the temperature (aka make it sound more 'normal')
temperature = 0.9
# Repetition penalty. In general makes sentences shorter and reduces repetition of words an punctuation.
repetition_penalty = 1.4

#Load model and tokenizer
print("Loading own gpt2 model")
model=GPT2LMHeadModel.from_pretrained(my_ML_model_path)
#model=GPT2LMHeadModel.from_pretrained("gpt2")
print("Loading tokenizer")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

seed="Egg shell are"

print("encoding token")
encoded_context= tokenizer.encode(context, return_tensors = "pt")
print("gpt2 generation....")
max_length= length_drift+random.randint(-var_length,var_length)
generated = model.generate(encoded_context, max_length = max_length, temperature= temperature, repetition_penalty = repetition_penalty, do_sample=True, top_k=10)
print("Decoding generated text...")
drift = tokenizer.decode(generated.tolist()[0])
print("gpt2 Response: "+ drift)

cleaned_drift=clean_text(seed, drift)

print("cleaned gpt2 Response: ", cleaned_drift)
print("*****Done!*******") 
