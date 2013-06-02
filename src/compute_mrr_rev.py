#############################
# Compute Mean Reciprocal Rank using Litkowski's patterns on
# standard TREC formatted QA passage results.
#
# Note: Revised to be case insensitive and handle AQUAINT-2 DocIds
#
# Usage: $0 patt_file pr_file type
# where patt_file is a Litkowski style factoid pattern file and
#       pr_file is a TREC formatted result file, and
#       type is 'strict': must match both pattern and document, or
#              'lenient': only needs to match pattern
#               Default is 'strict'
#
##############################

import os, sys, re, glob, string

import numpy

# treats Litkowski patterns as arrays of patts and doclists
# where patts are regular expression patterns that match correct answers
# and  doclist are list of docnos in which those patterns are valid
class pattern:
    def __init__(self,patt,doclist):
        self.patts = []
        self.patts.append(patt)
        self.doclists = []
        self.doclists.append(doclist)

def main():

    result_qids = []
    if len(sys.argv) < 3:
        print 'usage: ',sys.argv[0],' infile outfile strict/lenient'
        sys.exit(0)
    if len(sys.argv) < 4:
        type = 'strict'
    else:
        type = sys.argv[3]

    patt_file = sys.argv[1]
    pr_file = sys.argv[2]



    prev_qid = ''
    
    # Array of reciprocal rank values
    all_recip_ranks = []
    
    patt_f = open(patt_file,'r')
    pr_f = open(pr_file,'r')

    patterns = {}

    # Collect patters from pattern files
    for pattline in patt_f.readlines():
        pattline = pattline[:-1]
        parts = re.split('\s+',pattline)
        if len(parts) > 2:
            qid = parts[0]
            patt = ''
            partct = 1
            while partct < len(parts) and parts[partct].find('APW') < 0 and parts[partct].find('XIE') < 0 and parts[partct].find('NYT') < 0 and parts[partct].find('AFP') < 0 and parts[partct].find('XIN') < 0 and parts[partct].find('LTW') < 0 and parts[partct].find('CNA') < 0:
                patt += parts[partct]+'\s*'
                partct += 1
            doclist = []
            while partct < len(parts):
                doclist.append(parts[partct])
                partct += 1
            if patterns.has_key(qid):
                patterns[qid].patts.append(patt)
                patterns[qid].doclists.append(doclist)
            else:
                patterns[qid] = pattern(patt,doclist)
    patt_f.close()

    # Scan results files for matches with patterns and compute MRR scores
    found = 0
    rank = 1
    foundrank = -1
    for prline in pr_f.readlines():
        prline = prline[:-1]
        parts = re.split('\s+',prline)
        if len(parts) < 4:
            print 'Ill-formed results file at: '+prline
            sys.exit(0)
        else:
            qid = parts[0]
            if qid != prev_qid:
                result_qids.append(qid)
                if found == 0 and rank > 1:
                    all_recip_ranks.append(0.0)
                    print prev_qid+':\t0.0'
                found = 0
                foundrank = -1
                rank = 1
                prev_qid = qid
            if qid == prev_qid and found == 0:
                if not(patterns.has_key(qid)):
                    print 'No factoid pattern for '+qid+': Ignoring'
                    continue
                docno = parts[2]
                passage = string.join(parts[3:],' ')
                pct = 0
                while pct < len(patterns[qid].patts):
                    if re.search(patterns[qid].patts[pct],passage,re.I) >= 0:
                        if (type != 'strict') or ((type == 'strict') and  (docno in patterns[qid].doclists[pct])):
                            foundrank = rank
                            found = 1
                            print qid+':\t'+str(1.0/float(rank))
                            all_recip_ranks.append(1.0/float(rank))
                            break
                    pct += 1
            rank += 1
    pr_f.close()
    if found == 0 and rank > 1:
        all_recip_ranks.append(0.0)
        print qid+':\t0.0'

    nores_ct = 0
    for key in patterns.keys():
        if not (key in result_qids):
            nores_ct += 1
            all_recip_ranks.append(0.0)

    print 'No response: \t'+str(nores_ct)
    print 'Aggregate:\t'+str(numpy.mean(all_recip_ranks))


main()
