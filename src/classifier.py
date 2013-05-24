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
from util import checkanswer, getyearbyqid
import numpy
from sklearn.feature_extraction import FeatureHasher, DictVectorizer
from sklearn import svm


"""

"""
class clsfr():
    def __init__(self):
        self.training_dict = dict()
        self.devtest_dicT = dict()
        self.dv = DictVectorizer()
        self.rbf_svc = svm.SVC(kernel='rbf')
        qfile = open("pickledquestions",'rb')
        q = cp.load(qfile)
        qfile.close()
        for year in q:
            if year == '2006':
                for qid in q[year]:
                    self.devtest_dict[qid] = dict()
            else:
                for qid in q[year]:
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
        f = open(config["main_model"],'wb')
        cp.dump(self.rbf_svc, f)
        f.close()
    
    def devtest(self):
        X,Y = [], []
        for qid in self.devtest_dict:
            year_str = getyearbyqid(qid)       
            for ac in self.devtest_dict[qid]:
                if checkanswer(year_str, qid, ac):
                    label = 1
                else: label = -1
                X.append(self.devtest_dict[qid][ac])
                Y.append(label)
        Y = numpy.ndarray(Y)
        X_data = self.dv(X)
        

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



        
        