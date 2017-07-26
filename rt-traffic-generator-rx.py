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

DEFAULT_START_PORT = 33000

def high_res_timestamp():
    utc = datetime.datetime.utcnow()
    return utc.timestamp() + utc.microsecond / 1e6

def init_v4_rx_fd(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setblocking(False)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(s, "SO_REUSEPORT"):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('', port))
    return s

def ask_exit(signame, loop):
    sys.stderr.write("got signal %s: exit\n" % signame)
    loop.stop()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--configuration", help="configuration", type=str, default=None)
    parser.add_argument("-p", "--port", help="default start port", type=int, default=DEFAULT_START_PORT)
    args = parser.parse_args()
    if not args.configuration:
        print("Configuration required, please specify a valid file path, exiting now")
        sys.exit(1)
    return args


def load_configuration_file(args):
    config = dict()
    exec(open(args.configuration).read(), config)
    return config


def conf_init():
    args = parse_args()
    return args, load_configuration_file(args)

def network_init(ctx):
    port_default_start = ctx['args'].port
    ctx['rt'] = dict()
    for i, data in enumerate(ctx['conf']['data']):
        ctx['rt'][i] = dict()
        ctx['rt'][i]['seq-no'] = 0
        ctx['rt'][i]['conf'] = data
        if 'port' in data:
            ctx['rt'][i]['port'] = data['port']
        else:
            ctx['rt'][i]['port'] = port_default_start
            port_default_start += 1
        ctx['rt'][i]['fd'] = init_v4_rx_fd(ctx['rt'][i]['port'])
        ctx['rt'][i]['seq-expected'] = 0

def ctx_new(args, conf):
    return {'args' : args, 'conf' : conf }

def name(d, i):
    if 'name' in d:
        return d['name']
    return i

def process_data(ctx, data, i, msg):
    seq = struct.unpack('!I', msg[0:4])[0]
    p = {}
    p['seq-no'] = seq
    p['payload-size'] = len(msg)
    p['stream'] = name(data, i)
    p['rx-time'] = high_res_timestamp()
    print(json.dumps(p, sort_keys=True))
    #if seq != data['seq-expected']:
    #    print("sequence not expected - packet loss detected!")
    #    print("expect {}, received: {}".format(data['seq-expected'], seq))
    #    packets_lost = seq - data['seq-expected']
    #    print("packet lost: {}".format(packets_lost))
    #data['seq-expected'] = seq + 1

def cb_v4_rx(fd, ctx, data, i):
    try:
        msg, addr = fd.recvfrom(16600)
    except socket.error as e:
        print('Expection')
    process_data(ctx, data, i, msg)

def main():
    args, conf = conf_init()
    ctx = ctx_new(args, conf)

    network_init(ctx)
    loop = asyncio.get_event_loop()

    # spawn n independent tx threads
    for i, data in ctx['rt'].items():
        fd = data['fd']
        loop.add_reader(fd, functools.partial(cb_v4_rx, fd, ctx, data, i))

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame, loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
