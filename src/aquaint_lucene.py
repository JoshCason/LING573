from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, File, \
    VERSION, initVM, Version, MultiFieldQueryParser, SimpleFSDirectory
    
initVM()
# Load up items to be able to search AQUAINT lucene index
STORE_DIR = config['aquant_index_dir']
directory = SimpleFSDirectory(File(STORE_DIR))
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
parser = MultiFieldQueryParser(Version.LUCENE_CURRENT, ['doctext', 'docheadline'], analyzer)
 
"""
>>> util.aquaint_search("roger barrister first four minute mile")["docid"]
u'APW19980908.1323'
>>> docid = util.aquaint_search("roger barrister first four minute mile")["docid"]
>>> util.aquaint_search("roger barrister first four minute")["docid"]
u'APW19980908.1323'
>>> util.aquaint_search("roger barrister first four")["docid"]
u'APW19980909.0112'
>>> util.aquaint_search("roger barrister first")["docid"]
u'APW19990218.0167'
>>> util.aquaint_search("roger barrister")["docid"]
u'APW19990218.0167'
"""
def aquaint_search(qry, searcher=None):
     
    wildcard = config['use_lucene_wildcard']
    closeSearcher = False
    if searcher == None:
        searcher = IndexSearcher(directory, True)
        closeSearcher = True
         
    # replace any lucene keywords
    replacements = [',','.',';','|','/','\\','OR','AND','+','-','NOT','~','TO',':','[',']','(',')','{','}','!','||','&&','^','*','?','"']
    for p in replacements:
        qry = qry.replace(p, '')
 
    qry = qry.strip()
 
    # wildcard matching
    if wildcard == True:
        qry = qry + '* OR ' + qry
     
    query = MultiFieldQueryParser.parse(parser, qry)
     
    # How many docs do we want back?
    aquaint_lim = 1
    scoreDocs = searcher.search(query, aquaint_lim).scoreDocs
    if len(scoreDocs) == 0:
        return False
 
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc) 
    if closeSearcher:
        searcher.close()
    return doc