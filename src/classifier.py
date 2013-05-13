#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Classifier
#
# @author Joshua Cason <casonj@uw.edu>
import subprocess
import json

def runclassifier():
    json_data=open('config')
    config = json.load(json_data)
    json_data.close()
    subprocess.call(config['binarize_cmd'],shell=True)
    subprocess.call(config['train_cmd'],shell=True)
    subprocess.call(config['test_cmd'],shell=True)

