#***********************************************************************INITIALIZATION***************************************************************************
#!/usr/bin/env python3 # to use in terminal

###IMPORT libraries
import time
import numpy as np
import random
import json
import re
import nltk #For NLP
from nltk.corpus import words, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
import urllib.request
from nltk import word_tokenize, sent_tokenize, pos_tag

attractors=['climate change', 'climate change','climate change','global warming', 'degrowth', 'pollution', 'climate collapse', 'survivalism', 'carbon footprint', 'environmental impact', 'societal collapse', 'waste', 'ecological footprint', 'ressource depletion', 'fragile Earth', 'Earth tipping point', 'sustainable']

#To execute Node.js from python
from Naked.toolshed.shell import execute_js, muterun_js

#For scrap text
import requests
from bs4 import BeautifulSoup #More beautiful to see html
import urllib.parse
import lxml
import cssselect
import sys

# there may be more elements you don't want, such as "style", etc. can check
blacklist = ['[document]','noscript','header','footer','html','meta','head','input','script','picture','time','mark','button','form', 'svg','cite', 'figure', 'link','em', 'nav', 'strong', 'clippath',
	'style',
	'title',#, okremove ? as keep apart
    'h2',
    'i',# okremove ? emphasis...
	'form',#, okremove ?
	'label',#, okremove ?
	'span', #, okremove ?
	'img',#, okremove ?
	'section',#, okremove ?
	'ul', #, unordered list
	'li',#, okremove ?
	'ol',#, ordered list
	'a',#, hyperlink to link one page to another
	'body',#, okremove ?
	'hgroup'#, okremove ?
]


#**********************************************************************PRELIMINARIES***************************************************************************

def extractNouns(blabla):
    """
       Extract one noun from a text
       Todo: Could be also couple of noun or noun+ adj etc>>>. Also, ideally should be main noun
    """
    nouns=[]
    text = word_tokenize(blabla)
    taggedWords=nltk.pos_tag(text)
    for (word, tag) in taggedWords:
        if tag=='NN' or tag=='NNS':
            nouns.append(word)
    return nouns

#DOnly above threshold char and line. Here string as input !
def extractMainBlocks(blabla, mChar, nLine): #>>implement with nLine
    blocks=blabla.split("\n \n \n")
    extract=""
    for block in blocks:
        if len(block) > mChar:
            extract+=block+" \n"
        print(len(block))
    return extract

#DOnly above threshold word LIST as INPUT. mchar dont work as sentences cut strangely sometimes by p !!!
def extractBlocks(blocks, mChar):
    extract=""
    for block in blocks:
        if len(block) > mChar:
            extract+=block+" \n"
    return extract


#**********************************************************************SCRAP ONLINE DATA***************************************************************************
def climateCheck(nouns):
    textPage=""
    addQuery=" "+attractors[0]#random.choice(attractors)
    queries=[n + addQuery for n in nouns]
    #query=noun+ " "+attractors[0] #" climate change" here but could add others
    #Record query in json file:
    with open('./data/query.json', 'w') as json_file:
        json.dump(queries, json_file)
    #The execute_js() function returns a boolean value for the success (or lack thereof) of the JavaScript. This is based upon the zero (success) or non-zero (failure) exit code returned from the JavaScript to the Python code.
    success = execute_js('scrapOneQuery.js')
    return success

def scrapsPage(url):
    textPage = ''
    result = requests.get(url)
    html_page = result.content # or .text ?
    soup = BeautifulSoup(html_page, 'html.parser')
    #print(soup.prettify()[:10000])
    title= '{} '.format(soup.find_all("title")[0].text)
    print(title)
    text = soup.find_all(text=True) #here keep only the text already ?
    #Here see what have in text, as text is going to give us some information we don’t want: remove some type in black list.
    # print(soup.title.text) TITle
    #for link in soup.find_all("a"): get just an attribute then can do .format(link.text) or .format(link.href) or .format(link.title)
    # TO do : REMOVE WHITE SPACES blank Lines: ie cut blocks before !
#{'p', 'h1', 'i', 'div'', h2'}#USUALLY: p is the good tag or div! but also 'h2', 'h3','h1 maybbe...
    #Can ad if reach footer etc then suppress even if p or cut text end because issue,,,
    print(set([t.parent.name for t in text]))
    blocks=[]
    foundTitle=False
    for t in text:
        print('{} '.format(t.parent.name))
        print('{} '.format(t))
        if t.parent.name not in blacklist: #only keep things after title, or actually after h1 do not always work...???
            blocks.append('{} '.format(t))
            #print('{} '.format(t.parent.name))
            #print('{} '.format(t))
    		#textPage += '{} '.format(t) # but this suppress the jump of lines 
        if t.parent.name=='title' and not foundTitle:
            foundTitle=True
            print('{} '.format(t))
            blocks=[]#reinit
    output= extractBlocks(blocks, 50)
    #output= extractMainBlocks(textPage, 400, 3) #Could add also number line>>
    print(output)
    return title, output

#Take maximum scrapping result
def scrapFew(nouns, minText):
    success=climateCheck(nouns)
    if success:
        with open('./data/links.json', "r") as f: #read links dict
            links=json.load(f)
    maxLength=0
    maxText=""
    maxTitle=""
    maxNoun=""
    for noun in nouns:
        title, output=scrapOne(noun, links[noun +" "+attractors[0]], minText)
        if len(output)>maxLength:
            maxLength=len(output)
            maxText=output
            maxTitle=title
            maxNoun=noun
    with open('./data/outputSearch.txt', "w") as f: #read links
        f.write(maxTitle+maxText)
    return maxNoun, maxTitle, maxText

def scrapOne(noun, links, minText):
    title=""
    output=""
    count=0
    while count<len(links) and len(output)<minText:
        title, output=scrapsPage(links[count])
        count+=1
    return title,output

# with open('./data/links.txt', "r") as f: #read links
# 	links=f.readlines()
# scrapsPage(links[1])
# Link 3 abstracts in span
scrapFew(["avocado", "petrol"], 200)

