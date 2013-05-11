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


    
# stemming
def stem_query(mod_text):
    final_text = ''
    stemmer = nltk.PorterStemmer()
    for wordform in mod_text.split(' '):
        stemmed = stemmer.stem(wordform)
        final_text += stemmed + ' '
    return final_text.strip()

# methods for finding synonyms/hypernyms/storing data
wnTags = {'ADJ':'a','ADV':'r','N':'n','V':'v','VD':'v','VG':'v'}

goalWords = {}
hypernyms = []
synonyms = []

def processQuestion(q, tagset):
	#tags input question with simplified NLTK tagset
    bagOfWords = nltk.word_tokenize(q)
    #TEST: print 'tokenized'
    taggedWords = nltk.pos_tag(bagOfWords)
    #TEST: print 'tagged words'
    simplified = [(word, simplify_wsj_tag(tag)) for word, tag in taggedWords] 
    #TEST: print taggedWords	
    
	#converts NLTK simplified tagset to WordNet-accepted tags
    for word, tag in simplified:
	    if wnTags.has_key(tag):
		    goalWords[word.lower()] = wnTags[tag]
	
    return goalWords		    

def findBestSense(goalWords, q):
    commonWords = 0
    count = 0
    maxCount = -1
    optimumSense = ''
    glossWords = []
    senseRank = {}
	
    for key in goalWords.keys():
        #TEST: print 'key =' + str(key)
        POS = str(goalWords[key])
	
        for word in q:
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
			
        sorted_senseRank = sorted(senseRank.iteritems(), key=operator.itemgetter(1))
        optimumSense = len(sorted_senseRank)
        #TEST: print sorted_senseRank[optimumSense - 1]
        hyps = sorted_senseRank[optimumSense - 1][0].hypernyms()
        for hyp in hyps:
            hypernyms.append(hyp.name.split('.')[0])

			
        synonyms.append(key)			
        for lemma in sorted_senseRank[optimumSense - 1][0].lemmas:
            synonyms.append(lemma)

        results = []
        wordDict = {}
		
        wordDict['key'] = key
        wordDict['tag'] = key + '.' + POS
        wordDict['synset'] = key + '.' + str(sorted_senseRank[optimumSense - 1][0])
		
        for i in range(len(hyps)):
            whichHyp = 'hypernym' + str(i)
            wordDict[whichHyp] = key + '.' + str(hyps[i])

        results.append(wordDict)		    
		
        senseRank.clear()

    return results

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
            
            # grabbing question text to find synonyms
            processQuestion(q.text.strip(), wnTags)
            findBestSense(goalWords, q.text.strip())
            #adding synonyms to question/target text
            for synonym in synonyms:
                q_dict['question_target_combined'] += ' ' + synonym + ' '

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
    


