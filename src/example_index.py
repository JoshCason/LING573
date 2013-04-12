#!/usr/bin/python
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Example Solr Document Indexing 
#
# @author Anthony Gentile <agentile@uw.edu>
import os, sys, sunburnt

# We are running a multicore setup. Sepcify which core.
SOLR_CORE = 'dev'

SOLR_SCHEMA_PATH = os.path.dirname(os.path.realpath(__file__)) + '/apache-solr-3.6.2/573/multicore/' + SOLR_CORE + '/conf/schema.xml'

si = sunburnt.SolrInterface("http://localhost:8983/solr/" + SOLR_CORE, SOLR_SCHEMA_PATH)

# If any schema changes were made, lets pick them up
si.init_schema()

# Delete all documents from the index
si.delete_all()

# Add a document
documents = [{"id":1,
            "question":"Who is the leader of North Korea?",
            "answer":"Pak Pong-ju"}]

si.add(documents)

# Commit to be searchable
si.commit()
