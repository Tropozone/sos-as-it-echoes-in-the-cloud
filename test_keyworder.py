


from string import punctuation
import random
####TEST KEYWORD EXTRACTOR
#import spacy
#spacy.load("en_core_web_sm")

#keyworder = spacy.load("en_core_web_sm")
text="I wish I would be perforated by sun rays a every minute yess"

#keyword= extract_keywords(text, keyworder)

#doc = keyworder(text)
#print(doc.ents)

# text="Are you blue"
def yake_extract_keyword(input, keyworder):

    keywords = keyworder.extract_keywords(input)
    if len(keywords)>0:
        output=keywords[0][0]
    else:
        output=""

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

import time

####TEST KEYWORD EXTRACTOR 1
import yake
keyworder=yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=3, features=None)
start = time.time()
keyword= yake_extract_keyword(text, keyworder)
end = time.time()
print(keyword)
print(start-end)

####TEST KEYWORD EXTRACTOR 2
import spacy
keyworder2 = spacy.load("en_core_web_sm") #NOTE: temporarily desactivated for raspberry pi
start = time.time()
keyword= extract_keywords(text, keyworder2)
end = time.time()
print(keyword)
print(start-end)


