#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Web Candidates
#
# @author Marie-Renee Arend <rcarend@uw.edu>
# @author Joshua Cason <casonj@uw.edu>
# @author Anthony Gentile <agentile@uw.edu>
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
from util import *
import string
from nltk.corpus import stopwords
import sys, os, hashlib, cPickle as pickle, math
from qa_filters import qa_filters
from config573 import config
sys.path.append('./requests/')
from bing_search_api import BingSearchAPI

my_key = 'cvzWROzO9Vaxqu0k33+y6h++ts+a4PLQfvA7HlyJyXM='
bing = BingSearchAPI(my_key)

sys.path.insert(0, os.path.join("..", ".."))

from xgoogle.search import GoogleSearch, SearchError

from pattern.web import Bing, asynchronous, plaintext
from pattern.web import SEARCH, IMAGE, NEWS
import time

# for our search libraries search things about our queries need cleaned
def clean_query(q):
    return q.replace('#','').replace('&','')

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

# search the web for a particular query using different libraries and engines
def websearch(search_library, search_engine, query, limit):
    ret = []
    # Get the top 100 - I think it will let you get only 50 at a time.
    per_page = 50
    pages = int(math.ceil(limit / float(per_page)))

    if search_library == 'pattern':
        engine = Bing(license='cvzWROzO9Vaxqu0k33+y6h++ts+a4PLQfvA7HlyJyXM=', language="en")
        for page in range(pages):
            try:
                # turns out start = starting page and count is results per page
                # could probably do some logic to make sure count is right if limit was 130, on page 3, count should be 30, whereas 
                # our code is going to fetch 50 for a total of 150. ... I think we can probably mess with that later and just work in blocks of 50
                request = asynchronous(engine.search, clean_query(query), start=page+1, count=per_page, type=SEARCH, timeout=10)
                while not request.done:
                    time.sleep(0.01)
            except:
                raise

            for result in request.value:
                ret.append({'title' : result.title, 'description' : result.text})
            
    elif search_library == 'requests':
        for page in range(pages):
            offset = per_page * page
            params = {'$format': 'json', '$top': per_page,'$skip': offset}
            results = bing.search('web',clean_query(query),params)()['d']['results'][0]['Web']
            for result in results:
                ret.append({'title' : result['Title'], 'description' : result['Description']})
                
    elif search_library == 'xgoogle':
        for page in range(pages):
            try:
                # inject some delay
                time.sleep(0.04)
                gs = GoogleSearch(clean_query(query))
                gs.page = page+1
                gs.results_per_page = per_page
                results = gs.get_results()
                for res in results:
                    ret.append({'title' : res.title.encode("utf8"), 'description' : res.desc.encode("utf8")})
            except SearchError, e:
                print "Search failed: %s" % e
                
    return ret

# grather up n-grams from our web search reslts
def getcandidates(search_results, query):
    stop_words = set(stopwords.words('english')) | set(["'s"])
    punct = set(string.punctuation)
        
    ngrams = Counter()
    for result in search_results:
        text = ''
        text += "... %s" % result['title']
        text += "... %s" % result['description']
        texts = text.split('...')
        toked = []
        for t in texts:
            tokes = word_tokenize(t)
            tokes = map(lambda x: x.lower(), tokes)
            toked.append(tokes)
        for tokens in toked:
            bigrams = map(lambda x: ' '.join(x), bigramize(tokens))
            trigrams = map(lambda x: ' '.join(x), trigramize(tokens))
            quadrigrams = map(lambda x: ' '.join(x), quadrigramize(tokens))
            for token in tokens:
                ngrams[token] += result['weight']
            for bigram in bigrams:
                ngrams[bigram] += result['weight']
            for trigram in trigrams:
                ngrams[trigram] += result['weight']
            for quadrigram in quadrigrams:
                ngrams[quadrigram] += result['weight']
    stemmer = nltk.PorterStemmer()
    for k in ngrams.keys():
        qwords = set(map(lambda x: stemmer.stem(x.lower()), word_tokenize(query)))
        remove = False
        tokens = k.split()
        if len(tokens) > 1:
            if tokens[0] in stop_words: remove = True
            if tokens[-1] in stop_words: remove = True
            for token in tokens:
                if stemmer.stem(token) in qwords: remove = True
                if token in punct: remove = True
        else:
            if k in stop_words: remove = True
            if k in punct: remove = True
            if stemmer.stem(k) in qwords: remove = True
        if remove: del ngrams[k]
    for k in ngrams.keys():
        tokens = k.split()
        if len(tokens) > 1:
            for token in tokens:
                ngrams[k] += ngrams[token]
    return ngrams 

# Take a TREC question and retrieve search results from the web. 
# Leverage caching and exact query searching
def getwebresults(question):
    q = question['question_target_combined']
    # blocks of 50
    lim = config['web_results_limit']
    search_library = config['search_library_active']
    search_engine = config['search_engine_active']
    
    # Should check cache first
    cache_key = hashlib.md5(q + search_engine + search_library).hexdigest()
    cache_path = config['web_cache_dir'] + '/' + search_engine + '/' + search_library + '/' + cache_key
    
    if config['reset_web_cache'] == 0 and os.path.exists(cache_path):
        # continue # uncomment this just to cache a bunch of web results.
        with open(cache_path ,'rb') as fp:
            web_results = pickle.load(fp)
    else:
        web_results = websearch(search_library, search_engine, q, lim)
        with open(cache_path ,'wb') as fp:
            pickle.dump(web_results,fp)
            
    # do we want to search for exact query web results as well and do some merging?
    if config['include_exact_query_matches'] == 1:
        cache_key = hashlib.md5('"' + q + '"' + search_engine + search_library).hexdigest()
        cache_path = config['web_cache_dir'] + '/' + search_engine + '/' + search_library + '/' + cache_key
        if config['reset_web_cache'] == 0 and os.path.exists(cache_path):
            # continue # uncomment this just to cache a bunch of web results.
            with open(cache_path ,'rb') as fp:
                web_results_exact = pickle.load(fp)
        else:
            web_results_exact = websearch(search_library, search_engine, '"' + q + '"', lim)
            with open(cache_path ,'wb') as fp:
                pickle.dump(web_results_exact,fp)

    # continue # uncomment this just to cache a bunch of web results.

    # Apply Anthony's context filters
    if config['include_exact_query_matches'] == 0:
        # if we don't have to merge in exact query web results than just pass on through
        web_results = apply_filters(web_results, question['question_text'], lim)
    else:
        # If we are combining results, lets filter than independently to maintain weighting by index rank
        # Then merge the results together, remove duplicates, resort and cut the list by the limit.
        web_results = apply_filters(web_results, question['question_text'], lim)
        web_results_exact = apply_filters(web_results_exact, question['question_text'], lim)
        web_results = web_results + web_results_exact

        # lets remove duplicates, keeping the result that has a higher weight.
        filters = qa_filters(web_results, 0)
        web_results = filters.sort_by_weight().results

        results = []
        for r in web_results:
            insert = True;
            for r2 in results:
                if r['title'] == r2['title']:
                    insert = False
                    break
                
            if (insert == True):
                results.append(r)
                
        # at this point we could have less or more than are limit depending on the 
        # results, so lets just cut list by limit so at the least we aren't dealing with more
        web_results = results[:lim]
    return web_results
