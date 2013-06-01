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
from util import checkanswer, getyearbyqid, getquestion, questions as q
import numpy
from sklearn.feature_extraction import FeatureHasher, DictVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.feature_selection import SelectKBest, chi2
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from config573 import config


VEC_CHOICE = "dv"

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
    def __init__(self, functionality, alg="svm", kfeatures=150):
        self.modelfilename = config["model_dir"]+functionality+"_model"
        self.vectorizername = config["model_dir"]+functionality+"_vectorizer"
        self.chisquaredname = config["model_dir"]+functionality+"_chisquared"
        self.scalername = config["model_dir"]+functionality+"_scaler"
        self.ch2 = SelectKBest(chi2, kfeatures)
        self.scaler = StandardScaler(with_mean=False)
        if functionality == "main":
            self.training_dict = dict()
            self.devtest_dict = dict()
        self.trained = False
        pick_alg = {
                    "svm": lambda : svm.SVC(kernel='rbf', probability=True),
                    "knn": lambda : KNeighborsClassifier(n_neighbors=10, warn_on_equidistant=False)
                    }
        pick_vec = {
                    "fh": lambda : FeatureHasher(),
                    "dv": lambda : DictVectorizer()
                    }
        try:
            f = open(self.modelfilename,'rb')
            self.clsfr_alg = cp.load(f)
            f.close()
            g = open(self.vectorizername,'rb')
            self.vec = cp.load(g)
            g.close()
            h = open(self.chisquaredname,'rb')
            self.ch2 = cp.load(h)
            h.close()
            i = open(self.scalername,'rb')
            self.scaler = cp.load(i)
            i.close()
            self.trained = True
        except:
            print("ack!!")
            self.clsfr_alg = pick_alg[alg]()
            self.vec = pick_vec[VEC_CHOICE]()
        
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
    def addfeatures(self, qid, ans_cand, feat_dict, train=True):
        
        if not train:
            dict_to_update = self.devtest_dict
        else:
            dict_to_update = self.training_dict
        if qid not in dict_to_update:
            dict_to_update[qid] = dict()
        if ans_cand not in dict_to_update[qid]:
            dict_to_update[qid][ans_cand] = feat_dict
        else:
            for feat in feat_dict:
                if feat not in dict_to_update[qid][ans_cand]:
                    dict_to_update[qid][ans_cand][feat] = feat_dict[feat]
#                 else:
#                     msg = "This feature, %s, is already in the feature set of %s.\n"
#                     msg = (msg % (feat, ans_cand)) 
#                     msg += "Try combining the values earlier in the pipeline or changing the name."
#                     raise Exception(msg)
    
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
                    try:
                        if checkanswer(year_str, qid, ac):
                            label = 1
                        else: label = -1
                        X_dict_list.append(self.training_dict[qid][ac])
                        Y_labels.append(label)
                    except: pass
        else: raise Exception("""Either the main pipeline features should be used, in which case,\n 
            supply no arguments, or supply both X_dict_list and Y_labels, please.""")
        X_data = self.vec.fit_transform(X_dict_list)
        X_data = self.ch2.fit_transform(X_data, Y_labels)
        X_data = self.scaler.fit_transform(X_data)
        #X_data = self.fh.fit_transform(X_dict_list)
        self.clsfr_alg.fit(X_data,Y_labels)
        f = open(self.modelfilename,'wb')
        cp.dump(self.clsfr_alg, f)
        f.close()
        g = open(self.vectorizername,'wb')
        cp.dump(self.vec,g)
        g.close()
        h = open(self.chisquaredname,'wb')
        cp.dump(self.ch2, h)
        h.close()
        i = open(self.scalername,'wb')
        cp.dump(self.scaler, i)
        i.close()
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
    list of (classification,[probabilities,...]) pairs (see below)
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
    
    >>> reload(c)
    <module 'classifier' from 'classifier.py'>
    >>> a_clsfr_object = c.clsfr("something_other_than_main")
    >>> X_dict_list = [{1:2,2:3,3:4},{1:3,2:3,3:4}]
    >>> Y_gold = [-1,1] # since this is a binary svm
    >>> a_clsfr_object.train(X_dict_list, Y_gold)
    >>> a_clsfr_object.devtest(X_dict_list, Y_gold)
    [(-1, array([ 0.45098648,  0.54901352])), (1, array([ 0.5489233,  0.4510767]))]
    # obviously, the higher probability refers to the selected class

    If you want to use multiple labels and textual labels, scikit sorts that out for you too.
    
    >>> import classifier as c
    >>> a_clsfr_object = c.clsfr("something_other_than_main")
    >>> X_dict_list = [{1:2,2:3,3:4},{1:3,2:3,3:4}, {1:4,2:3,3:4}]
    >>> Y_gold = ['A','B','C']
    >>> a_clsfr_object.train(X_dict_list, Y_gold)
    >>> a_clsfr_object.devtest(X_dict_list, Y_gold)
    [('A', array([ 0.25777335,  0.31319117,  0.42903547])), ('B', array([ 0.3534678 ,  0.29212005,  0.35441214])), ('C', array([ 0.42954912,  0.31293183,  0.25751905]))]


    """
    def devtest(self, X_dict_list=None, Y_gold=None):
        self.Y_gold = Y_gold
        if not self.trained: raise Exception("train() must be run before testing.") 
        main = False
        if X_dict_list is not None and Y_gold is not None:
            pass
        elif X_dict_list == Y_gold == None:
            main = True
            X_dict_list,Y = [], []
            error_dict = dict()
            for qid in self.devtest_dict:
                year_str = getyearbyqid(qid)       
                for ac in self.devtest_dict[qid]:
                    try:
                        if checkanswer(year_str, qid, ac):
                            label = 1
                        else: label = -1
                        X_dict_list.append(self.devtest_dict[qid][ac])
                        Y.append(label)
                    except: pass
            self.Y_gold = Y
        else: raise Exception("""Either the main pipeline features should be used, in which case,\n 
            supply no arguments, or supply both X_dict_list and Y_gold, please.""")
        X_data = self.vec.transform(X_dict_list)
        X_data = self.ch2.transform(X_data)
        X_data = self.scaler.transform(X_data)
        self.Y_probs = self.clsfr_alg.predict_proba(X_data)
        self.Y_model = list()
        self.results = list()
        for prob in self.Y_probs:
            result = sorted(zip(self.clsfr_alg.classes_, prob), key=lambda x: x[1], reverse=True)
            self.Y_model.append(result[0][0])
            self.results.append(result)
        self.err_indices = filter(lambda x: self.Y_gold[x] != self.Y_model[x], range(len(self.Y_gold)))
        
        # this is for classification report
        labels2ints = {label: i for i, label in enumerate(set(self.Y_gold) | set(self.Y_model))}
        newY_model = map(lambda x: labels2ints[x], self.Y_model) 
        newY_gold = map(lambda x: labels2ints[x], self.Y_gold)
        self.report = lambda : print(classification_report(newY_gold, newY_model)+"\n"+str(labels2ints))
        
        self.acc = 1-(float(len(self.err_indices))/float(len(self.Y_gold)))
        return self.results


        
        
