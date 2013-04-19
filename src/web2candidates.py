#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Retrieve Web Results 
#
# Example usage: 
# python2.7 web2candidates.py reformed_TREC-2005.xml
#
# @author Joshua Cason <casonj@uw.edu>
# @author Anthony Gentile <agentile@uw.edu>
import sys, os, math
import xml.etree.ElementTree as ET
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

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

#bing.search('web','Your Query',params)

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
            
if __name__ == '__main__':
    reformed_trec_file = os.path.realpath(sys.argv[1])
    tree = ET.parse(reformed_trec_file)
    root = tree.getroot()
    for question in root.findall('question'):
        q = question.find('question_target_combined')
        q = q.text
        print q
        
        lim = 4
        c = getcandidates(q, lim)
        # TODO:up the lim and store these in lucene index.
        for r, count in c.most_common(lim):
            print '%s: %7d' % (r, count)
            
        # lets just do the first one for now to not kill our rate quota
        sys.exit()
    




