#!/bin/bash

/opt/python-2.7/bin/python2.7 qa_runner.py
cd ../outputs
./compute_mrr.sh