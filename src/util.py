#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Utility functions
#
# @author Joshua Cason <casonj@uw.edu>
import cPickle
import re
from config573 import config
import xml.etree.ElementTree as ET
from webcandidates import websearch, clean_results
from nltk import word_tokenize, PorterStemmer
import string

f = open("pickledquestions",'rb')
questions = cPickle.load(f)
f.close()
f = open("pickledanswers",'rb')
ans_patterns = cPickle.load(f)
f.close()

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

# treats Litkowski patterns as arrays of patts and doclists
# where patts are regular expression patterns that match correct answers
# and  doclist are list of docnos in which those patterns are valid
class pattern:
    def __init__(self,patt,doclist):
        self.patts = []
        self.patts.append(patt)
        self.doclists = []
        self.doclists.append(doclist)

"""
Stole most of this code from compute_mrr.py written by UW faculty/TAs

 I used this to get the pickledanswers file.
Since we have the answers pickled now, this function will
probably not be useful
-j
""" 
def getanswerpatterns(patt_file):
    
    patt_f = open(patt_file,'r')

    patterns = {}

    # Collect patters from pattern files
    for pattline in patt_f.readlines():
        pattline = pattline[:-1]
        parts = re.split('\s+',pattline)
        if len(parts) > 2:
            qid = parts[0]
            patt = ''
            partct = 1
            while partct < len(parts) and parts[partct].find('APW') < 0 and parts[partct].find('XIE') < 0 and parts[partct].find('NYT') < 0:
                patt += parts[partct]+'\s*'
                partct += 1
            doclist = []
            while partct < len(parts):
                doclist.append(parts[partct])
                partct += 1
            if patterns.has_key(qid):
                patterns[qid].patts.append(patt)
                patterns[qid].doclists.append(doclist)
            else:
                patterns[qid] = pattern(patt,doclist)
    patt_f.close()
    return patterns

"""
Used this to pickle all the questions except year 2001 because
the xml parser barfed. To use that data we'll have to alter the 
file a little. 

Basically stole this code from reform_trec_questions though it's
a little different.

Once we solidify our query modifications, it would be wise to pickle
those in the pickledquestions dictionary too.
"""
def getquestions(trec_file):
    tree = ET.parse(trec_file)
    root = tree.getroot()
    
    q_dict = dict()
    for target in root.findall('target'):
        targettext = target.attrib['text']
        for question in target.findall('qa'):
            q = question.find('q')
            if q.attrib['type'].strip() != 'FACTOID':
                continue
            qid = q.attrib['id']
            q_dict[qid] = dict()
            q_dict[qid]['target'] = targettext
            q_dict[qid]['question'] = q.text.strip()
    return q_dict

"""
pass in a year and get back a dictionary of dictionaries.
Each question id picks out a dictionary which contains "target" and 
"question" keys. "target" is the topic for several questions such as
"Warren Moon". "question" is the actual question text.

If you pass a year and a question id to the function, you get back
just one of those question dictionaries with "target" and "question"
keys.

>>> getquestion('2004', '35.2')
{'question': 'How many years was he with GE?', 'target': 'Jack Welch'}

"""
def getquestion(year, qid=None):
    if qid == None:
        return questions[year]
    else:
        return questions[year][qid]

"""
Stole most of this code from compute_mrr.py written by UW faculty/TAs

You can use util.checkanswer to check whether a string contains
an acceptable answer. You must supply the year (2001,2004,2005,or
2006) and the question id. Doc number is optional if you want to
test lucene.

Returns True or False (type bool).

>>> import util
>>> util.checkanswer('2004','5.2','1958')
True
>>> util.checkanswer('2004','5.2','1956')
True
>>> util.checkanswer('2004','5.2','1956','NYT19980720.0082')
True
>>> util.checkanswer('2004','5.2','1956','NYT20000519.0335')
True
>>> util.checkanswer('2004','5.2','1956','NYT20000908.0136')
False
>>> util.checkanswer('2004','5.2','1957')
False
>>> util.checkanswer('2004','5.2','1952')
False
>>> util.checkanswer('2004','5.2','isdvufv 1956')
True
>>> util.checkanswer('2004','5.2','isdvufv 1956 sdibdfg')
True
>>> util.checkanswer('2004','5.2','isdvufv 1956sdibdfg')
True
"""
def checkanswer(year_str,qid_str,ans_str, docno=None):
    mrr_type = ''
    if docno == None:
        mrr_type = 'lenient'
    else: mrr_type = 'strict'
    qid = qid_str
    if year_str in ans_patterns:
        patterns = ans_patterns[year_str]
    pct = 0
    while pct < len(patterns[qid].patts):
        if re.search(patterns[qid].patts[pct],ans_str) >= 0:
            if (mrr_type != 'strict') or ((mrr_type == 'strict') and  (docno in patterns[qid].doclists[pct])):
                return True
        pct += 1
    return False

"""
Give it a question id and get back which year it was asked.
"""
def getyearbyqid(qid):
    return filter(lambda x: qid in questions[x],questions)[0]

"""
util.cache_plain_web_results

plain means nothing was done to the question except prepending
the target.

goes through 2004, 2005, 2006 questions and caches their cleaned 
results. Will store results separately for different search engines 

how to look up results:
unpickle pickledplainwebresults
you need to know the year, the qid, and the search engine. Then you 
get a dictionary with keys 1-n where n is the number of results we 
retrieved for that search engine (which differs, so use len() if necessary).

if "results" is the name of the unpickled dictionary:
google result 1 for 2004 qid 35.3 would be results['2004']['35.3']['google'][1]

**Important** If you get throttled in the middle of a run, the results
that did get returned will get cached. the algorithm will skip over those
questions the next time and not search them again. That way you can change
the config to use someone else's key or up your billing limits.
"""
def cache_plain_web_results():
    cp = cPickle
    q = questions
    countdown = len(reduce(lambda x,y: x+y,map(lambda x: q[x].values(),q)))
    try:
        rfile = open("pickledplainwebresults",'rb')
        q = cPickle.load(rfile)
        rfile.close()
    except:
        rfile = open("pickledplainwebresults",'wb')
    for year in q:
        key = config["search_engine_active"]
        qids = q[year].keys() 
        for qid in qids:
            qkey = key + "_" + qid
            if qkey not in q[year]: 
                question = q[year][qid]['question']
                target = q[year][qid]['target']
                qry = "%s %s" % (target, question)
                q[year][qid][key] = dict()
                try:
                    r = clean_results(websearch(qry))
                except:
                    print("qid:%s, %s" % (qid, qry))
                    cp.dump(q,rfile)
                    rfile.close()
                    raise
                for i,result in enumerate(r):
                    q[year][qid][key][i] = result
                q[year][qkey] = True
            countdown -= 1
            print(str(countdown) + " to go")
    cp.dump(q,rfile)
    rfile.close()
    return q

"""

__call__ is when you use an instance of the class as a method
>>> st = StemTokenizer()
>>> tokedNstemmed = st(sentence)

"""
class StemTokenizer(object):
    def __init__(self):
        self.stem = PorterStemmer()
        self.punct = set(string.punctuation) | set(['..','...','....','.....'])
    def __call__(self, doc):
        return [self.stem.stem(t) for t in word_tokenize(doc) if t not in self.punct]
    
"""
this function checks if there are any missing web results
"""    
def f():
    cp = cPickle
    rfile = open("pickledplainwebresults",'rb')
    r = cp.load(rfile)
    rfile.close()
    try:
        del r['comment']
    except: pass 
    missing = []
    for year in r:
        for qid in r[year]:
            if not type(r[year][qid]) == bool:
                if 'google' in r[year][qid]:
                    if r[year][qid]['google'] == {}:
                        missing.append(qid)
                else: print("ack!!!")
    return missing
    

