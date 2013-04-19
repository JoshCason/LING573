#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Retrieve TREC Quetions
# Example usage: 
# python2.7 trec_questions.py /dropbox/12-13/573/Data/Questions/training/TREC-2005.xml
# 
# XML docs http://docs.python.org/2/library/xml.etree.elementtree.html
# 
# @author Anthony Gentile <agentile@uw.edu>
import os, sys, xml.etree.ElementTree as ET

if __name__ == '__main__':
    trec_file = os.path.realpath(sys.argv[1])
    tree = ET.parse(trec_file)
    root = tree.getroot()
    for target in root.findall('target'):
        target_id = target.attrib['id']
        target_text = target.attrib['text']
        for question in target.findall('qa'):
            q = question.find('q')
            if q.attrib['type'].strip() != 'FACTOID':
                continue
            question_id = q.attrib['id']
            question_text = q.text.strip()
            print(question_text)
            # do some query expansion
            
            # store in easy to parse file?
    
    
    
    
