#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Classifier
#
# @author Joshua Cason <casonj@uw.edu>
import subprocess
import json
import cPickle as cp
from util import checkanswer, getyearbyqid, getquestion
import numpy
from sklearn.feature_extraction import FeatureHasher, DictVectorizer
from sklearn import svm


"""

"""
class clsfr():
    def __init__(self):
        self.training_dict = dict()
        self.devtest_dicT = dict()
        try:
            f = f = open(config["model_dir"]+"main_model",'rb')
            self.rbf_svc = cp.load(f)
            f.close()
        except:
            self.rbf_svc = svm.SVC(kernel='rbf')
        try:
            g = open(config["model_dir"]+"vectorizer",'wb')
            cp.dump(self.dv,g)
            g.close()
        except:
            self.dv = DictVectorizer()
        qfile = open("pickledquestions",'rb')
        self.q = cp.load(qfile)
        qfile.close()
        for year in self.q:
            if year == '2006':
                for qid in self.q[year]:
                    self.devtest_dict[qid] = dict()
            else:
                for qid in self.q[year]:
                    self.training_dict[qid] = dict()
        
    """
    Since in all of our current questions, the qid is unique, there
    is no need to include the year.
    
    If you'd like to add features to a certain answer candidate for a 
    certain qid, you can add them at any point in the pipeline with this
    method.
    
    If the feature is already present, then you should sort out how to
    combine the results elsewhere. It's difficult to guess how to deal with
    duplicate features because their values might be string or numerical.
    """
    def addfeatures(qid, ans_cand, feat_dict):
        if qid in self.devtest_dict:
            if ans_cand not in devtest_dict[qid]:
                self.devtest_dict[qid][ans_cand] = feat_dict
            else:
                for feat in feat_dict:
                    if feat not in self.devtest_dict[qid][ans_cand]:
                        self.devtest_dict[qid][ans_cand][feat] = feat_dict[feat]
                    else:
                        msg = "This feature, %s, is already in the feature set of %s.\n"
                        msg = (msg % (feat, ans_cand)) 
                        msg += "Try combining the values earlier in the pipeline or changing the name."
                        raise msg
        else:
            if ans_cand not in self.training_dict[qid]:
                self.training_dict[qid][ans_cand] = feat_dict
            else:
                for feat in feat_dict:
                    if feat not in self.training_dict[qid][ans_cand]:
                        self.training_dict[qid][ans_cand][feat] = feat_dict[feat]
                    else:
                        msg = "This feature, %s, is already in the feature set of %s.\n"
                        msg = (msg % (feat, ans_cand)) 
                        msg += "Try combining the values earlier in the pipeline or changing the name."
                        raise msg
    
    """
    Once you have gathered all the features you like, adding them with the addfeatures method,
    run train() on the object. It takes no input and yields no output. The model is loaded
    into the current object and also cached, so training and devtest can be done separately.
    """
    def train():
        X,Y = [], []
        for qid in self.training_dict:
            year_str = getyearbyqid(qid)       
            for ac in self.training_dict[qid]:
                if checkanswer(year_str, qid, ac):
                    label = 1
                else: label = -1
                X.append(self.training_dict[qid][ac])
                Y.append(label)
        Y = numpy.ndarray(Y)
        X_data = self.dv(X)
        self.rbf_svc.fit(X,Y)
        f = open(config["model_dir"]+"main_model",'wb')
        cp.dump(self.rbf_svc, f)
        f.close()
        g = open(config["model_dir"]+"vectorizer",'wb')
        cp.dump(self.dv,g)
        g.close()
    
    """
    returns accuracy and an error dictionary having these keys: 
    
    ans = the answer candidate
    qid = qid
    q = the question
    features = all the features
    
    call it like this:
    acc, err_dict = a_clsfr_object.devtest()
    
    Of course, the train method must have been run at least once. Models are cached, so
    devtest can be run in a separate session as long as train has been run once before.
    """
    def devtest(self):
        X,Y = [], []
        error_dict = dict()
        for qid in self.devtest_dict:
            year_str = getyearbyqid(qid)       
            for i,ac in enumerate(self.devtest_dict[qid]):
                error_dict[i] = \
                {"ans" : ac,"qid": qid, "q": getquestion(year_str, qid), \
                 "features" : self.devtest_dict[qid][ac]}
                if checkanswer(year_str, qid, ac):
                    label = 1
                else: label = -1
                X.append(self.devtest_dict[qid][ac])
                Y.append(label)
        Y_gold = numpy.ndarray(Y)
        X_data = self.dv(X)
        Y_model = self.rbf_svc.predict(X_data)
        err_indices = filter(lambda x: Y_gold[x] != Y_data[x], range(len(Y_gold)))
        acc = float(err_indices)/float(len(Y_gold))
        return acc, dict(map(lambda x: (x,error_dict[x]), err_indices))
        

"""
from when I was going to use mallet.
"""
def runclassifier():
    json_data=open('config')
    config = json.load(json_data)
    json_data.close()
    subprocess.call(config['binarize_cmd'],shell=True)
    subprocess.call(config['train_cmd'],shell=True)
    subprocess.call(config['test_cmd'],shell=True)



        
        