import classifier
import util
from util import qc, getquestion
from trainQueryFeatures import featurize
import numpy as np

np.random.seed(0)
indices = np.random.permutation(len(qc))
qids = qc.keys()
qids = map(lambda x: qids[x], indices) 
twentypercent = int(len(qids) * 0.2)
trainq = qids[twentypercent:]
testq = qids[:twentypercent]

qc_classifier = classifier.clsfr("question_classification", kfeatures=150)

def train(): 
    X,Y = [],[]
    for qid in trainq:
        target = getquestion(qid=qid)['target']
        question = getquestion(qid=qid)['question']
        features = featurize(target, question) # your function
        label = qc[qid]
        X.append(features)
        Y.append(label)
    qc_classifier.train(X,Y)
    
def devtest():
    X,Y = [],[]
    for qid in testq:
        target = getquestion(qid=qid)['target']
        question = getquestion(qid=qid)['question']
        features = featurize(target, question) # your function
        label = qc[qid]
        X.append(features)
        Y.append(label)
        qc_classifier.devtest(X,Y)
    return qc_classifier

def predict(new_qids):
    features_dict = dict()
    X,Y = [],[]
    for qid in new_qids:
        target = getquestion(qid=qid)['target']
        question = getquestion(qid=qid)['question']
        features = featurize(target, question) # your function
        label = qc[qid]
        features_dict[qid] = features
        X.append(features)
        Y.append(label)
    Y_model = qc_classifier.devtest(X,Y)
    return Y_model, features_dict