Tracking Tor Exit Nodes
=========================

These set of scripts fetch data on Tor exit nodes from the only - as of now - currently known valid and authoritative source: https://check.torproject.org/exit-addresses

Upon downloading the data, it gets inserted into a DB (directory: 'db/')
There is a web interface written in python+flask in 'www/'


Directory Contents
------------------

	www/		-> website stuff
	db/			DB structure and initial data import mechanisms
	data/		data directory
	

Prerequisites
--------------

wget
postgresql 9.3 or higher
python
flask
webserver such as nginx

See the requirements.txt file in www/tor


Initial setup
--------------

 
  $ cd db
  $ sudo su 
  # su - postgresql
  $ createuser -s userename
  $ psql template1 < db.sql


Testing if it works
-------------------

1. Activate any virtualenv or conda environment in case you use that to install the prerequisites.
2. Test if fetching the data works:

First, make sure that the newly created user ``tordb`` may access the tables and the DB and add it to the postgresql pg_hba.conf file.


```bash
$ ./fetch-tor-list.sh 
psql -U tordb tordb_simple
select count(*) from node
```

you should see a non-zero result.

If it works, you can continue to run this automatically...

How to get this to run automatically?
------------------------------------

```bash
$ crontab -l
(...)
# fetch the list once a day at 1:05 A.M.
# m h  dom mon dow   command
5 01   *   *   *     ( cd /home/your_user/torexitnodes_simple; source venv/bin/activate ; ./fetch-tor-list.sh  >/dev/null 2>&1 ) 
```

(Note that this assumes you installed the prerequisites via virtual-env).


Deploying the web interface properly
------------------------------------

The built-in webserver of flask is a no-no for production environments.
Hence, please follow the great [documentation](https://flask.palletsprojects.com) on production setups. 
The instructions vary depending on which web server you use.

