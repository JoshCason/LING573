import classifier
import util
from util import qc, getquestion
from trainQueryFeatures import featurize
import numpy as np
import cPickle as cp

# negative one is basically all of them
NUM_OF_QUESTIONS = -1

np.random.seed(0)
indices = np.random.permutation(len(qc))
qids = qc.keys()
qids = map(lambda x: qids[x], indices)[:NUM_OF_QUESTIONS] 
percent = int(len(qids) * 0.1)
trainq = qids[percent:]
testq = qids[:percent]

qc_classifier = classifier.clsfr("question_classification", alg="svm",kfeatures=3000)

def qcpipeline(theqids, predict=False):
    try:
        f = open("pickledquestionfeats",'rb')
        pickledquestionfeats = pickle.load(f)
        f.close()
    except:
        pickledquestionfeats = dict()
    features_dict = dict()
    X,Y = [],[]
    for qid in theqids:
        target = getquestion(qid=qid)['target']
        question = getquestion(qid=qid)['question']
        features, pickledquestionfeats = featurize(target, question, pickledquestionfeats) # your function
        features_dict[qid] = features
        if not predict:
            label = qc[qid].split(':')[0]
            Y.append(label)
        else:
            Y.append('NUM')
        X.append(features)
    f = open("pickledquestionfeats",'wb')
    cp.dump(pickledquestionfeats,f)
    f.close()
    return X,Y,features_dict

def train(): 
    X,Y,feats = qcpipeline(trainq)
    qc_classifier.train(X,Y)
    
def devtest():
    X,Y,feats = qcpipeline(testq)
    qc_classifier.devtest(X,Y)
    return qc_classifier

def predict(new_qids):
    X,Y,feats = qcpipeline(new_qids, True)
    qc_classifier.devtest(X,Y)
    return qc_classifier, feats

def run():
    train()
    results = devtest()
    return results.acc