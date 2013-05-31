import cPickle

# treats Litkowski patterns as arrays of patts and doclists
# where patts are regular expression patterns that match correct answers
# and  doclist are list of docnos in which those patterns are valid
class pattern:
    def __init__(self,patt,doclist):
        self.patts = []
        self.patts.append(patt)
        self.doclists = []
        self.doclists.append(doclist)

f = open("pickledquestions",'rb')
questions = cPickle.load(f)
f.close()

rfilein = open("pickledplainwebresults",'rb')
r = cPickle.load(rfilein)
rfilein.close()

h = open("pickledqc",'rb')
qc = cPickle.load(h)
h.close()

# don't move the following section above the "pattern" class since the
# data structure in the pickle requires it.
g = open("pickledanswers",'rb')
anspatterns = cPickle.load(g)
g.close()
