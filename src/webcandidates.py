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
import HTMLParser
from util import Tokenizer

my_key = 'cvzWROzO9Vaxqu0k33+y6h++ts+a4PLQfvA7HlyJyXM='
bing = BingSearchAPI(my_key)

sys.path.insert(0, os.path.join("..", ".."))

from xgoogle.search import GoogleSearch, SearchError

from pattern.web import Google, Bing, asynchronous, plaintext
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
def websearch(query):
    limit = config['web_results_limit']
    search_library = config['search_library_active']
    search_engine = config['search_engine_active']
    
    ret = []
    # Bing=50 per page, Google=10 - go figure!
    per_page = config[search_engine + '_per_page']
    pages = int(math.ceil(limit / float(per_page)))

    if search_library == 'pattern':
        if search_engine == 'bing':
            engine = Bing(license='cvzWROzO9Vaxqu0k33+y6h++ts+a4PLQfvA7HlyJyXM=', language="en")
        elif search_engine == 'google':
            engine = Google(license=config[config['use_whose_key'] + '_google_key'], language="en")
        for page in range(pages):
            try:
                # turns out start = starting page and count is results per page
                # could probably do some logic to make sure count is right if limit was 130, on page 3, count should be 30, whereas 
                # our code is going to fetch 50 for a total of 150. ... I think we can probably mess with that later and just work in blocks of 50
                request = asynchronous(engine.search, clean_query(query), start=page+1, count=per_page, type=SEARCH, timeout=10, throttle=0.5)
                while not request.done:
                    time.sleep(0.01)
            except:
                raise
            if request.value != None:
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

useUnion = False
# gather up n-grams from our web search reslts
def getcandidates(search_results, query, label, qfeatures, qid, pickledngrams):

    tokenizer = Tokenizer()
    qa = qa_filters([])
    stop_words = set(stopwords.words('english')) | set(["'s"])
    punct = set(string.punctuation + '·™')
    
    if qid in pickledngrams:
        ngrams = pickledngrams[qid]
    else:
        ngrams = Counter()
    
    ngram_featset = dict()
    result_features = dict()
    for result_key, result in enumerate(search_results):
        result_features[result_key] = set(qa.featurizeWebResult(label,result,1).items())
        text = "%s ... %s" % (result['title'], result['description'])
        texts = text.split('...')
        toked = []
        for t in texts:
            if config['search_library_active'] == 'xgoogle':
                tokes = tokenizer(t.decode('utf8'))
            else:
                tokes = tokenizer(t)
            toked.append(tokes)
        for tokens in toked:
            bigrams = map(lambda x: ' '.join(x), bigramize(tokens))
            trigrams = map(lambda x: ' '.join(x), trigramize(tokens))
            quadrigrams = map(lambda x: ' '.join(x), quadrigramize(tokens))
            
            for ng in tokens+bigrams+trigrams+quadrigrams:
                #ngrams[token] += result['weight']
                if qid not in pickledngrams:
                    ngrams[ng] += 1
                if ng in ngram_featset:
                    ngram_featset[ng].add(result_key)
                else:
                    ngram_featset[ng]= set([result_key])
    if qid not in pickledngrams:
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
    finalfeatdict = dict()
    for ng, chunk in ngrams.most_common(30):
        if useUnion:
            feats = reduce(lambda x,y: x | y, map(lambda z: result_features[z], ngram_featset[ng]))
        else:
            feats = reduce(lambda x,y: x & y, map(lambda z: result_features[z], ngram_featset[ng]))
        feats.add(('REDUNDANCY_SCORE',ngrams[ng]))
        feats.add(('WEB_RANK', 1 + min(ngram_featset[ng])))
        feats.add(('QC_LABEL', label))
        finalfeatdict[ng] = dict(feats | set(qa.featurizeCandidate(label, ng, 0).items()) | set(qfeatures.items()))
        #finalfeatdict[ng] = dict(feats | set(qa.featurizeCandidate(label, ng, 0).items()))
    return finalfeatdict, ngrams
    
def clean_results(results):
    # we want to remove html tags and decode html entities for titles and descriptions
    h = HTMLParser.HTMLParser()
    for result in results:
        result['title'] = h.unescape(re.sub('<[^<]+?>', '', result['title']))
        result['description'] = h.unescape(re.sub('<[^<]+?>', '', result['description']))
        
    return results

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
        web_results = websearch(q)
        with open(cache_path ,'wb') as fp:
            pickle.dump(web_results,fp)
            
    web_results = clean_results(web_results)
            
    # do we want to search for exact query web results as well and do some merging?
    if config['include_exact_query_matches'] == 1:
        cache_key = hashlib.md5('"' + q + '"' + search_engine + search_library).hexdigest()
        cache_path = config['web_cache_dir'] + '/' + search_engine + '/' + search_library + '/' + cache_key
        if config['reset_web_cache'] == 0 and os.path.exists(cache_path):
            # continue # uncomment this just to cache a bunch of web results.
            with open(cache_path ,'rb') as fp:
                web_results_exact = pickle.load(fp)
        else:
            web_results_exact = websearch('"' + q + '"')
            with open(cache_path ,'wb') as fp:
                pickle.dump(web_results_exact,fp)
                
        web_results_exact = clean_results(web_results_exact)

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
