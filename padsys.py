#!/usr/bin/env python
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

from launch import Launchpad_wrapper
from osc import OSC_send, OSC_receive

NUMBER_OF_PADS = 1

OSC_s = OSC_send()
l = []
for padnum in range(NUMBER_OF_PADS):
    l.append( Launchpad_wrapper(padnum, OSC_s) )

OSC_r = OSC_receive(l)

while True:
    for pad in l:
        pad.normalmode()

for pad in l:
    pad.Reset()
