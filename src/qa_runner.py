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
import web_reranking
import qc

sys.path.insert(0, os.path.join("..", ".."))

from qa_filters import qa_filters

from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, MultiFieldQueryParser
    
import time
from datetime import datetime




# Lets do some work! Main Runner
if __name__ == '__main__':

    
        
    # Start timer
    start = datetime.now()
    STORE_DIR = config['aquant_index_dir']
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    

    # output file
    out_file = '../outputs/' + config['deliverable'] + '.' + str(config['answer_char_length']) + '.outputs'
    run_tag = config['deliverable'] + '-' + str(int(time.time()))
    f = open(out_file, 'a')
    
    # determine ngrams from our search results
    c = evalcandidates()
    
    for question in questions[:qta]:
    
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
    


