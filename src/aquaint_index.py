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
    aquaint_path = '/corpora/LDC/LDC02T31'
    sub_dirs = ['/apw/1998/']
    
    lucene.initVM()
    print 'lucene', lucene.VERSION
    start = datetime.now()
    
    # create aquaint index
    if not os.path.exists('aquaint_index'):
        os.mkdir('aquaint_index')
    store = lucene.SimpleFSDirectory(lucene.File('aquaint_index'))
    writer = lucene.IndexWriter(store, lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT), True,
                                lucene.IndexWriter.MaxFieldLength.LIMITED)
    writer.setMaxFieldLength(1048576)

    # gather each AQUAINT dir
    for d in sub_dirs:
        files = [ aquaint_path + d + f for f in os.listdir(aquaint_path + d) if os.path.isfile(os.path.join(aquaint_path + d,f)) ]

    # for each AQUAINT file get info
    for af in files:
        file = open(af)
        content = unicode(file.read(), 'utf8')
        file.close()
        
        # parse content as XML? doesn't seem to be working right.
        #tree = ET.parse('<root>' + content + '</root>')
        #root = tree.getroot()
    
        for doc in root.findall('DOC'):
            #docid = doc.find('DOCNO').text
            #doctext = doc.find('.//TEXT').text.strip()
            #docheadline = document.find('.//HEADLINE').text.strip()
            
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
                
    ticker = Ticker()
    print 'optimizing index',
    threading.Thread(target=ticker.run).start()
    writer.optimize()
    writer.close()
    ticker.tick = False
    print 'done'
    
    end = datetime.now()
    print end - start
