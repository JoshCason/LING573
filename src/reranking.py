import numpy as np
import classifier

TOTAL_QUESTIONS = 995
NUM_OF_QUESTIONS = TOTAL_QUESTIONS
PERCENT = 0.1 # of data for testing
KFEATURES = 1500

main_clsfr = classifier.clsfr("web_reranking", alg="svm",kfeatures=KFEATURES)

qids = []

np.random.seed(0)
indices = np.random.permutation(len(qids))
qids = map(lambda x: qids[x], indices)[:NUM_OF_QUESTIONS] 
portion = int(len(qids) * PERCENT)
trainq = qids[portion:]
testq = qids[:portion]

def web_rerank(qc_dict):
    pass