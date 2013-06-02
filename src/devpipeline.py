import reranking
import qc
import util
import numpy as np
import classifier
from webcandidates import getcandidates
import cPickle as cp
from collections import Counter
from config573 import config

qids = reduce(lambda x, y: x+y, \
              map(lambda x: util.questions[x].keys(), \
                  filter(lambda y: y not in  ['2006', '10000', '2007'], util.questions)))

TOTAL_QUESTIONS = 592
NUM_OF_QUESTIONS = TOTAL_QUESTIONS
PERCENT = 0.1 # of data for testing
KFEATURES = 50

main_clsfr = classifier.clsfr("main", alg="svm",kfeatures=KFEATURES)

evalq = util.questions['2007'].keys()
devq = util.questions['2006'].keys()

np.random.seed(0)
indices = np.random.permutation(len(qids))
qids = map(lambda x: qids[x], indices)[:NUM_OF_QUESTIONS] 
portion = int(len(qids) * PERCENT)
trainq = qids[portion:]
testq = qids[:portion]

def dopipeline(qidsq):
    try:
        f = open("pickledwebcandidates"+marker,'rb')
        webcandpickled = cp.load(f)
        f.close()
        #raise
    except:
        webcandpickled = dict()
    try:
        f = open("pickledngrams1"+marker,'rb')
        pickledngrams = pickle.load(f)
        f.close()
    except:
        pickledngrams = dict()
    qc_qids_clsfr, qc_qids_feats = qc.predict(qidsq)
    qidsqc_dict = dict(zip(qidsq, qc_qids_clsfr.Y_model))
    search_results = dict()
    for qid in qidsq:
        search_results[qid] = util.getplainwebresults(qid)
    webcand_dict = dict()
    for qid, result in search_results.items():
        query = util.getquestion(qid=qid)
        # c = dict of dicts with 'ngram' and 'features'
        qry = "%s %s" % (query['target'], query['question'])
        if qid in webcandpickled:
            c = webcandpickled[qid]
        else:
            c, ngrams = getcandidates(result, qry, qidsqc_dict[qid], qc_qids_feats[qid], qid, pickledngrams)
            webcandpickled[qid] = c
            pickledngrams[qid] = ngrams
        webcand_dict[qid] = c
    f = open("pickledwebcandidates"+marker,'wb')
    cp.dump(webcandpickled,f)
    f.close()
    f = open("pickledngrams"+marker,'wb')
    cp.dump(pickledngrams, f)
    f.close()
    return webcand_dict

def train():
    #qc.train() # we can assume this is trained
    webcand_dict = dopipeline(trainq)
    for qid, c in webcand_dict.items():
        for ngram in c:
            feats = c[ngram]
            main_clsfr.addfeatures(qid,ngram,feats)
    main_clsfr.train()
    print("done training")
    
def devtest():
    webcand_dict = dopipeline(testq)
    for qid, c in webcand_dict.items():
        for ngram in c:
            feats = c[ngram]
            main_clsfr.addfeatures(qid,ngram,feats, False)
    main_clsfr.devtest()
    return main_clsfr 

def evalcandidates(year):
    global evalq
    if year == '2006':
        dev = True
    else:
        dev = False
    tempq = None
    if dev:
        tempq = evalq
        evalq = devq
    webcand_dict = dopipeline(evalq)
    X, Y = [],[]
    cand_indexing = dict()
    index = 0
    for qid, c in webcand_dict.items():
        cand_indexing[qid] = dict()
        for ngram in c:
            X.append(c[ngram])
            Y.append(1)
            cand_indexing[qid][ngram] = index
            index += 1
    results = main_clsfr.devtest(X,Y)
    output = dict()
    for qid in evalq:
        output[qid] = Counter()
        for ngram in cand_indexing[qid]:
            probs = dict(results[cand_indexing[qid][ngram]])
            output[qid][ngram] = probs[1]
    if dev:
        evalq = tempq
    return output

def run2(k):
    global main_clsfr
    KFEATURES = k
    main_clsfr = classifier.clsfr("main", alg="svm",kfeatures=KFEATURES)
    train()
    results = devtest()
    print(results.report())
    print(results.acc)
    return main_clsfr 

def run3(klist):
    max1 = 0
    maxk = 0
    for k in klist:
        output = run4(k)
        distotal = 0
        distct = 0
        for qid in output:
            x = output[qid].most_common()
            dist = abs(x[0][1] - x[-1][1])
            distotal += dist
            distct +=1
        new1 = distotal / float(distct)
        #new1 = Counter(main_clsfr.Y_model)[1]
        if new1 > max1:
            maxk = k
            max1 = new1
    return maxk

def run4(k):
    KFEATURES = k
    main_clsfr = classifier.clsfr("main", alg="svm",kfeatures=KFEATURES)
    train()
    return evalcandidates()

def run():
    results = devtest()
    print(results.report())
    return results.acc
    
    