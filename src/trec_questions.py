#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Retrieve TREC Questions and do query expansion
# Example usage: 
# python2.7 trec_questions.py /dropbox/12-13/573/Data/Questions/training/TREC-2005.xml
#
# slightly expanded query reformulation...
# (much work left to be done)
#
# @author Marie-Renee Arend <rcarend@uw.edu>
# @author Anthony Gentile <agentile@uw.edu>
import sys, os
import nltk
#from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import xml.etree.ElementTree as ET

# output file (stores reformulated queries + relevant question data)
output = open('query_reform_output.txt','w')

# storing question words
def classify_question(text):
    words = []
    for word in text:
	    words.append(word)
    if text.lower().startswith('how'):
		question_word = words[0] + '_' + words[1]
    elif text.lower().startswith('for how'):
        question_word = words[0] + '_' + words[1] + '_' + words[2]
    elif text.lower().startswith('for'):
	    question_word = words[0] + '_' + words[1]
    elif text.lower().startswith('from'):
	    question_word = words[0] + '_' + words[1]
    else:
	    question_word = words[0]
    return question_word

# removing stopwords
def remove_stopwords(text):
    stopwords = nltk.corpus.stopwords.words('english')
    mod_text = ''
    for word in nltk.wordpunct_tokenize(text):
        if word.isalnum():
            if word not in stopwords:
                mod_text += word.lower() + ' '				
    return mod_text

# adding synonyms
#def expand_query_vocab(mod_text):

# stemming
def stem_query(mod_text):
    final_text = ''
    stemmer = nltk.PorterStemmer()
    for wordform in mod_text.split(' '):
        stemmed = stemmer.stem(wordform)
        final_text += stemmed + ' '
    return final_text

# modification of Anthony's code
if __name__ == '__main__':
    trec_file = os.path.realpath(sys.argv[1])
    tree = ET.parse(trec_file)
    root = tree.getroot()
    for target in root.findall('target'):
        target_id = target.attrib['id']
        target_text = target.attrib['text']
        #store target + useful info
        output.write('Target: ' + target_text + ' ' + 'Target_ID: ' + target_id)
        for question in target.findall('qa'):
            q = question.find('q')
            if q.attrib['type'].strip() != 'FACTOID':
                continue
            question_id = q.attrib['id']
            question_text = q.text.strip()

            # store question + useful info
            output.write(question_id + '    ' + question_text)
            
            # do some query modification
            question_word = classify_question(question_text)
            output.write('Classification: ' + question_word)

            mod_text = remove_stopwords(question_text)
            output.write('BagOfWords: ' + mod_text)

            final_text = stem_query(mod_text)
            output.write('StemmedQuery: ' + final_text)

            output.write('ExpandedQuery: ') # missing method(s) for query expansion
