#!/bin/bash
# Strict & lenient MRR for 2006
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_100 strict 
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_250 strict
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_100 lenient
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_250 lenient
# strict and lenient MRR for 2007
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_100 strict
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_250 strict
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_100 lenient
python2.6 compute_mrr.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_250 strict