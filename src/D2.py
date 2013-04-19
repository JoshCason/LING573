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
import sys, os, math
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import xml.etree.ElementTree as ET
from collections import Counter

from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, MultiFieldQueryParser
    
sys.path.append('./requests/')
from bing_search_api import BingSearchAPI

stopwords = set(stopwords.words('english'))
punct = set(["'",',','.',':',';','?','-','!','(',')', '|'])

quadrigramize = lambda t: [(t[w],t[x],t[y],t[z]) for (w,x,y,z) in \
                zip(range(0,len(t)-3), \
                    range(1,len(t)-2), \
                    range(2,len(t)-1), \
                    range(3, len(t)-0))]

trigramize = lambda t: [(t[x],t[y],t[z]) for (x,y,z) in \
                zip(range(len(t)-2), \
                    range(1,len(t)-1), \
                    range(2,len(t)))]

bigramize = lambda t: [(t[x],t[y]) for (x,y) in \
                zip(range(len(t)-1),range(1,len(t)))]

my_key = 'cvzWROzO9Vaxqu0k33+y6h++ts+a4PLQfvA7HlyJyXM='
bing = BingSearchAPI(my_key)

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
    
def getcandidates(query, limit):
    text = ''
    # Get the top 100 - I think it will let you get only 50 at a time.
    per_page = 50
    pages = int(math.ceil(limit / float(per_page)))
    for page in range(pages):
        offset = (limit * (page + 1)) - limit;
        params = {'$format': 'json', '$top': limit,'$skip': offset}
        try:
            results = bing.search('web',query,params)()['d']['results'][0]['Web']
        except:
            print params
            raise
        for result in results:
            text += "... %s" % result['Title']
            text += "... %s" % result['Description']
    ngrams = Counter()
    texts = text.split('...')
    toked = []
    for t in texts:
        tokes = word_tokenize(t)
        tokes = map(lambda x: x.lower(), tokes)
        toked.append(tokes)
    for tokens in toked:
        ngrams.update(tokens)
        ngrams.update(map(lambda x: ' '.join(x), bigramize(tokens)))
        ngrams.update(map(lambda x: ' '.join(x), trigramize(tokens)))
        ngrams.update(map(lambda x: ' '.join(x), quadrigramize(tokens)))
    for k in ngrams.keys():
        qwords = set(map(lambda x: x.lower(), word_tokenize(query)))
        variations = set()
        for qword in qwords:
            variations.add("%s%s" % (qword,"s"))
            variations.add("%s%s" % (qword,"es"))
            variations.add("%s%s" % (qword,"ed"))
            variations.add("%s%s" % (qword,"."))
            variations.add("%s%s" % (qword,"er"))
            variations.add("%s%s" % (qword,"ers"))
            variations.add(qword[:-1])
        qwords.update(variations)
        remove = False
        if k in stopwords:remove = True
        if k in punct:remove = True
        tokens = k.split()
        if len(tokens) > 1:
            if k.split()[0] in stopwords:remove = True
            if k.split()[-1] in stopwords:remove = True
            for token in tokens:
                if token in qwords: remove = True
        if k in qwords: remove = True
        if remove: del ngrams[k]
    for k in ngrams.keys():
        tokens = k.split()
        if len(tokens) > 1:
            for token in tokens:
                ngrams[k] += ngrams[token]
    return ngrams 
    
# Lets do some work!
if __name__ == '__main__':
    trec_file = os.path.realpath(sys.argv[1])
    
    # Retrieve pertinent info from TREC questions file
    questions = reform_trec_questions(trec_file)
    
    # Load up items to be able to search AQUAINT lucene index
    STORE_DIR = "aquaint_index"
    initVM()
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    parser = MultiFieldQueryParser(Version.LUCENE_CURRENT, ['doctext', 'docheadline'], analyzer)
    
    for question in questions:
        q = question['question_target_combined']

        print q
        
        # Search AQUAINT lucene first
        # wildcard/partial term matching
        print "FETCHING AQUAINT RESULTS"
        whole_group = q.strip() + '* OR ' + q.strip()
        parts_group = ''
        terms = q.split()
        i = 0
        for term in terms:
            if i != 0:
                parts_group += ' OR '
            parts_group += '(' + term.strip() + '* OR ' + term.strip() + ')'
            i += 1
        term = '(' + whole_group + ' OR ' + parts_group + ')'
        
        query = MultiFieldQueryParser.parse(parser, term)
        
        # How many docs do we want back?
        aquaint_lim = 1
        scoreDocs = searcher.search(query, aquaint_lim).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            print 'docid:', doc.get("docid")
            print 'docheadline:', doc.get("docheadline")
            print 'doctext:', doc.get("doctext")
        
        # Get Web Results leveraging N-Grams
        print "FETCHING WEB RESULTS"
        lim = 4
        # Should check cache first
        c = getcandidates(q, lim)
        # TODO:up the lim and store these in lucene index.
        for r, count in c.most_common(lim):
            print '%s: %7d' % (r, count)
            
        # lets just do the first one for now to not kill our rate quota
        sys.exit()
        
    searcher.close()
    


