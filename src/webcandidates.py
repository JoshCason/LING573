import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
from util import *
import string
from nltk.corpus import stopwords


def getcandidates(search_results, query):
    stopwords = set(stopwords.words('english'))
    punct = set(string.punctuation)
    
    text = ''
    
    for result in search_results:
        text += "... %s" % result['title']
        text += "... %s" % result['description']
            
    ngrams = Counter()
    texts = text.split('...')
    toked = []
    for t in texts:
        tokes = word_tokenize(t)
        tokes = map(lambda x: x.lower(), tokes)
        toked.append(tokes)
    for tokens in toked:
        ngrams.update(tokens)
        ngrams.update(map(lambda x: ' '.join(x), bigramize(tokens)))
        ngrams.update(map(lambda x: ' '.join(x), trigramize(tokens)))
        ngrams.update(map(lambda x: ' '.join(x), quadrigramize(tokens)))
    stemmer = nltk.PorterStemmer()
    for k in ngrams.keys():
        qwords = set(map(lambda x: stemmer.stem(x.lower()), word_tokenize(query)))
        remove = False
        tokens = k.split()
        if len(tokens) > 1:
            if tokens[0] in stopwords: remove = True
            if tokens[-1] in stopwords: remove = True
            for token in tokens:
                if stemmer.stem(token) in qwords: remove = True
                if token in punct: remove = True
        else:
            if k in stopwords: remove = True
            if k in punct: remove = True
            if stemmer.stem(k) in qwords: remove = True
        if remove: del ngrams[k]
    for k in ngrams.keys():
        tokens = k.split()
        if len(tokens) > 1:
            for token in tokens:
                ngrams[k] += ngrams[token]
    return ngrams 