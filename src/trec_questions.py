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
    return mod_text.strip()

# adding synonyms
#def expand_query_vocab(mod_text):

# stemming
def stem_query(mod_text):
    final_text = ''
    stemmer = nltk.PorterStemmer()
    for wordform in mod_text.split(' '):
        stemmed = stemmer.stem(wordform)
        final_text += stemmed + ' '
    return final_text.strip()

# modification of Anthony's code
if __name__ == '__main__':
    trec_file = os.path.realpath(sys.argv[1])
    tree = ET.parse(trec_file)
    root = tree.getroot()
    
    # we will store pertinent data in a new XML file
    new_root = ET.Element('questions')
    for target in root.findall('target'):
        for question in target.findall('qa'):
            q = question.find('q')
            if q.attrib['type'].strip() != 'FACTOID':
                continue
                
            question = ET.SubElement(new_root, 'question')
            target_id = ET.SubElement(question,'target_id')
            target_id.text = target.attrib['id']
            
            target_text = ET.SubElement(question,'target_text')
            target_text.text = target.attrib['text']
            
            question_id = ET.SubElement(question,'question_id')
            question_id.text = q.attrib['id']
            
            question_text = ET.SubElement(question,'question_text')
            question_text.text = q.text.strip()
            
            question_target_combined = ET.SubElement(question,'question_target_combined')
            if target_text.text.lower() in q.text.strip().lower():
                question_target_combined.text = q.text.strip()
            else:
                question_target_combined.text = target_text.text + ' ' + q.text.strip()
            
            classification = ET.SubElement(question,'classification')
            classification.text = classify_question(question_text.text)
            
            bag_of_words = ET.SubElement(question,'bag_of_words')
            bag_of_words.text = remove_stopwords(question_text.text)
            
            stemmed_query = ET.SubElement(question,'stemmed_query')
            stemmed_query.text = stem_query(bag_of_words.text)

    # output file (stores reformulated queries + relevant question data)
    new_tree = ET.ElementTree(new_root)
    new_tree.write('reformed_' + os.path.basename(trec_file))

