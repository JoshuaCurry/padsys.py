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

import sys
import launchpad_py as launchpad
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import atexit
import random
import json
import time

execfrombutton = {104:2, 105:3, 106:4, 107:5, 108:6, 109:7, 110:8, 111:9, 81:12, 82:13, 83:14, 84:15, 85:16, 86:17, 87:18, 88:19, 89:20, 71:22, 72:23, 73:24, 74:25, 75:26, 76:27, 77:28, 78:29, 79:30, 61:32, 62:33, 63:34, 64:35, 65:36, 66:37, 67:38, 68:39, 69:40, 51:42, 52:43, 53:44, 54:45, 55:46, 56:47, 57:48, 58:49, 59:50, 41:52, 42:53, 43:54, 44:55, 45:56, 46:57, 47:58, 48:59, 49:60, 31:62, 32:63, 33:64, 34:65, 35:66, 36:67, 37:68, 38:69, 39:70, 21:72, 22:73, 23:74, 24:75, 25:76, 26:77, 27:78, 28:79, 29:80, 11:82, 12:83, 13:84, 14:85, 15:86, 16:87, 17:88, 18:89, 19:90}
buttonfromexec = {2:104, 3:105, 4:106, 5:107, 6:108, 7:109, 8:110, 9:111, 12:81, 13:82, 14:83, 15:84, 16:85, 17:86, 18:87, 19:88, 20:89, 22:71, 23:72, 24:73, 25:74, 26:75, 27:76, 28:77, 29:78, 30:79, 32:61, 33:62, 34:63, 35:64, 36:65, 37:66, 38:67, 39:68, 40:69, 42:51, 43:52, 44:53, 45:54, 46:55, 47:56, 48:57, 49:58, 50:59, 52:41, 53:42, 54:43, 55:44, 56:45, 57:46, 58:47, 59:48, 60:49, 62:31, 63:32, 64:33, 65:34, 66:35, 67:36, 68:37, 69:38, 70:39, 72:21, 73:22, 74:23, 75:24, 76:25, 77:26, 78:27, 79:28, 80:29, 82:11, 83:12, 84:13, 85:14, 86:15, 87:16, 88:17, 89:18, 90:19}
colours = {"off":[0,False], "red":[5,False], "orange":[9,False], "yellow":[13,False], "green":[21,False], "cyan":[37,False], "blue":[45,False], "magenta":[53,False], "uv":[49,False], "white":[3,False], "flash_red":[5,True], "flash_orange":[9,True], "flash_yellow":[13,True], "flash_green":[21,True], "flash_cyan":[37,True], "flash_blue":[45,True], "flash_magenta":[53,True], "flash_uv":[49,True], "flash_white":[3,True], "light_red":[4,False], "light_orange":[8,False], "light_yellow":[12,False], "light_green":[20,False], "light_cyan":[36,False], "light_blue":[44,False], "light_magenta":[52,False], "light_uv":[48,False], "light_white":[1,False]}
settable = ['off', 'white', 'red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'uv']
colournames = list(colours.keys())
stateslength = 200
buttons = ["off"] * 200
states = [False] * stateslength
execpage = 3
returnstates = {}

lp = None

def feedback(address, value=-1):
	n = int(str(address).split("/")[3].strip("'"))
	value = int(value)
	returnstates.update({n:value})
	print("EXEC "+str(n)+" VAL "+str(value))
	global lp
	if(n in buttonfromexec and value==0):
		but = buttonfromexec[n]
		if(buttons[but]!='off'):
			print("RELEASE "+str(but))
			setCol(lp, but, "light_"+buttons[but])
	if(n in buttonfromexec and value==1):
		but = buttonfromexec[n]
		if(buttons[but]!='off'):
			print("ACTIVATE "+str(but))
			setCol(lp, but, buttons[but].replace('light_', ''))

oscserver = OSCThreadServer(advanced_matching=True)
sock = oscserver.listen(address='0.0.0.0', port=9000, default=True)
oscserver.bind(b'/exec/*/*', feedback, sock, get_address=True)

osc = OSCClient('10.0.1.110', 8000)



def savecolours():
	with open("save.json", "w") as f:
		f.write(json.dumps(buttons))
		print("Save Successful")

def loadcolours():
	try:
		with open("save.json", "r") as f:
			global buttons
			buttons = json.loads(''.join(f.readlines()))
			print("Load Successful")
	except:
		print("problem with save file... skipping...")

	for but in range(11,112):
		setCol(lp, but, buttons[but])

	return


def init():
	mode = None
	global lp
	# create an instance
	lp = launchpad.Launchpad();

	# check for available launchpads
	if lp.Check( 0, "pro" ):
		lp = launchpad.LaunchpadPro()
		if lp.Open(0,"pro"):
			print("Launchpad Pro Detected")
			mode = "pro"
			
	elif lp.Check( 0, "mk2" ):
		lp = launchpad.LaunchpadMk2()
		if lp.Open( 0, "mk2" ):
			print("Launchpad Mk2 Detected")
			mode = "mk2"

	elif lp.Check( 0, "control xl" ):
		lp = launchpad.LaunchControlXL()
		if lp.Open( 0, "control xl" ):
			print("Launch Control XL Detected, but not supported.")
			exit()
			
	elif lp.Check( 0, "launchkey" ):
		lp = launchpad.LaunchKeyMini()
		if lp.Open( 0, "launchkey" ):
			print("LaunchKey (Mini) Detected, but not supported.")
			exit()

	elif lp.Check( 0, "dicer" ):
		lp = launchpad.Dicer()
		if lp.Open( 0, "dicer" ):
			print("Dicer Detected, but not supported.")
			exit()			
	else:
		if lp.Open():
			print("Launchpad Mk1/S/Mini Detected")
			mode = "mk1"

	if mode is None:
		print("Did not find any Launchpads, check USB connection...")
		exit()

	lp.Reset() # turn all LEDs off
	lp.ButtonFlush() # clear launchpad state

	loadcolours()

	return(lp, mode)


def buttonRead(lp):
	but = lp.ButtonStateRaw()
	if but != []:
		print(" event: ", but )

		if(but[1]==0):
			event = False
		else:
			event = True

		return but[0], event

	else:
		return None, None

def setCol(lp,num,col):

	c = colours[col][0]
	flash = colours[col][1]

	if(flash):
		#white flash if current colour is off, otherwise off flash
		if(col=='off'):
			col2 = 'white'
		else:
			col2 = 'off'

		lp.LedCtrlRawByCode(num, c)
		lp.LedCtrlFlashByCode(num, colours[col2][0])
	else:
		c = colours[col][0]
		lp.LedCtrlRawByCode(num, c)

def transmitOSC(but):
	executor = execfrombutton[but]
	oscstring = '/exec/'+str(execpage)+'/'+str(executor)
	oscbytes = oscstring.encode('utf-8')
	print(oscbytes)
	osc.send_message(oscbytes, [])

def main():
	lp, mode = init()
	normalmode(lp)
	lp.Reset()

def normalmode(lp):
	lastrequesttime = time.time()
	while True:
		num, state = buttonRead(lp)
		if(state==True):
			states[num] = True
			transmitOSC(num)
			if(buttons[num]!='off'):
				print("ACTIVATE "+str(num))
				setCol(lp, num, buttons[num].replace('light_', ''))
		elif(state==False):
			states[num] = False
		else:
			time.sleep(0.001)
			if(states[110] and states[111] and states[89] and states[19]):
				print("ENTER CONFIGURATION MODE")
				configmode(lp)
				setCol(lp,110,'off')
				setCol(lp,111,'off')
				#Reset states so we don't just drop straight back in.
				states[110]=False
				states[111]=False
				states[89]=False
				states[19]=False

			if((time.time()-lastrequesttime)>1):
				# refresh active
				print('refresh')
				osc.send_message(b'/feedback/exec', b'1')
				lastrequesttime = time.time()

def configmode(lp):
	paintcol = settable[1]
	setCol(lp,110,paintcol)
	setCol(lp,111,'white')

	while True:
		num, state = buttonRead(lp)
		#If pushed
		if(state==True):
			if(num==110):
				prevcol = paintcol

				#changed colournames to settable to remove weird ones

				if(settable.index(prevcol)==(len(settable)-1)):
					col=settable[0]
				else:
					col=settable[(settable.index(prevcol)+1)]

				paintcol = col
				print("paint colour updated")
				setCol(lp,num,paintcol)

			elif(num==111):
				print("EXIT BUTTON PRESS")
				osc.send_message(b'/feedback/exec', b'1')
				savecolours()
				break

			else:
				print("doing colour paint")
				buttons[num] = paintcol
				setCol(lp,num,paintcol)
		else:
			time.sleep(0.001)



				
	
if __name__ == '__main__':
	main()

