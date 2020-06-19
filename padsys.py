#!/usr/bin/env python3
#                  _                             
#  _ __   __ _  __| |___ _   _ ___   _ __  _   _ 
# | '_ \ / _` |/ _` / __| | | / __| | '_ \| | | |
# | |_) | (_| | (_| \__ \ |_| \__ \_| |_) | |_| |
# | .__/ \__,_|\__,_|___/\__, |___(_) .__/ \__, |
# |_|                    |___/      |_|    |___/ 
# 
# Python-based Launchpad Interface to Chamsys
#
# GitHub: https://github.com/joshuacurry/padsyspy
# adapted from https://github.com/electronics/padsys
# 
# Usage: padsys.py [no args]
#

from padsys.launch import Launchpad_wrapper
from padsys.osc import OSC_send, OSC_receive
import padsys.colour_logs as colour_logs
import sys
import argparse
import logging


parser = argparse.ArgumentParser(description='PadSys.py: Use Novation Launchpads to control Chamsys MagicQ over OSC')
parser.add_argument('-n', '--pads', required=False, default="1", type=int,
                    help='Number of Launchpads (default: 1)')
parser.add_argument('-e', '--exec', required=False, default="3", type=int,
                    help='ChamSys Exec Page (default: 3), increments by pad number by default, e.g. first LaunchPad maps to page3, second LaunchPad to page4 etc.')
parser.add_argument('-c', '--combine', required=False, action='store_true',
                    help='Combine multiple pads onto same exec page (e.g. 2 pads map to a 20x10 page)')
parser.add_argument('--host', required=False, default="127.0.0.1",
                    help='OSC Hostname (default: 127.0.0.1)')
parser.add_argument('--port', required=False, default="8000", type=int,
                    help='OSC Port (default: 8000)')
parser.add_argument('-v', '--verbose', required=False, action='store_true',
                    help='Verbose logging')

args = parser.parse_args()

if(args.verbose):
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)

NUMBER_OF_PADS = args.pads
OSC_HOST = args.host
OSC_PORT = args.port
# Exec page to start on, with pad 0
EXEC_PAGE_START = args.exec
# Mode 0: Sequential pads sequential pages
# Mode 1: Sequential pads same page horizontal
EXEC_PAGE_MODE = 1 if args.combine else 0

logging.info("Args: {} LaunchPads, {}:{} exec {} pagemode {}".format(NUMBER_OF_PADS, OSC_HOST, OSC_PORT, EXEC_PAGE_START, EXEC_PAGE_MODE))

l = []
OSC_s = OSC_send(OSC_HOST, OSC_PORT, EXEC_PAGE_START, EXEC_PAGE_MODE, NUMBER_OF_PADS)

for padnum in range(NUMBER_OF_PADS):
    l.append( Launchpad_wrapper(padnum, OSC_s) )

OSC_r = OSC_receive(l, EXEC_PAGE_START, EXEC_PAGE_MODE, NUMBER_OF_PADS)

while True:
    for pad in l:
        pad.normalmode()

for pad in l:
    pad.Reset()
