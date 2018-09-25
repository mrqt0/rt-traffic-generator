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
    return utc.timestamp()

def init_v4_rx_fd(conf):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setblocking(False)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(s, "SO_REUSEPORT"):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('localhost', 6666))
    return s

def init_v4_tx_fd(port=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if port is None:
        return s
    if hasattr(s, "SO_REUSEPORT"):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('localhost', port))
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
        if 'src-port' in data:
            ctx['rt'][i]['fd'] = init_v4_tx_fd(data['src-port'])
        else:
            ctx['rt'][i]['fd'] = init_v4_tx_fd()
        ctx['rt'][i]['seq-no'] = 0
        ctx['rt'][i]['conf'] = data
        if 'port' in data:
            ctx['rt'][i]['port'] = data['port']
        else:
            ctx['rt'][i]['port'] = port_default_start
            port_default_start += 1
        # -1 -> unlimited
        ctx['rt'][i]['limit'] = -1
        if 'limit' in data:
            ctx['rt'][i]['limit'] = int(data['limit'])

def ctx_new(args, conf):
    return {'args' : args, 'conf' : conf }

def name(d, i):
    if 'name' in d: return d['name']
    return i

def message(ctx, d, i):
    assert(d['conf']['payload-size'] >= 8)
    payloadsize = d['conf']['payload-size'] - 8
    d['seq-no']
    hdr = struct.pack('!II', d['seq-no'], i)
    msg = hdr + bytes([0x00 for _ in range(payloadsize)])
    d['seq-no'] += 1
    return msg, d['seq-no'] - 1

def print_tx(data):
    print(json.dumps(data, sort_keys=True))

def tx(ctx, d, i, stream_name):
    print_data = dict()
    s = d['fd']
    addr = ctx['conf']['destination_addr']
    port = d['port']
    msg, seq_no = message(ctx, d, i)
    s.sendto(msg, (addr, port))
    print_data['tx-time'] = high_res_timestamp()
    print_data['stream'] = stream_name
    print_data['seq-no'] = seq_no
    print_data['payload-size'] = len(msg)
    print_tx(print_data)

async def burst_mode(ctx, d, i, stream_name):
    no_packets =  d['conf']['bursts-packets']
    for packet_counter in range(0, no_packets):
        tx(ctx, d, i, stream_name)
        if d['limit'] != -1:
            # limit activated
            d['limit'] -= 1
            if d['limit'] == 0:
                sys.exit(0)
        if packet_counter == no_packets -1:
            # after the last transmission we do not wait
            return
        await asyncio.sleep(d['conf']['burst-intra-time'])

async def tx_thread(ctx, i):
    d = ctx['rt'][i]
    stream_name = name(d, i)
    if 'initial-waittime' in d['conf']:
        await asyncio.sleep(d['conf']['initial-waittime'])
    while True:
        await burst_mode(ctx, d, i, stream_name)
        await asyncio.sleep(d['conf']['burst-inter-time'])

def main():
    args, conf = conf_init()
    ctx = ctx_new(args, conf)

    network_init(ctx)
    loop = asyncio.get_event_loop()

    # spawn n independent tx threads
    for i, data in enumerate(ctx['conf']['data']):
        asyncio.ensure_future(tx_thread(ctx, i))

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame, loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
