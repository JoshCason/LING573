import reranking
import qc
import util
import numpy as np
import classifier
from webcandidates import getcandidates
import cPickle as cp
from collections import Counter


qids = reduce(lambda x, y: x+y, \
              map(lambda x: util.questions[x].keys(), \
                  filter(lambda y: y not in  ['2006', '10000', '2007'], util.questions)))

TOTAL_QUESTIONS = 592 - 300
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

def train():
    try:
        f = open("pickledwebcandidates",'rb')
        webcandpickled = cp.load(f)
        f.close()
    except:
        webcandpickled = dict()
    qc.train()
    qc_train_clsfr, qc_train_feats = qc.predict(trainq)
    trainqc_dict = dict(zip(trainq, qc_train_clsfr.Y_model))
    search_results = dict()
    for qid in trainq:
        search_results[qid] = util.getplainwebresults(qid)
    webcand_dict = dict()
    for qid, result in search_results.items():
        query = util.getquestion(qid=qid)
        # c = dict of dicts with 'ngram' and 'features'
        qry = "%s %s" % (query['target'], query['question'])
        if qid in webcandpickled:
            c = webcandpickled[qid]
        else:
            c = getcandidates(result, qry, trainqc_dict[qid], qc_train_feats[qid])
            webcandpickled[qid] = c
        webcand_dict[qid] = c
    f = open("pickledwebcandidates",'wb')
    cp.dump(webcandpickled,f)
    f.close()
    for qid, c in webcand_dict.items():
        for ngram in c:
            feats = c[ngram]
            main_clsfr.addfeatures(qid,ngram,feats)
    main_clsfr.train()
    print("done training")
    
def devtest():
    try:
        f = open("pickledwebcandidates",'rb')
        webcandpickled = cp.load(f)
        f.close()
    except:
        webcandpickled = dict()
    qc_test_clsfr, qc_test_feats = qc.predict(testq)
    testqc_dict = dict(zip(testq, qc_test_clsfr.Y_model))
    search_results = dict()
    for qid in testq:
        search_results[qid] = util.getplainwebresults(qid)
    webcand_dict = dict()
    for qid, result in search_results.items():
        query = util.getquestion(qid = qid)
        # c = dict of dicts with 'ngram' and 'features'
        qry = "%s %s" % (query['target'], query['question'])
        if qid in webcandpickled:
            c = webcandpickled[qid]
        else:
            c = getcandidates(result, qry, testqc_dict[qid], qc_test_feats[qid])
            webcandpickled[qid] = c
        webcand_dict[qid] = c
    f = open("pickledwebcandidates",'wb')
    cp.dump(webcandpickled,f)
    f.close()
    for qid, c in webcand_dict.items():
        for ngram in c:
            feats = c[ngram]
            main_clsfr.addfeatures(qid,ngram,feats, False)
    main_clsfr.devtest()
    return main_clsfr 

def evalcandidates(dev=False):
    if dev:
        tempq = evalq
        evalq = devq
    try:
        f = open("pickledwebcandidates",'rb')
        webcandpickled = cp.load(f)
        f.close()
    except:
        webcandpickled = dict()
    qc_eval_clsfr, qc_eval_feats = qc.predict(evalq)
    evalqc_dict = dict(zip(evalq, qc_eval_clsfr.Y_model))
    search_results = dict()
    for qid in evalq:
        search_results[qid] = util.getplainwebresults(qid)
    webcand_dict = dict()
    for qid, result in search_results.items():
        query = util.getquestion(qid = qid)
        # c = dict of dicts with 'ngram' and 'features'
        qry = "%s %s" % (query['target'], query['question'])
        if qid in webcandpickled:
            c = webcandpickled[qid]
        else:
            c = getcandidates(result, qry, evalqc_dict[qid], qc_eval_feats[qid])
            webcandpickled[qid] = c
        webcand_dict[qid] = c
    f = open("pickledwebcandidates",'wb')
    cp.dump(webcandpickled,f)
    f.close()
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
    evalq = tempq
    return output

def run2(k):
    KFEATURES = k
    train()
    results = devtest()
    print(results.report())
    print(results.acc)
    return main_clsfr 

def run3(klist):
    max1 = 0
    maxk = 0
    for k in klist:
        x = run2(k)
        new1 = Counter(x.Y_model)[1]
        if new1 > max1:
            maxk = k
            max1 = new1
    return maxk

def run():
    results = devtest()
    print(results.report())
    return results.acc
    
    