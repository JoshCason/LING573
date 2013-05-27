#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Classifier
#
# @author Joshua Cason <casonj@uw.edu>
from __future__ import print_function
import subprocess
import json
import cPickle as cp
from util import checkanswer, getyearbyqid, getquestion
import numpy
from sklearn.feature_extraction import FeatureHasher, DictVectorizer
from sklearn.metrics import classification_report
from sklearn import svm
from config573 import config


"""
***Important***
The only parameter to the constructor is "functionality" which is 
a string that defines the names of the model and vectorizer cache 
files. If you are experimenting with using a classifier in other code
be sure to name it something unique.

examples:
x = classifier.clsfr("question_classification")
x = classifier.clsfr("web_result_reranking")

"""
class clsfr(object):
    def __init__(self, functionality):
        self.modelfilename = config["model_dir"]+functionality+"_model"
        self.vectorizername = config["model_dir"]+functionality+"_vectorizer"
        if functionality == "main":
            self.training_dict = dict()
            self.devtest_dicT = dict()
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
        self.trained = False
        try:
            f = f = open(self.modelfilename,'rb')
            self.rbf_svc = cp.load(f)
            f.close()
            g = open(self.vectorizername,'rb')
            cp.dump(self.dv,g)
            g.close()
            self.trained = True
        except:
            self.rbf_svc = svm.SVC(kernel='rbf', probability=True)
            self.dv = DictVectorizer()
        
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
    def addfeatures(self, qid, ans_cand, feat_dict):
        
        if qid in self.devtest_dict:
            dict_to_update = self.devtest_dict
        else:
            dict_to_update = self.training_dict
        if qid in dict_to_update:
            if ans_cand not in dict_to_update[qid]:
                dict_to_update[qid][ans_cand] = feat_dict
            else:
                for feat in feat_dict:
                    if feat not in dict_to_update[qid][ans_cand]:
                        dict_to_update[qid][ans_cand][feat] = feat_dict[feat]
                    else:
                        msg = "This feature, %s, is already in the feature set of %s.\n"
                        msg = (msg % (feat, ans_cand)) 
                        msg += "Try combining the values earlier in the pipeline or changing the name."
                        raise Exception(msg)
    
    """
    Once you have gathered all the features you like, adding them with the addfeatures method,
    run train() on the object. It takes no input and yields no output. The model is loaded
    into the current object and also cached, so training and devtest can be done separately.
    """
    def train(self, X_dict_list=None, Y_labels=None):
        if X_dict_list is not None and Y_labels is not None: pass
        elif X_dict_list == Y_labels == None:
            X_dict_list,Y_labels = [], []
            for qid in self.training_dict:
                year_str = getyearbyqid(qid)       
                for ac in self.training_dict[qid]:
                    if checkanswer(year_str, qid, ac):
                        label = 1
                    else: label = -1
                    X_dict_list.append(self.training_dict[qid][ac])
                    Y_labels.append(label)
        else: raise Exception("""Either the main pipeline features should be used, in which case,\n 
            supply no arguments, or supply both X_dict_list and Y_labels, please.""")
        X_data = self.dv.fit_transform(X_dict_list)
        self.rbf_svc.fit(X_data,Y_labels)
        f = open(self.modelfilename,'wb')
        cp.dump(self.rbf_svc, f)
        f.close()
        g = open(self.vectorizername,'wb')
        cp.dump(self.dv,g)
        g.close()
        self.trained = True
    
    """
    If no arguments are supplied the test runs on the main pipeline devtest data.
    Otherwise you may supply your own test instances and gold labels.
    
    Of course, the train method must have been run at least once. Models are cached, so
    devtest can be run in a separate session as long as train has been run once before.
    
    For the main pipeline, accuracy and an error dictionary having these keys is stored: 
    
    ans = the answer candidate
    qid = qid
    q = the question
    features = all the features
    
    >>> a_clsfr_object.devtest()
    >>> a_clsfr_object.acc
    some number
    >>> a_clsfr_object.report()
    prints a confusion matrix with precision and recall
    >>> a_clsfr_object.error_indices
    [i,j,...,n]
    >>> a_clsfr_object.error_dict[0]['ans']
    some answer candidate
    
    For other tasks, an error dictionary is not stored, but error indices are (showing where
    in the test instances there were errors)
    
    >>> import classifier
    >>> a_clsfr_object = classifier.clsfr("something_other_than_main")
    >>> X_dict_list = [{1:2,2:3,3:4},{1:3,2:3,3:4}]
    >>> Y_gold = [-1,1] # since this is a binary svm
    >>> a_clsfr_object.train(X_dict_list, Y_gold)
    >>> a_clsfr_object.devtest(X_dict_list, Y_gold)
    array([-1,  1])
    >>> Y_gold
    [-1, 1]

    ... etc.

    """
    def devtest(self, X_dict_list=None, Y_gold=None):
        if not self.trained: raise Exception("train() must be run before testing.") 
        if X_dict_list is not None and Y_gold is not None:
            pass
        elif X_dict_list == Y_gold == None:
            X_dict_list,Y = [], []
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
                    X_dict_list.append(self.devtest_dict[qid][ac])
                    Y.append(label)
            Y_gold = Y
        else: raise Exception("""Either the main pipeline features should be used, in which case,\n 
            supply no arguments, or supply both X_dict_list and Y_gold, please.""")
        X_data = self.dv.fit_transform(X_dict_list)
        Y_model = self.rbf_svc.predict(X_data)
        self.err_indices = filter(lambda x: Y_gold[x] != Y_model[x], range(len(Y_gold)))
        self.error_dict = dict(map(lambda x: (x,error_dict[x]), self.err_indices))
        self.report = lambda : print(classification_report(Y_gold, Y_model))
        self.acc = 1-(float(len(self.err_indices))/float(len(Y_gold)))
        Y_probs = self.rbf_svc.predict_proba(X_data)            
        return zip(Y_model,Y_probs)
        # TODO: figure out how to rank answer candidates not just classify them.
        

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



        
        