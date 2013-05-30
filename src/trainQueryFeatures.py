# BASELINE feature-gathering code for the training data.
# Current features: the words in the question & target with stopwords removed
# Value: 1 (meaning presence)
# Label: question word(s)
# prepending "q_" to all question features & labels per Josh's rqst
# ---------------------------------------------------------

import sys, os, math, hashlib, cPickle as pickle, json
import operator
import nltk
#from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
#from nltk.tag import pos_tag
#from nltk.tag.simplify import simplify_wsj_tag
#import xml.etree.ElementTree as ET
import util
from util import *
#from aquaint_lucene import aquaint_search
from config573 import config
import classifier
from classifier import *

output = open('trainTestOutput.txt','w')

# Extracting unigrams --> features for now (X)
# INPUT: target, question
def extractUnigrams(t,q):
    features = {}
    stopwords = nltk.corpus.stopwords.words('english')
    clean_q = q.strip()
    clean_t = t.strip()
	
    for q_unigram in nltk.wordpunct_tokenize(clean_q):
        if q_unigram.isalnum():
            if q_unigram not in stopwords:
                features['q_' + q_unigram] = 1 
	
    for t_unigram in nltk.wordpunct_tokenize(clean_t):
        if t_unigram.isalnum():
            if t_unigram not in stopwords:
                features['q_' + t_unigram] = 1

    return features

# storing question words --> label for now (Y)
# INPUT: question
def extractLabel(q):
    tokens = []
    label = ''
	
    for token in nltk.wordpunct_tokenize(q.strip()):
        tokens.append(token)
		
    if q.lower().startswith('how'):
        label = 'q_' + tokens[0] + '_' + tokens[1]
    elif q.lower().startswith('for how'):
        label = 'q_' + tokens[0] + '_' + tokens[1] + '_' + tokens[2]
    elif q.lower().startswith('for'):
        label = 'q_' + tokens[0] + '_' + tokens[1]
    elif q.lower().startswith('from'):
        label = 'q_' + tokens[0] + '_' + tokens[1]
    else:
        label = 'q_' + tokens[0]
		
    return label

# Train the classifier w/ 2004 & 2005 data
# Each question gets its own dictionary of feature/value pairs & 
#    list of corresponding labels
if __name__ == '__main__':
    qc = classifier.clsfr("question_classification")
    trainingData_04 = util.getquestion('2004')
    trainingData_05 = util.getquestion('2005')
    X = [] # List of dicts to store features (keys) & feature values (values)
    Y = [] # List of labels corresponding to each feature/value pair
	
	# adding features/values for 2004 TREC questions
    for qid in trainingData_04:
        target = trainingData_04[qid]['target']
        question = trainingData_04[qid]['question']
		# feature extraction function(s)
        features = extractUnigrams(target, question)
		# Label extraction function
        label = extractLabel(question)
		# append to respective list/dictionary
        X.append(features)
        Y.append(label)

    # adding features/values for 2005 TREC questions
    for qid in trainingData_05:
        target = trainingData_05[qid]['target']
        question = trainingData_05[qid]['question']
        features = extractUnigrams(target, question)
		# Label extraction function
        label = extractLabel(question)
		# append to respective list/dictionary
        X.append(features)
        Y.append(label)
	
	# testing
    for i in range(0,len(X)-1):
        output.write('X member #' + str(i) + ' = ' + str(X[i]) + '\n')
    for j in range(0,len(Y)-1):
        output.write('Y member #' + str(j) + ' = ' + str(Y[j]) + '\n')
	
    qc.train(X,Y)
		
	
    