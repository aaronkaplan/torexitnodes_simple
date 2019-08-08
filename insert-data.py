#!/usr/bin/env python3

"""
Copyright 2019 (C) by Aaron Kaplan <aaron@lo-res.org>. All rights reserved.
See the accompanied COPYRIGHT file for details
"""

import pprint
import sys
import bz2
import argparse
import re
import datetime
import psycopg2

""" insert TOR Exit Node list from the [check.torproject.org](https://check.torproject.org/exit-addresses)
source into a PostgreSQL DB. See ``db/db.sql`` for a description of the schema.

Format of the data:

    ```
    ExitNode 0011BD2485AD45D984EC4159C88FC066E5E3300E
    Published 2019-08-06 07:07:09
    LastStatus 2019-08-06 08:03:23
    ExitAddress 162.247.74.201 2019-08-06 08:07:19
    ```

"""

debug=False
timezone=datetime.datetime.now().astimezone().tzinfo

if (debug):
    print("timezone=%s" %timezone)

try:
    conn = psycopg2.connect("dbname='tordb_simple' user='tordb'")
    conn.autocommit = False
except Exception as ex:
    print("I am unable to connect to the database. Error: %s" %str(ex))
    exit(255)
cur = conn.cursor()
if (debug):
    print("connected")


parser = argparse.ArgumentParser()
parser.add_argument("filename", help="filename of the downloaded file")
parser.add_argument("--debug", help="turn on debug output", action="store_true")
parser.add_argument("--torproject-format", help="assume the input is in the format as given by the https://check.torproject.org/exit-addresses site", action="store_true")

#
# argument parsing stuff
args = parser.parse_args()
if args.debug:
    debug = args.debug

filename=args.filename

if args.torproject_format:
    with bz2.BZ2File(filename, 'rb') as f:
        i = 0
        for l in f:
            kv = None
            line = l.rstrip().decode('utf-8')
            if line.startswith('ExitNode'):
                node_id = line.split(' ')[1]
            elif line.startswith('Published'):
                published = line.split(' ')[1]
            elif line.startswith('LastStatus'):
                last_status = line.split(' ')[1]
                pass
            elif line.startswith('ExitAddress'):
                res = re.match('ExitAddress ([0-9a-fA-F:.]+)\\s+([0-9 :-]+)$.*', line)
                ip = res.group(1)
                ts = res.group(2)
                if ip:
                    kv = dict(
                        node_id=node_id,
                        ip=ip,
                        first_published=published,
                        last_status=last_status,
                        exit_address_ts=ts,
                        nodetype=1                # fixed to tor exit node for now since this script only parses exitnodes
                    )
                    try:
                        cur.execute("""INSERT INTO node
                                (
                                    node_id,
                                    ip,
                                    first_published,
                                    last_status,
                                    exit_address_ts,
                                    id_nodetype
                                ) VALUES (
                                    %(node_id)s,
                                    %(ip)s,
                                    %(first_published)s,
                                    %(last_status)s,
                                    %(exit_address_ts)s,
                                    %(nodetype)s
                                )
                            """, kv)
                    except psycopg2.Error as e:
                        print(e.pgerror)
                    if debug:
                        pprint.pprint(kv)
            else:
                if debug:
                    print("could not parse line %d. Skipping... (was: %s)" %(i, line[:20]))
            i += 1

else:
    print("Error: currently only the check.torproject.org format is supported (intentionally)", file=sys.stderr)
    sys.exit(255)

# close postgresql connections & clean up
conn.commit()
conn.close()
