# Methods to gather features from the training data
# The "featurize" method is used in qc.py for the actual training
# Values are binary
# Labels: from Li & Roth's data
#
# Contributors:
# - Marie-Renee Arend
# - Josh Cason
# - Anthony Gentile

import sys, os, math, hashlib, cPickle as pickle, json
import operator
import nltk, re
from nltk.corpus import stopwords
import util
from util import *
from config573 import config
import classifier
from classifier import *
from collections import Counter
import cPickle as cp

output = open('trainTestOutput.txt', 'w')




def featurize(target, question, pickledquestionfeats):
    t = Tokenizer()
    tokens = t.stem_toke("%s %s" % (target, question))
    bigrams = map(lambda y: "%s%s" % ("q_",y), map(lambda x: ' '.join(x), bigramize(tokens)))
    trigrams = map(lambda y: "%s%s" % ("q_",y), map(lambda x: ' '.join(x), trigramize(tokens)))
    quadrigrams = map(lambda y: "%s%s" % ("q_",y), map(lambda x: ' '.join(x), quadrigramize(tokens)))
    
    qry = (target+question)
    if qry not in pickledquestionfeats:
        
        pickledquestionfeats[qry] = dict()
        pickledquestionfeats[qry]['A'] = dict(Counter(tokens+bigrams+trigrams+quadrigrams))
        pickledquestionfeats[qry]['B'] = weighContexts(question)
        pickledquestionfeats[qry]['C'] = extractTaggedUnigrams(question,target)
        pickledquestionfeats[qry]['D'] = extractHeadChunks(question)
        pickledquestionfeats[qry]['E'] = extractQuestionWord(question)
        
    feats = dict()
    
    A=True; B=True; C=True; D=True; E=False;
    # A: ngrams, B: adding pattern weights, C: added tagged unigrams, 
    # D: adding head chunks, E: adding question word
    
    for flagged,letter in [(A,'A'),(B,'B'),(C,'C'),(D,'D'),(E,'E')]:
    
        if flagged:
            feats = dict(pickledquestionfeats[qry][letter].items() + feats.items())

    '''
    add (or remove) whatever features you want here then run qc.devtest()
    to see if you've gained anything.
    '''
    return feats, pickledquestionfeats
    
def weighContexts(question):
    q = question.lower()

    if q.startswith('when') or q.startswith('what year') or q.startswith('what month'):
        return {'q_weigh_temporal' : 1}
    elif q.startswith('where') or q.startswith('in what country') or q.startswith('in what state') or q.startswith('what country') or q.startswith('what state'):
        return {'q_weigh_location' : 1}
    elif q.startswith('how many') or q.startswith('how much') or q.startswith('at what age') or q.startswith('how old'):
        return {'q_weigh_numerical' : 1}
    else:
        return {}      

# FEATURE FUNCTION
# Add POS tags to question + target words
# INPUT: question, target
def extractTaggedUnigrams(q, t):
    taggedUnigrams = {}
    text = []
    stopwords = nltk.corpus.stopwords.words('english')
	
    for token in nltk.wordpunct_tokenize(q + t):
	    if token.isalnum():
		    if token not in stopwords:
				text.append(token)

    taggedWords = nltk.pos_tag(text)
    for word, tag in taggedWords:
		# feature looks like: 'q_Rapunzel_NNP'
	    taggedUnigrams['q_' + word + '_' + tag] = 1

    return taggedUnigrams   
    
# FEATURE FUNCTION	
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
    tree = chunker.parse(taggedWords)
    NP_candidates = []
    VP_candidates = []
    for subtree in tree.subtrees():
        if subtree.node == 'NP':
	        NP_candidates.append(subtree)
        elif subtree.node == 'VP':
	        VP_candidates.append(subtree)
    if NP_candidates != []:
        cleanedN = str(re.sub(r'\/.{1,3}','',str(NP_candidates[0]))).replace(' ','_').replace('(','').replace(')','')
	    # FEATURE LOOKS LIKE: 'q_NP_the_little_yellow_dog'
        headChunks['q_' + cleanedN] = 1
    if VP_candidates != []:
        cleanedV = str(re.sub(r'\/.{1,3}','',str(VP_candidates[0]))).replace(' ','_').replace('(','').replace(')','')
	    # FEATURE LOOKS LIKE: 'q_VP_barked'
        headChunks['q_' + cleanedV] = 1

    return headChunks

# FEATURE FUNCTION
# extract question words 
# INPUT: question
def extractQuestionWord(q):
    tokens = []
    q_word = {}	
    for token in nltk.wordpunct_tokenize(q.strip()):
        tokens.append(token)		
    if q.lower().startswith('how'):
        q_word['q_' + tokens[0] + '_' + tokens[1]] = 1
    elif q.lower().startswith('for how'):
        q_word['q_' + tokens[0] + '_' + tokens[1] + '_' + tokens[2]] = 1
    elif q.lower().startswith('for'):
        q_word['q_' + tokens[0] + '_' + tokens[1]] = 1
    elif q.lower().startswith('from'):
        q_word['q_' + tokens[0] + '_' + tokens[1]] = 1
    else:
        q_word['q_' + tokens[0]] = 1
    # FEATURE LOOKS LIKE: 'q_how_many'		
    return q_word
	
