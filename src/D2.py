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
import nltk
import xml.etree.ElementTree as ET
from webcandidates import getcandidates, getwebresults

sys.path.insert(0, os.path.join("..", ".."))

from qa_filters import qa_filters

from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, MultiFieldQueryParser
    


import time



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

def reform_trec_questions(trec_file):
    tree = ET.parse(trec_file)
    root = tree.getroot()
    
    # we will store pertinent data in an array of question dictionaries
    new_root = ET.Element('questions')
    questions = []
    for target in root.findall('target'):
        for question in target.findall('qa'):
            q = question.find('q')
            if q.attrib['type'].strip() != 'FACTOID':
                continue
            
            q_dict = {}

            q_dict['target_id'] = target.attrib['id']
            q_dict['target_text'] = target.attrib['text']
            q_dict['question_id'] = q.attrib['id']
            q_dict['question_text'] = q.text.strip()
            
            if q_dict['target_text'].lower() in q_dict['question_text'].lower():
                q_dict['question_target_combined'] = q_dict['question_text']
            else:
                q_dict['question_target_combined'] = q_dict['target_text'] + ' ' + q_dict['question_text']

            q_dict['classification'] = classify_question(q_dict['question_text'])
            q_dict['bag_of_words'] = remove_stopwords(q_dict['question_text'])
            q_dict['stemmed_query'] = stem_query(q_dict['bag_of_words'])
            
            questions.append(q_dict)

    return questions
    


# Lets do some work!
if __name__ == '__main__':
    # load config
    json_data=open('config')
    config = json.load(json_data)
    json_data.close()

    try:
        trec_file = os.path.realpath(sys.argv[1])
    except:
        trec_file = config['trec_file']

    # Retrieve pertinent info from TREC questions file
    questions = reform_trec_questions(trec_file)
    
    # Load up items to be able to search AQUAINT lucene index
    STORE_DIR = config['aquant_index_dir']
    initVM()
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    parser = MultiFieldQueryParser(Version.LUCENE_CURRENT, ['doctext', 'docheadline'], analyzer)

    # output file
    out_file = '../outputs/' + config['deliverable'] + '.outputs'
    run_tag = config['deliverable'] + '-' + str(int(time.time()))
    f = open(out_file, 'a')
    for question in questions:
        q = question['question_target_combined']
            
        print q
        
        # Get Web Results leveraging N-Grams
        print "FETCHING WEB RESULTS"
        
        web_results = getwebresults(question, config)
        
        c = getcandidates(web_results, q)
        
        lim = config['web_results_limit']
        # TODO:up the lim and store these in lucene index.
        for r, count in c.most_common(lim):
            # now for each we get the supporting AQUAINT doc
            
            # Search AQUAINT lucene 
            # wildcard/partial term matching
            
            # we need to clean up our ngram set to make sure it doesn't have things that lucene won't like
            ngram_set = r
            qry = q + ' ' + ngram_set

            # replace any lucene keywords
            replacements = [',','.',';','|','/','\\','OR','AND','+','-','NOT','~','TO',':','[',']','(',')','{','}','!','||','&&','^','*','?','"']
            for p in replacements:
                qry = qry.replace(p, '')

            qry = qry.strip()

            whole_group = qry + '* OR ' + qry
            parts_group = ''
            terms = qry.split()
            i = 0
            for term in terms:
                if term.strip() == '':
                    continue
                if i != 0:
                    parts_group += ' OR '
                parts_group += '(' + term.strip() + '* OR ' + term.strip() + ')'
                i += 1
            qry = '(' + whole_group + ' OR ' + parts_group + ')'
            
            query = MultiFieldQueryParser.parse(parser, qry)
            
            # How many docs do we want back?
            aquaint_lim = 1
            scoreDocs = searcher.search(query, aquaint_lim).scoreDocs
            print "FOUND %s AQUAINT RESULT(S)." % len(scoreDocs)
    
            for scoreDoc in scoreDocs:
                doc = searcher.doc(scoreDoc.doc)
                # write to D2.outputs
                f.write(u' '.join((question['question_id'], run_tag, doc.get("docid"), ngram_set)).encode('utf-8').strip() + "\n")
                
        # lets just do the first one for now to not kill our rate quota
        # sys.exit()
        
    f.close()
    searcher.close()
    


