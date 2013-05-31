#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Utility functions
#
# @author Joshua Cason <casonj@uw.edu>
import cPickle
import re
import xml.etree.ElementTree as ET
from nltk import word_tokenize, PorterStemmer
import string
from cached_resources import questions, r, anspatterns

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
Give it a question id and get back which year it was asked.
"""
def getyearbyqid(qid):
    return filter(lambda x: qid in questions[x],questions)[0]

"""
pass in a year and get back a dictionary of dictionaries.

In each sub-dictionary:
Each question id picks out a dictionary which contains "target" and 
"question" keys. "target" is the topic for several questions such as
"Warren Moon". "question" is the actual question text.

If you pass a year and a question id to the function, you get back
just one of those question dictionaries with "target" and "question"
keys.

>>> getquestion('2004', '35.2')
{'question': 'How many years was he with GE?', 'target': 'Jack Welch'}

The same works without the year:
>>> getquestion(qid='35.2')
{'question': 'How many years was he with GE?', 'target': 'Jack Welch'}

with just the year:
>>> getquestion('2004')['35.2']
{'question': 'How many years was he with GE?', 'target': 'Jack Welch'}

with just the year:
>>> getquestion('2004')['35.2']['question']
'How many years was he with GE?'

"""
def getquestion(year=None, qid=None):
    if qid == None:
        return questions[year]
    elif qid != None and year != None:
        return questions[year][qid]
    else:
        return questions[getyearbyqid(qid)][qid]

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

__call__ is when you use an instance of the class as a method
>>> t = Tokenizer()
>>> toked = t(sentence)

stem_toke also stems the token.
>>> t = Tokenizer()
>>> toked = t.stem_toke(sentence)

"""
class Tokenizer(object):
    def __init__(self):
        self.stem = PorterStemmer()
        self.punct = set(string.punctuation) | set(['..','...','....','.....','......'])
    def __call__(self, doc):
        return [t for t in word_tokenize(doc) if t not in self.punct]
    def stem_toke(self, doc):
        return [self.stem.stem(t) for t in word_tokenize(doc) if t not in self.punct]

"""
get your plain results, already cached.

>>> util.getplainwebresults('260.4')[0]
{'description': u'Ninja Turtles: The Next Mutation is an American live-action television series produced
by Saban Entertainment, which ran on the Fox Kids network from 1997 to 1998. ... introduced many new
elements to the Teenage Mutant Ninja Turtles saga. ... TMNT continuities, Leonardo states in the second episode
that the Turtles are ...', 'title': u'Ninja Turtles: The Next Mutation - Wikipedia, the free encyclopedia'}
>>> util.getquestion(qid='260.4')
{'question': 'What television network carried TMNT?', 'target': 'Teenage Mutant Ninja Turtles (TMNT)'}

"""
def getplainwebresults(qid, engine='google'):
    year = getyearbyqid(qid)
    if 'google' in r[year][qid]:
        # this part is stupid, but I didn't realize I had designed it
        # stupidly until I had already cached a bunch of results
        result = []
        for i in range(len(r[year][qid][engine])):
            result.append(r[year][qid][engine][i])
        return result

