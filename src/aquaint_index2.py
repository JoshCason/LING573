#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Do some indexing of AQUAINT corpora
# 
# XML docs http://docs.python.org/2/library/xml.etree.elementtree.html
# 
# @author Anthony Gentile <agentile@uw.edu>
import sys, os, xml.etree.ElementTree as ET, lucene, threading, time
from datetime import datetime

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)
            
if __name__ == '__main__':
    aquaint_path = '/corpora/LDC/LDC08T25/data'
    sub_dirs = ['/afp_eng/', '/apw_eng/', '/cna_eng/', '/ltw_eng/', '/nyt_eng/', '/xin_eng/']

    lucene.initVM()
    print 'lucene', lucene.VERSION
    start = datetime.now()
    
    # create aquaint index
    if not os.path.exists('aquaint_index2'):
        os.mkdir('aquaint_index2')
    store = lucene.SimpleFSDirectory(lucene.File('aquaint_index2'))
    writer = lucene.IndexWriter(store, lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT), True,
                                lucene.IndexWriter.MaxFieldLength.LIMITED)
    writer.setMaxFieldLength(1048576)

    # gather each AQUAINT dir
    fileList = []

    for d in sub_dirs:
        for root, subFolders, files in os.walk(aquaint_path + d):
            for file in files:
                if os.path.isfile(os.path.join(root,file)):
                    fileName, fileExtension = os.path.splitext(os.path.join(root,file))
                    if fileExtension == '.xml':
                        fileList.append(os.path.join(root,file))

    # for each AQUAINT file get info
    for af in fileList:
        file = open(af)
        content = file.readlines()
        file.close()
        
        # crude way of parsing out the AQUAINT docs.
        # was having issues with ElementTree and the aquaint.dtd
        doc_found = False
        headline_found = False
        text_found = False
        docid = ''
        doctext = ''
        docheadline = ''
        for line in content:
            # headline can be split across multiple lines or on one line.
            if doc_found and '</HEADLINE>' in line:
                headline_found = False
            if headline_found:
                docheadline += line.strip() + ' ' 
            if doc_found and '<HEADLINE>' in line:
                if '</HEADLINE>' in line:
                    docheadline = line.replace('<HEADLINE>', '').replace('</HEADLINE>', '').strip()
                else:
                    headline_found = True

            # text can be split across multiple lines or on one line.
            if doc_found and '</TEXT>' in line:
                text_found = False
            if text_found:
                doctext += line.strip() + ' '
            if doc_found and '<TEXT>' in line:
                if '</TEXT>' in line:
                    doctext = line.replace('<TEXT>', '').replace('</TEXT>', '').strip()
                else:
                    text_found = True
                
            if line.strip().startswith('<DOC'):
                docid = line[line.find('id="') + 4:line.find('"', line.find('id="') + 4)].strip()
                doc_found = True
                
            if line.strip() == '</DOC>':
                # Done with doc, lets index it.
                
                docheadline = docheadline.strip()
                doctext = doctext.strip()

                d = lucene.Document()
                
                d.add(lucene.Field("docid", docid,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.ANALYZED))
                                     
                d.add(lucene.Field("doctext", doctext,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.ANALYZED))
                                     
                d.add(lucene.Field("docheadline", docheadline,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.ANALYZED))
    
                writer.addDocument(d)
                
                # Reset for next doc
                doc_found = False
                headline_found = False
                text_found = False
                docid = ''
                doctext = ''
                docheadline = ''
        
    ticker = Ticker()
    print 'optimizing index',
    threading.Thread(target=ticker.run).start()
    writer.optimize()
    writer.close()
    ticker.tick = False
    print 'done'
    
    end = datetime.now()
    print end - start
