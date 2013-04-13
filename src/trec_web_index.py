#!/usr/bin/python
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Example Web Search Using CLiPS
#
# @author Anthony Gentile <agentile@uw.edu>
import os, sys; sys.path.insert(0, os.path.join("..", ".."))

from pattern.web import Google, plaintext
from pattern.web import SEARCH

import sunburnt

# We are running a multicore setup. Sepcify which core.
SOLR_CORE = 'dev'

SOLR_SCHEMA_PATH = os.path.dirname(os.path.realpath(__file__)) + '/apache-solr-3.6.2/573/multicore/' + SOLR_CORE + '/conf/schema.xml'

si = sunburnt.SolrInterface("http://localhost:8983/solr/" + SOLR_CORE, SOLR_SCHEMA_PATH)

# If any schema changes were made, lets pick them up
si.init_schema()

# Delete all documents from the index
si.delete_all()

# Setup CLiPS
engine = Google(license=None, language="en")

# Fetch some TREC questions
TREC_TRAIN = os.path.dirname(os.path.realpath(__file__)) + '/Data/Questions/training/TREC-2001.xml'

f = open(TREC_TRAIN)
train_lines = f.readlines()
f.close()

# Dumb TREC file parsing for questions
questions = []

i = 0
for line in train_lines:
    if '<desc>' in line:
        questions.append(train_lines[i+1].strip())
    i += 1

# Just do the first five questions. Shove the first google result snippet as the answer into our Lucene Index
doc_id = 1
for q in questions[:5]:
    # Google is very fast but you can only get up to 100 (10x10) results per query.
    for i in range(1,2):
        for result in engine.search(q, start=i, count=2, type=SEARCH):
            # here is where we would do some processing to the google results to try to get our answer
            # and add it to our index accordingly. We will be tweaking the Lucene Index Schema to 
            # store/factor in web results
            si.add({"id":doc_id,"question":q,"answer":plaintext(result.text)})
    doc_id += 1

# Commit to be searchable
si.commit()
