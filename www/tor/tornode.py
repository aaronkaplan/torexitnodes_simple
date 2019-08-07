#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

   tornode.py
   ~~~~~~~~~~~~

   A small flask (http://flask.pocoo.org/) based webinterface
   for the tordb

   Author: L. Aaron Kaplan <aaron@lo-res.org>
   Copyright 2014, all rights reserved

"""

from __future__ import print_function

import ipaddress
import psycopg2
import psycopg2.extras
import json
import sys
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import flask_restful as restful
# from flask.ext.psycopg2 import Psycopg2

import config as cfg

# config.py file example:
"""
DATABASE='tordb_simple'
DBUSER='aaron'
SECRET_KEY='XXXXXX CHANGE HERE - LONG RANDOM STRING XXXXX'
USERNAME='admin'
PASSWORD='XXXXXX CHANGE HERE XXXXX'
"""


# configuration

DATABASE="dbname='%s' user='%s'" %(cfg.DBNAME, cfg.DBUSER)
PSYCOPG2_DATABASE_URI='postgresql:///%s' %cfg.DBNAME
DEBUG=True
SECRET_KEY=cfg.SECRET_KEY
USERNAME=cfg.USERNAME
PASSWORD=cfg.PASSWORD


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
api = restful.Api(app)


def connect_db():
    # g.db = psycopg2.connect(app.config['DATABASE'], connection_factory=psycopg2.extras.RealDictConnection)
    try:
        g.psql=psycopg2.connect(DATABASE)
    except psycopg2.Error as e:
        print(e.pgError)
        app.logger.error(e.pgError)
        return None
    return g.psql


@app.before_request
def before_request():
    g.psql = connect_db()


@app.teardown_request
def teardown_request(exception):
    # db = getattr(g, 'db', None)
    # cur = getattr(g, 'cur', None)
    # if cur is not None:
    #     cur.close()
    # if db is not None:
    #     db.close()
    pass


#
# RESTful API
#
class IP(restful.Resource):
    def get(self, ip):
        # argument parsing & sanity checking
        try:
            app.logger.info("trying to parse IP address: %s" %(ip))
            _valid_ip = ipaddress.ip_address(ip)
        except Exception as ex:
            app.logger.error("received invalid ip as parameter: %s" %(str(ex)))
            return {"error": "invalid IP parameter given. Must be a valid IPv4 or IPv6 address."}

        # check if we get limit params
        # seen_first = request.args.get('seen_first', '')
        # seen_last  = request.args.get('seen_last', '')

        cur = g.psql.cursor()
        sql = """
SELECT ip,
       to_char(exit_address_ts, 'YYYY-MM-DD HH:MM:SS'),
       nodetype.type
FROM node,nodetype
WHERE ip=%s AND nodetype.id=node.id_nodetype
        """
        res = cur.execute(sql, (ip,))
        rows = cur.fetchall()

        e = []
        for row in rows:
            if DEBUG:
                app.logger.debug(row)
                app.logger.debug(row[2])
                app.logger.debug(type(row[2]))
            e.append(dict(ip=row[0], exit_address_ts=row[1], node_type=row[2]))
        app.logger.debug("e=%s" % repr(e))
        app.logger.debug(type(e))
        return e        # render_template('show_entries.html', entries=entries)


api.add_resource(IP, '/ip/<string:ip>')


@app.route('/')
def show_entries():
    SQLSTMT="""
    SELECT distinct(ip),
        to_char(min(exit_address_ts), 'YYYY-dd-mm HH:MM:SS') as first_seen,
        to_char(max(exit_address_ts), 'YYYY-dd-mm HH:MM:SS') as last_seen,
        count(*) as count_seen,
        nodetype.type as type
    FROM node,nodetype
    WHERE id_nodetype=nodetype.id
    GROUP BY ip,type
    ORDER BY ip
    LIMIT 10000
    """
    cur = g.psql.cursor()
    try:
        res = cur.execute(SQLSTMT)
        if (DEBUG):
            app.logger.debug(cur)
    except psycopg2.Error as e:
        app.logger.error(e.pgerror)
    entries = [dict(ip=row[0], first_seen=row[1], last_seen=row[2], count_seen=row[3], node_type=row[4]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


if __name__ == '__main__':
    app.run()
