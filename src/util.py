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


questions = cPickle.load(open("pickledquestions",'rb'))
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
    f = open("pickledanswers",'rb')
    allyears = cPickle.load(f)
    if year_str in allyears:
        patterns = allyears[year_str]
    pct = 0
    while pct < len(patterns[qid].patts):
        if re.search(patterns[qid].patts[pct],ans_str) >= 0:
            if (mrr_type != 'strict') or ((mrr_type == 'strict') and  (docno in patterns[qid].doclists[pct])):
                return True
        pct += 1
    return False




