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
import qc
from devpipeline import evalcandidates, train

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

    searcher = IndexSearcher(SimpleFSDirectory(File('aquaint_index')), True)
    searcher2 = IndexSearcher(SimpleFSDirectory(File('aquaint_index2')), True)

    # output file
    out_file0 = '../outputs/' + 'QA' + '.' + 'outputs'
    
    train()
    
    for year in ['2006','2007']:
        out_file1 = out_file0 + '_'+ year + '_100'
        out_file2 = out_file0 + '_'+ year + '_250'
        
        run_tag = config['deliverable'] + '-' + str(int(time.time()))
        f1 = open(out_file1, 'w')
        f2 = open(out_file2, 'w')
        
        # determine ngrams from our search results
        cdict = evalcandidates(year)    
        for qid in sorted(cdict.keys(), key=lambda x: float(x)):
            q = getquestion(qid=qid)
            c = cdict[qid]
            # for the most common ngrams lets find some matching AQUAINT docs
            for ngram_set, count in c.most_common(config['answer_candidates_limit']):
                # now for each we get the supporting AQUAINT doc
                # Search AQUAINT lucene 
                # Add the ngram set to our question
                qry = q['target'] + ' ' + q['question'] + ' ' + ngram_set    
                if year == '2007':
                    doc = aquaint_search(qry, searcher2)   
                else:
                    doc = aquaint_search(qry, searcher)
                    
                if doc is not False:
                    # write to D2.outputs
                    f1.write(u' '.join((qid, run_tag, doc.get("docid"), ngram_set)).encode('utf-8').strip() + "\n")
                    f2.write(u' '.join((qid, run_tag, doc.get("docid"), ngram_set)).encode('utf-8').strip() + "\n")
    searcher.close()
    f1.close()
    f2.close()
    
    # End Timer
    end = datetime.now()
    print 'Time elapsed: ' + str(end - start)
    


