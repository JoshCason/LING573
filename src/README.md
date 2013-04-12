Solr
====

Solr is a HTTP interface to Lucene that provides for a lot of niceties that Lucene itself does not. Such as XML/JSON output.

Make sure you have Java available on your system, on a Ubuntu/Debian machine, you will more than likely need to install the following:

```
sudo apt-get install libcurl4-gnutls-dev

sudo apt-get install libxml2-dev

sudo apt-get install openjdk-6-jdk
```

Starting Solr
-------------
```
./bin/solr start
```

Sunburnt
========

Python wrapper for Solr

Documentation: http://opensource.timetric.com/sunburnt/

Installation
------------
```
sudo apt-get install python-httplib2

sudo apt-get install python-lxml

cd sunburnt

sudo python setup.py install
```

Example Solr Indexing and Querying
----------------------------------
```
python example_index.py

python example_search.py
```
