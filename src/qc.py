import classifier
import util
from util import qc, getquestion
from trainQueryFeatures import featurize
import numpy as np

NUM_OF_QUESTIONS = 3000

np.random.seed(0)
indices = np.random.permutation(len(qc))
qids = qc.keys()
qids = map(lambda x: qids[x], indices)[:NUM_OF_QUESTIONS] 
percent = int(len(qids) * 0.1)
trainq = qids[percent:]
testq = qids[:percent]

qc_classifier = classifier.clsfr("question_classification", alg="svm",kfeatures=2250)

def train(): 
    X,Y = [],[]
    for qid in trainq:
        target = getquestion(qid=qid)['target']
        question = getquestion(qid=qid)['question']
        features = featurize(target, question) # your function
        label = qc[qid].split(':')[0]
        X.append(features)
        Y.append(label)
    qc_classifier.train(X,Y)
    
def devtest():
    X,Y = [],[]
    for qid in testq:
        target = getquestion(qid=qid)['target']
        question = getquestion(qid=qid)['question']
        features = featurize(target, question) # your function
        label = qc[qid].split(':')[0]
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
        label = qc[qid].split(':')[0]
        features_dict[qid] = features
        X.append(features)
        Y.append(label)
    Y_model = qc_classifier.devtest(X,Y)
    return Y_model, features_dict