#!/usr/bin/python3
# -*- coding: utf-8 -*- 

import asyncio
import socket
import struct
import binascii
import time
import sys
import functools
import argparse
import signal
import os
import json
import datetime
import pprint
import random
import string


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-rx", help="RX trace file", type=str, default=None)
    parser.add_argument("--trace-tx", help="TX trace file", type=str, default=None)
    args = parser.parse_args()
    if not args.trace_rx or not args.trace_tx:
        print("RX and TX files required")
        sys.exit(1)
    return args

def load_configuration_file(args):
    config = dict()
    exec(open(args.configuration).read(), config)
    return config

def conf_init():
    return parse_args()

def db_new():
    d = dict()
    d['streams-tx'] = dict()
    d['streams-rx'] = dict()
    return d

def analyse(db):
    for stream_id, stream_data in db['streams-tx'].items():
        for packet_data in stream_data:
            if packet_data['seq-no'] in db['streams-rx'][stream_id]:
                rx_packet = db['streams-rx'][stream_id][packet_data['seq-no']]
                print("tx time: {}".format(packet_data['tx-time']))
                print("rx time: {}".format(rx_packet['rx-time']))
            else:
                print("packet loss")

def process(db, conf):
    with open(conf.trace_tx) as fd_tx:
        for line in fd_tx:
            d = json.loads(line)
            if d['stream'] not in db['streams-tx']:
                # stream packets (data) is ordered
                # at least at sender side
                db['streams-tx'][d['stream']] = []
            db['streams-tx'][d['stream']].append(d)

    with open(conf.trace_rx) as fd_rx:
        for line in fd_rx:
            d = json.loads(line)
            if d['stream'] not in db['streams-rx']:
                # this is different from tx db, we store
                # them dict() for fast lookup
                db['streams-rx'][d['stream']] = dict()

            db['streams-rx'][d['stream']][d['seq-no']] = d
    # do the analysis now
    analyse(db)

def main():
    conf = conf_init()
    db = db_new()
    process(db, conf)

if __name__ == "__main__":
    main()
