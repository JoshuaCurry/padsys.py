import json
import launchpad_py as launchpad
import time
import logging


colours = {"off":[0,False], "red":[5,False], "orange":[9,False], "yellow":[13,False], "green":[21,False], "cyan":[37,False], "blue":[45,False], "magenta":[53,False], "uv":[49,False], "white":[3,False], "flash_red":[5,True], "flash_orange":[9,True], "flash_yellow":[13,True], "flash_green":[21,True], "flash_cyan":[37,True], "flash_blue":[45,True], "flash_magenta":[53,True], "flash_uv":[49,True], "flash_white":[3,True], "light_red":[4,False], "light_orange":[8,False], "light_yellow":[12,False], "light_green":[20,False], "light_cyan":[36,False], "light_blue":[44,False], "light_magenta":[52,False], "light_uv":[48,False], "light_white":[1,False]}
settable = ['off', 'white', 'red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'uv']


class Launchpad_wrapper:
    def __init__(self, padnum, OSC):
        self.OSC = OSC
        self.config = False
        self.padnum = padnum
        self.buttons = ["off"] * 200

        stateslength = 200
        self.states = [False] * stateslength

        self.mode = None
        # create an instance
        self.lp = launchpad.Launchpad();

        # check for available launchpads
        if self.lp.Check( padnum, "pro" ):
            self.lp = launchpad.LaunchpadPro()
            if self.lp.Open(padnum,"pro"):
                logging.critical("Launchpad Pro Detected, but not supported")
                self.mode = "pro"
                exit()
                
        elif self.lp.Check( padnum, "mk2" ):
            self.lp = launchpad.LaunchpadMk2()
            if self.lp.Open( padnum, "mk2" ):
                logging.info("Launchpad id:{} Mk2 Detected".format(padnum))
                self.mode = "mk2"

        elif self.lp.Check( padnum, "control xl" ):
            self.lp = launchpad.LaunchControlXL()
            if self.lp.Open( padnum, "control xl" ):
                logging.critical("Launch Control XL Detected, but not supported.")
                exit()
                
        elif self.lp.Check( padnum, "launchkey" ):
            self.lp = launchpad.LaunchKeyMini()
            if self.lp.Open( padnum, "launchkey" ):
                logging.critical("LaunchKey (Mini) Detected, but not supported.")
                exit()

        elif self.lp.Check( padnum, "dicer" ):
            self.lp = launchpad.Dicer()
            if self.lp.Open( padnum, "dicer" ):
                logging.critical("Dicer Detected, but not supported.")
                exit()			
        else:
            if self.lp.Open():
                logging.info("Launchpad id:{} Mk1/S/Mini Detected".format(padnum))
                self.mode = "mk1"

        if self.mode is None:
            logging.critical("Did not find Launchpad id:{}, check USB connection...".format(padnum))
            exit()

        self.lp.Reset() # turn all LEDs off
        self.lp.ButtonFlush() # clear launchpad state

        self.loadcolours()
        self.lastrequesttime = time.time()


    def Reset(self):
        self.lp.Reset()

    def savecolours(self):
        with open("save"+str(self.padnum)+".json", "w") as f:
            f.write(json.dumps(self.buttons))
            logging.info("Save Successful to {}".format(str(self.padnum)+".json"))


    def loadcolours(self):
        try:
            with open("save"+str(self.padnum)+".json", "r") as f:
                self.buttons = json.loads(''.join(f.readlines()))
                logging.info("Launchpad id:{} config load successful".format(self.padnum))
        except:
            logging.info("Launchpad id:{} problem with save file... skipping...".format(self.padnum))

        for but in range(11,112):
            self.setCol(but, self.buttons[but])

        return

    def buttonRead(self):
        but = self.lp.ButtonStateRaw()
        if but != []:
            # logging.debug(" event: {}".format(but) )

            if(but[1]==0):
                event = False
            else:
                event = True

            return but[0], event
        return None, None


    def setCol(self, num, col):
        c = colours[col][0]
        flash = colours[col][1]

        if(flash):
            #white flash if current colour is off, otherwise off flash
            if(col=='off'):
                col2 = 'white'
            else:
                col2 = 'off'

            self.lp.LedCtrlRawByCode(num, c)
            self.lp.LedCtrlFlashByCode(num, colours[col2][0])
        else:
            c = colours[col][0]
            self.lp.LedCtrlRawByCode(num, c)

    def feedback(self, but, value):
        if(value==0):
            if(self.buttons[but]!='off'):
                logging.debug("Launchpad id:{}, deactivating {} ".format(self.padnum, but))
                self.setCol(but, "light_"+self.buttons[but])
        
        if(value==1):
            if(self.buttons[but]!='off'):
                logging.debug("Launchpad id:{}, activating {} ".format(self.padnum, but))
                self.setCol(but, self.buttons[but].replace('light_', ''))
        

    def normalmode(self):
        num, state = self.buttonRead()
        if(state==True):
            self.states[num] = True

            self.OSC.transmitOSC(self.padnum, num, state=1)
            
            if(self.buttons[num]!='off'):
                logging.debug("Launchpad id:{}, col set button press, brightening {}".format(self.padnum, num))
                self.setCol(num, self.buttons[num].replace('light_', ''))
        elif(state==False):
            self.states[num] = False
            self.OSC.transmitOSC(self.padnum, num, state=0)

        else:
            time.sleep(0.001)
            if(self.states[110] and self.states[111] and self.states[89] and self.states[19]):
                logging.info("Launchpad id:{} Entered configuration mode".format(self.padnum))
                self.configmode()
                self.setCol(110,'off')
                self.setCol(111,'off')
                #Reset states so we don't just drop straight back in.
                self.states[110]=False
                self.states[111]=False
                self.states[89]=False
                self.states[19]=False

            if((time.time()-self.lastrequesttime)>1):
                # refresh active
                self.OSC.send_message(b'/feedback/exec', b'1')
                self.lastrequesttime = time.time()


    def configmode(self):
        paintcol = settable[1]
        self.setCol(110,paintcol)
        self.setCol(111,'white')

        while True:
            num, state = self.buttonRead()
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
                    logging.debug("Launchpad id:{} Paint colour updated to {}".format(self.padnum, col))
                    self.setCol(num,paintcol)

                elif(num==111):
                    logging.info("Launchpad id:{} Exited configuration mode".format(self.padnum))
                    self.OSC.send_message(b'/feedback/exec', b'1')
                    self.savecolours()
                    break

                else:
                    logging.debug("Launchpad id:{} Painted {} {}".format(self.padnum, num, paintcol))
                    self.buttons[num] = paintcol
                    self.setCol(num,paintcol)
            else:
                time.sleep(0.001)