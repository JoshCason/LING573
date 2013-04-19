universe                = vanilla
executable              = /usr/bin/python
log                     = condor.log
error                   = condor.error
output                  = condor.out
arguments               = "src/trec_questions.py /dropbox/12-13/573/Data/Questions/training/TREC-2005.xml"
transfer_executable     = false
getenv                  = true
queue
