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

See the requirements.txt file in www/


Initial setup
--------------

 
  $ cd db
  $ sudo su 
  # su - postgresql
  $ createuser -s userename
  $ psql template1 < db.sql




How to get this to run?
------------------------

```bash
$ crontab -l
(...)
# m h  dom mon dow   command
*/5 *  *   *   *     ( cd /home/aaron/torexitnodes_simple; ./fetch-tor-list.sh  >/dev/null 2>&1 ) 
```


