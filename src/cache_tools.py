from webcandidates import websearch, clean_results
from config573 import config
import re
import cPickle
from cached_resources import pattern 

"""
Stole most of this code from compute_mrr.py written by UW faculty/TAs

 I used this to get the pickledanswers file.
Since we have the answers pickled now, this function will
probably not be useful

I updated it when I thought i'd need it again, and then didn't need it.
Hasn't been tested, but should work. Pass in the path to the directory
holding the training and devtest patterns. I supplied the patas default.
Make sure to put the / at the end of the path string.

-j
""" 
def getanswerpatterns(path_to_patterns_dir='/dropbox/12-13/573/Data/patterns/'):
    
    p = path_to_patterns_dir
    patt_files = {'2006': p +'devtest/factoid-docs.litkowski.2006.txt',
     '2004': p +'training/factoid-docs.litkowski.2004.txt',
     '2005': p +'training/factoid-docs.litkowski.2005.txt',
     '2001': p +'training/factoid-docs.litkowski.2001.txt'}
    all_patterns = dict()
    for patt_file in patt_files:
        patt_f = open(patt_files[patt_file],'r')
        patterns = dict()
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
        all_patterns[patt_file] = patterns
        patt_f.close()
    return all_patterns

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
google result 1 for 2004 qid 35.3 would be results['2004']['35.3']['google'][0]

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
        rfile = open("pickledplainwebresults",'wb')
    except:
        raise Exception("missing pickledplainwebresults file!")
        #rfile = open("pickledplainwebresults",'wb')
    for year in q:
        if year not in r:
            r[year] = q[year]
        key = config["search_engine_active"]
        qids = q[year].keys() 
        missing = set(findmissing())
        for qid in qids:
            if qid == '260.4':
                print("found it!")
            qkey = key + "_" + qid
            if qkey not in r[year] or qid in missing: 
                question = r[year][qid]['question']
                target = r[year][qid]['target']
                qry = "%s %s" % (target, question)
                r[year][qid][key] = dict()
                try:
                    results = clean_results(websearch(qry))
                except:
                    print("qid:%s, %s" % (qid, qry))
                    cp.dump(r,rfile)
                    rfile.close()
                    raise
                for i,result in enumerate(results):
                    # not really sure why I didn't just dump the
                    # list in there. maybe will fix it, but works
                    # for now.
                    r[year][qid][key][i] = result 
                r[year][qkey] = True
            countdown -= 1
            #print str(countdown) + " to go,",
    cp.dump(r,rfile)
    rfile.close()
    return r

"""
this function checks if there are any missing web results
"""    
def findmissing():
#   cp = cPickle
#     rfile = open("pickledplainwebresults",'rb')
#     r = cp.load(rfile)
#     rfile.close()
    missing = []
    for year in r:
        for qid in r[year]:
            if not type(r[year][qid]) == bool:
                if 'google' in r[year][qid]:
                    if r[year][qid]['google'] == {}:
                        missing.append(qid)
                else: print("ack!!!")
    return missing