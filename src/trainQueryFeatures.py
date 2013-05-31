# BASELINE feature-gathering code for the training data.
# Current features: the words in the question & target with stopwords removed
# Value: 1 (meaning presence)
# Label: question word(s)
# prepending "q_" to all question features & labels per Josh's rqst
# ---------------------------------------------------------

import sys, os, math, hashlib, cPickle as pickle, json
import operator
import nltk, re
from nltk.corpus import stopwords
import util
from util import *
from config573 import config
import classifier
from classifier import *

output = open('trainTestOutput.txt','w')

# Extracting unigrams
# INPUT: target, question
def extractUnigrams(t,q):
    unigrams = {}
    stopwords = nltk.corpus.stopwords.words('english')
    clean_q = q.strip()
    clean_t = t.strip()
	
    for q_unigram in nltk.wordpunct_tokenize(clean_q):
        if q_unigram.isalnum():
            if q_unigram not in stopwords:
                unigrams['q_' + q_unigram] = 1 
	
    for t_unigram in nltk.wordpunct_tokenize(clean_t):
        if t_unigram.isalnum():
            if t_unigram not in stopwords:
                unigrams['q_' + t_unigram] = 1

    return unigrams

# Add POS tags to question + target words
# INPUT: question, target
def extractTaggedUnigrams(q,t):
    taggedUnigrams = {}
	text = []
	stopwords = nltk.corpus.stopwords.words('english')
	
	for token in nltk.wordpunct_tokenize(q + t):
	    if token.isalnum():
		    if token not in stopwords:
				text.append(token)

    taggedWords = nltk.pos_tag(text)
    for t in taggedWords:
	    taggedUnigrams['q_' + t] = 1

    return taggedUnigrams   
    
	
# Head NP + Head VP chunks
# INPUT: question
def extractHeadChunks(q):
	# 1st step: tag the question words
    text = []
    stopwords = nltk.corpus.stopwords.words('english')	
    for token in nltk.wordpunct_tokenize(q):
        if token.isalnum():
            if token not in stopwords:
                text.append(token)
    taggedWords = nltk.pos_tag(text)
	
	# 2nd step: chunk
    headChunks = {}
	# grammar to extract NP & VP chunks from the question
    grammar = r"""
        NP: {<DT|PP\$>?<JJ>*<NN|NNP>+}
        VP: {<MD>?<V.+>+}
    """
    chunker = nltk.RegexpParser(grammar)
    tree = chunker.parse(sentence)
    NP_candidates = []
    VP_candidates = []
    for subtree in tree.subtrees():
        if subtree.node == 'NP':
	        NP_candidates.append(subtree)
        elif subtree.node == 'VP':
	        VP_candidates.append(subtree)
	# doing some clean-up of the subtree before adding it as a feature
	cleanedN = re.sub(r'\/.{1,3}','',str(NP_candidates[0]))
	finalN = cleanedN.replace(' ','_')
    headChunks['q_' + finalN] = 1
    cleanedV = re.sub(r'\/.{1,3}','',str(VP_candidates[0]))
    finalV = cleanedV.replace(' ','_')
    headChunks['q_' + finalV] = 1
    return headChunks

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
	
def addFeaturesValues(trainingData, X, Y):
    target = trainingData[qid]['target']
    question = trainingData[qid]['question']
	
    # feature extraction function(s)
    unigrams = extractUnigrams(target, question)
    X.append(unigrams)
	taggedUnigrams = extractTaggedUnigrams(question, target)
    X.append(taggedUigrams)
    chunks = extractHeadChunks(question)
    X.append(chunks)
	
    # Label extraction function
    label = extractLabel(question)
    Y.append(label)
	
    return X, Y

# Train the classifier w/ 2004 & 2005 data; devtest = 2006 data
# Each question gets its own dictionary of feature/value pairs & 
#    list of corresponding labels
if __name__ == '__main__':
    qc = classifier.clsfr("question_classification")
	
    trainingData_04 = util.getquestion('2004') # train
    trainingData_05 = util.getquestion('2005') # train
    trainingData_06 = util.getquestion('2006') # devtest
	
    X = [] # List of dicts to store features (keys) & feature values (values)
    Y = [] # List of labels corresponding to each feature/value pair
	
	# adding features/values for 2004 TREC questions
    for qid in trainingData_04:
        addFeaturesValues(trainingData_04, X, Y)		

    # adding features/values for 2005 TREC questions
    for qid in trainingData_05:
        addFeaturesValues(trainingData_05, X, Y)
			
	# writing X/Y content to output file to check if it's right
    for i in range(0,len(X)-1):
        output.write('X member #' + str(i) + ' = ' + str(X[i]) + '\n')
    for j in range(0,len(Y)-1):
        output.write('Y member #' + str(j) + ' = ' + str(Y[j]) + '\n')
	
    qc.train(X,Y)
    
	# QUESTION: Am I supposed to do this?? I was getting an error that seemed to suggest I should
    X = []
    Y = []

	# ---------------------------------------------------------------------
	# DEVTEST	
	# adding features/values for 2006 TREC questions
    features_dict = dict()
	
    for qid in trainingData_06:
        addFeaturesValues(trainingData_06, X, Y)    
	
	# testing contents of X & Y
    for i in range(0,len(X)-1):
        output.write('X member #' + str(i) + ' = ' + str(X[i]) + '\n')
    for j in range(0,len(Y)-1):
        output.write('Y member #' + str(j) + ' = ' + str(Y[j]) + '\n')
	
    Y_model = qc.devtest(X,Y)
	
	# ERROR MESSAGE: "return" outside function... I have no idea why this is happening
    #return features_dict, Y_model
	
    