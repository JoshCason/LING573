#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Store QA data in Lucene
# 
# @author Anthony Gentile <agentile@uw.edu>
import sys, os, lucene, threading, time
from datetime import datetime

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)
        store = lucene.SimpleFSDirectory(lucene.File(storeDir))
        writer = lucene.IndexWriter(store, analyzer, True,
                                    lucene.IndexWriter.MaxFieldLength.LIMITED)
        writer.setMaxFieldLength(1048576)
        self.indexDocs(root, writer)
        ticker = Ticker()
        print 'optimizing index',
        threading.Thread(target=ticker.run).start()
        writer.optimize()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, root, writer):
        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if not filename.endswith('.txt'):
                    continue
                print "adding", filename
                try:
                    path = os.path.join(root, filename)
                    file = open(path)
                    contents = unicode(file.read(), 'utf8')
                    file.close()
                    doc = lucene.Document()
                    
                    doc.add(lucene.Field("qid", qid,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.ANALYZED))
                                         
                    doc.add(lucene.Field("target_text", target_text,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.ANALYZED))
                                         
                    doc.add(lucene.Field("target_id", target_id,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.ANALYZED))
                                         
                    doc.add(lucene.Field("question", question,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.ANALYZED))
                                         
                    doc.add(lucene.Field("path", path,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.NOT_ANALYZED))

                    writer.addDocument(doc)
                except Exception, e:
                    print "Failed in indexDocs:", e

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    lucene.initVM()
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        IndexFiles(sys.argv[1], "index", lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT))
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
