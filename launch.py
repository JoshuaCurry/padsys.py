import json
import launchpad_py as launchpad
import time


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
                print("Launchpad Pro Detected")
                self.mode = "pro"
                
        elif self.lp.Check( padnum, "mk2" ):
            self.lp = launchpad.LaunchpadMk2()
            if self.lp.Open( padnum, "mk2" ):
                print("Launchpad Mk2 Detected")
                self.mode = "mk2"

        elif self.lp.Check( padnum, "control xl" ):
            self.lp = launchpad.LaunchControlXL()
            if self.lp.Open( padnum, "control xl" ):
                print("Launch Control XL Detected, but not supported.")
                exit()
                
        elif self.lp.Check( padnum, "launchkey" ):
            self.lp = launchpad.LaunchKeyMini()
            if self.lp.Open( padnum, "launchkey" ):
                print("LaunchKey (Mini) Detected, but not supported.")
                exit()

        elif self.lp.Check( padnum, "dicer" ):
            self.lp = launchpad.Dicer()
            if self.lp.Open( padnum, "dicer" ):
                print("Dicer Detected, but not supported.")
                exit()			
        else:
            if self.lp.Open():
                print("Launchpad Mk1/S/Mini Detected")
                self.mode = "mk1"

        if self.mode is None:
            print("Did not find Launchpad, check USB connection...")
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
            print("Save Successful")


    def loadcolours(self):
        try:
            with open("save"+str(self.padnum)+".json", "r") as f:
                self.buttons = json.loads(''.join(f.readlines()))
                print("Load Successful")
        except:
            print("problem with save file... skipping...")

        for but in range(11,112):
            self.setCol(but, self.buttons[but])

        return

    def buttonRead(self):
        but = self.lp.ButtonStateRaw()
        if but != []:
            print(" event: ", but )

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
        

    def normalmode(self):
        num, state = self.buttonRead()
        if(state==True):
            self.states[num] = True

            self.OSC.transmitOSC(self.padnum, num)
            
            if(self.buttons[num]!='off'):
                print("ACTIVATE "+str(num))
                self.setCol(num, self.buttons[num].replace('light_', ''))
        elif(state==False):
            self.states[num] = False
        else:
            time.sleep(0.001)
            if(self.states[110] and self.states[111] and self.states[89] and self.states[19]):
                print("ENTER CONFIGURATION MODE")
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
                print('refresh')
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
                    print("paint colour updated")
                    self.setCol(num,paintcol)

                elif(num==111):
                    print("EXIT BUTTON PRESS")
                    self.OSC.send_message(b'/feedback/exec', b'1')
                    self.savecolours()
                    break

                else:
                    print("doing colour paint")
                    self.buttons[num] = paintcol
                    self.setCol(num,paintcol)
            else:
                time.sleep(0.001)