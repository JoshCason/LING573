#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Retrieve TREC Questions, do query expansion, AQUAINT and web searching,
# evaluation, reranking, and spit out D2.outputs
# Example usage: 
# python2.7 D2.py /dropbox/12-13/573/Data/Questions/training/TREC-2005.xml
#
#
# @author Marie-Renee Arend <rcarend@uw.edu>
# @author Joshua Cason <casonj@uw.edu>
# @author Anthony Gentile <agentile@uw.edu>
import sys, os, math, hashlib, cPickle as pickle, json
import operator
import nltk
from nltk.corpus import wordnet as wn
from nltk.tag import pos_tag
from nltk.tag.simplify import simplify_wsj_tag
import xml.etree.ElementTree as ET
from webcandidates import apply_filters, getcandidates
from util import getplainwebresults, getquestion
from aquaint_lucene import aquaint_search
from config573 import config
import pprint
import classifier as clsfr

sys.path.insert(0, os.path.join("..", ".."))

from qa_filters import qa_filters

from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, MultiFieldQueryParser
    
import time
from datetime import datetime

# Apply Anthony's context filters
def apply_filters(web_results, question, limit):
    filters = qa_filters(web_results)
    
    # Initial weigh by rank index
    filters.weigh_index_position()

    # Weigh by question word type that have matching context in results
    q = question.lower()

    if q.startswith('when') or q.startswith('what year') or q.startswith('what month'):
        filters.weigh_temporal_context()
    elif q.startswith('where') or q.startswith('in what country') or q.startswith('in what state') or q.startswith('what country') or q.startswith('what state'):
        filters.weigh_location_context()
    elif q.startswith('how many') or q.startswith('how much') or q.startswith('at what age') or q.startswith('how old'):
        filters.weigh_numerical_context()
    
    return filters.top(limit)

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
    
# stemming
def stem_query(mod_text):
    final_text = ''
    stemmer = nltk.PorterStemmer()
    for wordform in mod_text.split(' '):
        stemmed = stemmer.stem(wordform)
        final_text += stemmed + ' '
    return final_text.strip()

def processQuestion(q):
    # methods for finding synonyms/hypernyms/storing data
    wnTags = {'ADJ':'a','ADV':'r','N':'n','V':'v','VD':'v','VG':'v'}
	#tags input question with simplified NLTK tagset
    bagOfWords = nltk.word_tokenize(q)
    #TEST: print 'tokenized'
    taggedWords = nltk.pos_tag(bagOfWords)
    #TEST: print 'tagged words'
    simplified = [(word, simplify_wsj_tag(tag)) for word, tag in taggedWords] 
    #TEST: print taggedWords	
    
    goalWords = {}
    
	#converts NLTK simplified tagset to WordNet-accepted tags
    for word, tag in simplified:
	    if wnTags.has_key(tag):
		    goalWords[word.lower()] = wnTags[tag]
	
    return goalWords		    

def findBestSense(goalWords, q):
    synonyms = []
    commonWords = 0
    count = 0
    maxCount = -1
    optimumSense = ''
    glossWords = []
    senseRank = {}
	
    for key in goalWords.keys():
        #TEST: print 'key =' + str(key)
        POS = str(goalWords[key])
	
        for word in goalWords.keys():
		    # for each word in the question:
            senses = wn.synsets(word) # find all the senses for the word
            for sense in senses: # for each sense of the question word
                gloss = sense.definition # retrieve its definition
                for w in gloss:
                    if w not in glossWords:
                    	glossWords.append(w)
                    else:
                        continue		    
	
        for synset in wn.synsets(key, POS):
            #TEST: print synset
	        # for each sense of the head word in the question:
            count = 0
            #TEST: print count
		    # pull up the definition of that sense
            goalWordGloss = synset.definition
            for word in goalWordGloss:
                for item in glossWords:
                    if word.lower() == item.lower():
                        count += 1
            senseRank[synset] = count
			
        
        # sorted descending and grab the first (optmium sense)
        sorted_senseRank = sorted(senseRank.iteritems(), key=operator.itemgetter(1), reverse=True)

        synonyms.append(key)	
        
        if len(sorted_senseRank) > 0:
            for lemma in sorted_senseRank[0][0].lemma_names:
                synonyms.append(lemma) 
		
        senseRank.clear()

    return synonyms

# From our TREC files lets gather up the questions and any other pertinent
# info we want about them.
def reform_trec_questions(trec_file):
    tree = ET.parse(trec_file)
    root = tree.getroot()
    trecyear = root.attrib['year']
    
    # we will store pertinent data in an array of question dictionaries
    new_root = ET.Element('questions')
    questions = []
    for target in root.findall('target'):
        for question in target.findall('qa'):
            q = question.find('q')
            if q.attrib['type'].strip() != 'FACTOID':
                continue
            
            q_dict = {}

            # Comment out most of this as Josh already has the information cached, we just need the question id
            #q_dict['target_id'] = target.attrib['id']
            #q_dict['target_text'] = target.attrib['text']
            q_dict['question_id'] = q.attrib['id']
            #q_dict['question_text'] = q.text.strip()
            
            #if q_dict['target_text'].lower() in q_dict['question_text'].lower():
            #    q_dict['question_target_combined'] = q_dict['question_text']
            #else:
            #    q_dict['question_target_combined'] = q_dict['target_text'] + ' ' + q_dict['question_text']
            
            #q_dict['question_target_combined']  

            #q_dict['classification'] = classify_question(q_dict['question_text'])
            #q_dict['bag_of_words'] = remove_stopwords(q_dict['question_text'])
            #q_dict['stemmed_query'] = stem_query(q_dict['bag_of_words'])
            
            # Commenting synonym processing out for now (as it is somewhat intensive and in question about 
            # whether to be used or not
            
            # grabbing question text to find synonyms
            #q_dict['synonyms'] = findBestSense(processQuestion(q.text.strip()), q.text.strip())

            #adding synonyms to question/target text
            #q_dict['question_target_synonyms_combined'] = q_dict['question_target_combined']  
            #for synonym in q_dict['synonyms']:
            #    q_dict['question_target_synonyms_combined'] += ' ' + synonym + ' '
                
            questions.append(q_dict)

    return questions
    
def addtrainingfeatures(clsfr, questions):
    for question in questions:
        # get question info
        q = getquestion(qid=question['question_id'])
        # grab web results from cache
        results = getplainwebresults(question['question_id'])
        # apply some filters
        results = apply_filters(results, q['question'], config['web_results_limit'])
        
        for r in results:
            clsfr.addfeatures(question['question_id'], 'figureoutanswercand', {'rank' : r['rank'], 'weight' : r['weight']})
            
def adddevtestfeatures(clsfr, questions):
    for question in questions:
        # get question info
        q = getquestion(qid=question['question_id'])
        # grab web results from cache
        results = getplainwebresults(question['question_id'])
        # apply some filters
        results = apply_filters(results, q['question'], config['web_results_limit'])
        
        for r in results:
            clsfr.addfeatures(question['question_id'], 'figureoutanswercand', {'rank' : r['rank'], 'weight' : r['weight']})
    
def devpipeline(questions):
    mainclsfr = clsfr.clsfr("main")
    addtrainingfeatures(mainclsfr, questions) # needs to be written, looks up questions and web results for 2004 and 2005, extracts features
    mainclsfr.train()
    adddevtestfeatures(mainclsfr, questions) # also needs to be done, but only differs in doing 2006
    results = mainclsfr.devtest() # for devtest the results can be thrown away (unless we want to focus on strict MRR too, let me know)
    return mainclsfr
    
# Lets do some work! Main Runner
if __name__ == '__main__':

    # load trec file from config or command line argument
    try:
        trec_file = os.path.realpath(sys.argv[1])
    except:
        trec_file = config['trec_file']
        
    # Start timer
    start = datetime.now()

    # Retrieve pertinent info from TREC questions file
    questions = reform_trec_questions(trec_file)
    STORE_DIR = config['aquant_index_dir']
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    

    # output file
    out_file = '../outputs/' + config['deliverable'] + '.' + str(config['answer_char_length']) + '.outputs'
    run_tag = config['deliverable'] + '-' + str(int(time.time()))
    f = open(out_file, 'a')
    qta = config["questions_to_answer"]
    assert(type(qta == int))
    if qta == 0:
        qta = len(questions)
    
    # do classifier fun
    clsfr = devpipeline(questions[:qta])
    clsfr.report()
    clsfr.acc
    
    for question in questions[:qta]:

        # this is a crude means of picking up where a run left off if it fails for some reason
        # you need to find the last question_id in the output file
        #if question['question_id'] <= '205.4':
        #    continue
        
            
        print q['target'] + ' - ' + q['question']
        # get question info
        q = getquestion(qid=question['question_id'])
        # grab web results from cache
        web_results = getplainwebresults(question['question_id'])
        # apply some filters
        web_results = apply_filters(web_results, q['question'], config['web_results_limit'])

        # do something with our classifier
        
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(web_results)

        # determine ngrams from our search results
        c = getcandidates(web_results, q['target'] + ' ' + q['question'])
        
        # for the most common ngrams lets find some matching AQUAINT docs
        for ngram_set, count in c.most_common(config['answer_candidates_limit']):
            # now for each we get the supporting AQUAINT doc
            
            # Search AQUAINT lucene 
            # Add the ngram set to our question
            qry = q['target'] + ' ' + q['question'] + ' ' + ngram_set
            
            doc = aquaint_search(qry, searcher)
            
            if doc is not False:
                # write to D2.outputs
                f.write(u' '.join((question['question_id'], run_tag, doc.get("docid"), ngram_set)).encode('utf-8').strip() + "\n")
    searcher.close()
    f.close()
    
    # End Timer
    end = datetime.now()
    print 'Time elapsed: ' + str(end - start)
    


