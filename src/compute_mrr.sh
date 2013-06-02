#!/bin/bash
# Strict & lenient MRR for 2006
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_100 strict > QA.strict_2006_100 
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_250 strict > QA.strict_2006_250 
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_100 lenient > QA.lenient_2006_100
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/devtest/factoid-docs.litkowski.2006.txt QA.outputs_2006_250 lenient > QA.lenient_2006_250
# strict and lenient MRR for 2007
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_100 strict > QA.strict_2007_100
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_250 strict > QA.strict_2007_250 
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_100 lenient > QA.lenient_2007_100
python2.6 compute_mrr_rev.py /opt/dropbox/12-13/573/Data/patterns/evaltest/factoid-docs.litkowski.2007.txt QA.outputs_2007_250 lenient > QA.lenient_2007_250