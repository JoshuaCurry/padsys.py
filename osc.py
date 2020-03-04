from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient


execfrombutton = {104:2, 105:3, 106:4, 107:5, 108:6, 109:7, 110:8, 111:9, 81:12, 82:13, 83:14, 84:15, 85:16, 86:17, 87:18, 88:19, 89:20, 71:22, 72:23, 73:24, 74:25, 75:26, 76:27, 77:28, 78:29, 79:30, 61:32, 62:33, 63:34, 64:35, 65:36, 66:37, 67:38, 68:39, 69:40, 51:42, 52:43, 53:44, 54:45, 55:46, 56:47, 57:48, 58:49, 59:50, 41:52, 42:53, 43:54, 44:55, 45:56, 46:57, 47:58, 48:59, 49:60, 31:62, 32:63, 33:64, 34:65, 35:66, 36:67, 37:68, 38:69, 39:70, 21:72, 22:73, 23:74, 24:75, 25:76, 26:77, 27:78, 28:79, 29:80, 11:82, 12:83, 13:84, 14:85, 15:86, 16:87, 17:88, 18:89, 19:90}
buttonfromexec = {2:104, 3:105, 4:106, 5:107, 6:108, 7:109, 8:110, 9:111, 12:81, 13:82, 14:83, 15:84, 16:85, 17:86, 18:87, 19:88, 20:89, 22:71, 23:72, 24:73, 25:74, 26:75, 27:76, 28:77, 29:78, 30:79, 32:61, 33:62, 34:63, 35:64, 36:65, 37:66, 38:67, 39:68, 40:69, 42:51, 43:52, 44:53, 45:54, 46:55, 47:56, 48:57, 49:58, 50:59, 52:41, 53:42, 54:43, 55:44, 56:45, 57:46, 58:47, 59:48, 60:49, 62:31, 63:32, 64:33, 65:34, 66:35, 67:36, 68:37, 69:38, 70:39, 72:21, 73:22, 74:23, 75:24, 76:25, 77:26, 78:27, 79:28, 80:29, 82:11, 83:12, 84:13, 85:14, 86:15, 87:16, 88:17, 89:18, 90:19}
execpage = 3


class OSC_send:
    def __init__(self):
        self.osc = OSCClient('10.0.1.110', 8000)


    def transmitOSC(self, padnum, but):
        #TODO update this button decoder using the padnumber
        executor = execfrombutton[but]

        oscstring = '/exec/'+str(execpage)+'/'+str(executor)
        oscbytes = oscstring.encode('utf-8')
        print(oscbytes)
        self.osc.send_message(oscbytes, [])


class OSC_receive:
    def __init__(self, launch):
        self.launch = launch

        self.oscserver = OSCThreadServer(advanced_matching=True)
        self.sock = self.oscserver.listen(address='0.0.0.0', port=9000, default=True)
        self.oscserver.bind(b'/exec/*/*', self.feedback, self.sock, get_address=True)
        

    def feedback(self, address, value=-1):
        #TODO decode the message to the correct pad

        n = int(str(address).split("/")[3].strip("'"))
        value = int(value)

        print("EXEC "+str(n)+" VAL "+str(value))
        
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
