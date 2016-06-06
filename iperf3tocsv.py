#!/usr/bin/env python

import json
import sys
import csv
# todo: get ride of splitfile
from splitstream import splitfile


csv.register_dialect('iperf3log', delimiter=',', quoting=csv.QUOTE_MINIMAL)

csvwriter = csv.writer(sys.stdout, 'iperf3log')

# accummulate volume per ip in a dict
db = {}
# this will yield each test as a parsed json
objs = (json.loads(jsonstr) for jsonstr in splitfile(sys.stdin, format="json", bufsize=1))

csvwriter.writerow(["date", "ip", "duration", "protocol", "num_streams", "cookie", "sent", "rcvd", "totalsent", "totalreceived"])
for obj in objs:
    # caveat: assumes multiple streams are all from same IP so we take the 1st one
    ip = (obj["start"]["connected"][0]["remote_host"]).encode('ascii', 'ignore')
    sent = obj["end"]["sum_sent"]["bytes"]
    rcvd = obj["end"]["sum_received"]["bytes"]
    reverse = obj["start"]["test_start"]["reverse"]
    time = (obj["start"]["timestamp"]["time"]).encode('ascii', 'ignore')
    cookie = (obj["start"]["cookie"]).encode('ascii', 'ignore')
    protocol = (obj["start"]["test_start"]["protocol"]).encode('ascii', 'ignore')
    duration = obj["start"]["test_start"]["duration"]
    num_streams = obj["start"]["test_start"]["num_streams"]
    if reverse not in [0, 1]:
        sys.exit("unknown reverse")

    s = 0
    r = 0
    if ip in db:
        (s, r) = db[ip]

    if reverse == 0:
        r += rcvd
        sent = 0
    else:
        s += sent
        rcvd = 0

    db[ip] = (s, r)

    csvwriter.writerow([time, ip, duration, protocol, num_streams, cookie, sent, rcvd, s, r])

#    for i in db:
#        (s, r) = db[i]
#        print("%s, %d , %d " % (i, s, r))
