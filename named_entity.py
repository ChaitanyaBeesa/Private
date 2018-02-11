# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 20:07:29 2018

@author: test
"""
### Summarizers source - https://github.com/miso-belica/sumy


import os
import pandas as pd
#import spacy
import en_core_web_sm # Spacy default package
import re
#from collections import Counter

nlp = en_core_web_sm.load()

#file_name = 'sample_text.csv'
file_name = 'NewHireArticles02_02_2018_BusinessWire.csv'
#file_name = 'NewHireArticles02_02_2018_PRNews.csv'
samp_text = pd.read_csv(file_name) 

#print(samp_text.columns)

#### Spacy Named Entity recognition ######
def ner_extract(document):
    
    #define some parameters to identify words as noise and to filter from listing 
    noisy_pos_tags = ["PROP"]
    min_token_length = 2
    
    #Function to check if the token is a noise or not  
    def isNoise(token):     
        is_noise = False
        if token.pos_ in noisy_pos_tags:
            is_noise = True 
        elif token.is_stop == True:
            is_noise = True
        elif len(token.string) <= min_token_length:
            is_noise = True
        return is_noise 
    def cleanup(token, lower = True):
        if lower:
            token = token.lower()
        return token.strip()
    
    # top unigrams used in the reviews
    #cleaned_list = [cleanup(word.string) for word in document if not isNoise(word)]
    
    #labels = set([w.label_ for w in document.ents]) 
    ner_list = []
    for label in ['PERSON','ORG']:
        entities = [str(cleanup(e.string, lower=False)) for e in document.ents if label==e.label_] 
        entities = list(set(entities))
        ner_list.append(str(entities))
        #print ner_list
        #print "***********************************************"
    
    ### append entities list with frequent words. More appropriate words to list will give better results.
    ner_list.append(['named','appointed','join','president','officer','Technology','replace'])
    return ner_list

def sent_similarity(ner_list, document):
    query = nlp(unicode(ner_list))  
    
    doc_sim = []
    for sent in list(document.sents):
        temp = []
        temp.append(sent)
        temp.append(query.similarity(sent))
        temp.append(len(sent))
        doc_sim.append(temp)
        
    doc_sim = pd.DataFrame(doc_sim, columns=['Sentence','Similarity','Sentence Length'])
    sent_sim_sorted = doc_sim.sort_values(by='Similarity',ascending=False)
    
    return sent_sim_sorted    
    

def word_countbase_summary(sorted_sent,word_count):
    word_increment_cnt = 0
    for i in range(len(sorted_sent)):
        word_increment_cnt = word_increment_cnt + sorted_sent.iloc[i]['Sentence Length']
        indx = i
        if word_increment_cnt > word_count:
            break;
    if indx == 0:
        indx = indx + 1
        
    sorted_sent = sorted_sent[:indx]
    
    summary_text = []
    for sent in sorted_sent['Sentence']:
        summary_text.append(sent)
        
    return summary_text
    

text_sum_100 = []
text_sum_150 = []
text_sum_200 = []
sentence_cnt = 3
for i, article in enumerate(samp_text['Article Content']):
    ### Reduction - Python, TextRank (simple) ######
    ### Source  - https://github.com/adamfabish/Reduction
    #os.chdir('C:\Users\dt81540\Desktop\DataScience\Internals\RPA - NLP\Reduction-master\Source')
    #from reduction import *
    #reduction = Reduction()
    #text = open('filename.txt').read()
    #reduction_ratio = 1
    #reduced_text = reduction.reduce(article, reduction_ratio)
    #print(reduced_text)
    #text_sum.append(article)
    
    document = nlp(unicode(re.sub('[^A-Za-z0-9.;:/!-=,"$]+', ' ', article)))
    #document = nlp(unicode(article))
    #document = article
    #print(document)
    text_sum_100.append(word_countbase_summary(sent_similarity(ner_extract(document),document),100))
    text_sum_150.append(word_countbase_summary(sent_similarity(ner_extract(document),document),150))
    text_sum_200.append(word_countbase_summary(sent_similarity(ner_extract(document),document),200))
    


se_100 = pd.Series(text_sum_100)
samp_text["Article_Summary(100 words)"] = se_100.values

se_150 = pd.Series(text_sum_150)
samp_text["Article_Summary(150 words)"] = se_150.values

se_200 = pd.Series(text_sum_200)
samp_text["Article_Summary(200 words)"] = se_200.values
#se = pd.Series(ners)
#samp_text["Named_Entities"] = se.values


### Python, Term Frequency (very simple) ######
### Source - https://github.com/thavelick/summarize/ 

    #os.chdir('/home/test/Documents/text_summarizer/summarize-master')
    #import summarize
    #text = open('filename.txt').read()
    #ss = summarize.SimpleSummarizer()
    #reduced_text = ss.summarize(article, 2)
    #text_sum.append(reduced_text)

#https://github.com/chakki-works/sumeval


##### Writing to csv ###########
#print(os.curdir)
os.chdir('C:\Users\dt81540\Desktop\DataScience\Internals\RPA - NLP')
samp_text.to_csv(file_name,index=False)
