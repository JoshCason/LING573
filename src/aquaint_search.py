#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Search Lucene Index
# 
# @author Anthony Gentile <agentile@uw.edu>
from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, MultiFieldQueryParser


"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""
def run(searcher, analyzer):
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        if command == '':
            return

        print
        print "Searching for:", command
        parser = MultiFieldQueryParser(Version.LUCENE_CURRENT, ['doctext', 'docheadline'], analyzer)
        
        term = command
        # wildcard/partial term matching
        whole_group = term.strip() + '* OR ' + term.strip()
        parts_group = ''
        terms = term.split()
        i = 0
        for term in terms:
            if i != 0:
                parts_group += ' OR '
            parts_group += '(' + term.strip() + '* OR ' + term.strip() + ')'
            i += 1
        term = '(' + whole_group + ' OR ' + parts_group + ')'
        
        query = MultiFieldQueryParser.parse(parser, term)
        scoreDocs = searcher.search(query, 1).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            print 'docid:', doc.get("docid")
            print 'docheadline:', doc.get("docheadline")
            print 'doctext:', doc.get("doctext")


if __name__ == '__main__':
    STORE_DIR = "aquaint_index"
    initVM()
    print 'lucene', VERSION
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    searcher.close()
