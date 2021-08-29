from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
from math import floor
import logging

execfrombutton = {104:2, 105:3, 106:4, 107:5, 108:6, 109:7, 110:8, 111:9, 81:12, 82:13, 83:14, 84:15, 85:16, 86:17, 87:18, 88:19, 89:20, 71:22, 72:23, 73:24, 74:25, 75:26, 76:27, 77:28, 78:29, 79:30, 61:32, 62:33, 63:34, 64:35, 65:36, 66:37, 67:38, 68:39, 69:40, 51:42, 52:43, 53:44, 54:45, 55:46, 56:47, 57:48, 58:49, 59:50, 41:52, 42:53, 43:54, 44:55, 45:56, 46:57, 47:58, 48:59, 49:60, 31:62, 32:63, 33:64, 34:65, 35:66, 36:67, 37:68, 38:69, 39:70, 21:72, 22:73, 23:74, 24:75, 25:76, 26:77, 27:78, 28:79, 29:80, 11:82, 12:83, 13:84, 14:85, 15:86, 16:87, 17:88, 18:89, 19:90}
buttonfromexec = {2:104, 3:105, 4:106, 5:107, 6:108, 7:109, 8:110, 9:111, 12:81, 13:82, 14:83, 15:84, 16:85, 17:86, 18:87, 19:88, 20:89, 22:71, 23:72, 24:73, 25:74, 26:75, 27:76, 28:77, 29:78, 30:79, 32:61, 33:62, 34:63, 35:64, 36:65, 37:66, 38:67, 39:68, 40:69, 42:51, 43:52, 44:53, 45:54, 46:55, 47:56, 48:57, 49:58, 50:59, 52:41, 53:42, 54:43, 55:44, 56:45, 57:46, 58:47, 59:48, 60:49, 62:31, 63:32, 64:33, 65:34, 66:35, 67:36, 68:37, 69:38, 70:39, 72:21, 73:22, 74:23, 75:24, 76:25, 77:26, 78:27, 79:28, 80:29, 82:11, 83:12, 84:13, 85:14, 86:15, 87:16, 88:17, 89:18, 90:19}

class OSC_send:
    def __init__(self, host, port, EXEC_PAGE_START, EXEC_PAGE_MODE, NUMBER_OF_PADS):
        self.osc = OSCClient(host, port)
        self.exec_page_start = EXEC_PAGE_START
        self.exec_page_mode = EXEC_PAGE_MODE
        self.number_of_pads = NUMBER_OF_PADS

    def transmitOSC(self, padnum, but, state=1):
        #TODO update this button decoder using the padnumber

        execpage = self.execpage_from_mode(padnum)
        executor = self.exec_from_button(but, padnum)

        oscstring = '/exec/'+str(execpage)+'/'+str(executor)
        oscbytes = oscstring.encode('utf-8')
        logging.debug("Launchpad id:{}, transmitOSC {}".format(padnum, oscstring))
        self.osc.send_message(oscbytes, [state])

    def send_message(self, dest, msg):
        # logging.debug("send_message {} [{}]".format(dest, msg))
        self.osc.send_message(dest, msg)

    def execpage_from_mode(self, padnum):
        if(self.exec_page_mode==0):
            # Each pad different page
            return self.exec_page_start+padnum
        elif(self.exec_page_mode==1):
            # All pads same page
            return self.exec_page_start

    def exec_from_button(self, but, padnum):
        if(self.exec_page_mode==0 or self.number_of_pads<2):
            # Just a 1:1 mapping using the cheaty array above.
            return execfrombutton[but]
        elif(self.exec_page_mode==1):
            # Have to actually work it out
            single = execfrombutton[but]
            lp_rownum = floor((single-1)/10)
            n_pads = self.number_of_pads
            out = single + ((lp_rownum*(n_pads-1)+padnum)*10)
            logging.debug("but {}, padnum {}, total {}, rownum {}, if_single {}, out {}".format(but, padnum, n_pads, lp_rownum, single, out))
            return out


class OSC_receive:
    def __init__(self, launch, EXEC_PAGE_START, EXEC_PAGE_MODE, NUMBER_OF_PADS):
        self.launch = launch
        self.exec_page_start = EXEC_PAGE_START
        self.exec_page_mode = EXEC_PAGE_MODE
        self.number_of_pads = NUMBER_OF_PADS

        self.oscserver = OSCThreadServer(advanced_matching=True)
        self.sock = self.oscserver.listen(address='0.0.0.0', port=9000, default=True)
        self.oscserver.bind(b'/exec/*/*', self.feedback, self.sock, get_address=True)
        

    def feedback(self, address, value=-1):
        #TODO decode the message to the correct pad

        page = int(str(address).split("/")[2].strip("'"))
        execnum = int(str(address).split("/")[3].strip("'"))
        value = int(value)

        logging.debug("feedback page: {}, exec: {}, value: {} ".format(page, execnum, value))


        try:
            lp, but = self.button_from_exec(page, execnum, self.exec_page_mode)
            self.launch[lp].feedback(but, value)
        except:
            logging.debug("Discarding feedback for page {} exec {}".format(page, execnum))



    def button_from_exec(self, pagenum, execnum, exec_page_mode=0):
            if(self.exec_page_mode==0 or self.number_of_pads<2):
                if not (self.exec_page_start+self.number_of_pads>=pagenum>=self.exec_page_start):
                    raise Exception("No pad for this pagenum")
                # Just a 1:1 mapping using the cheaty array above.
                lp = pagenum-self.exec_page_start
                but = buttonfromexec[execnum]
                logging.debug("lp: {}, but: {}".format(lp, but))
                return lp, but

            elif(self.exec_page_mode==1):
                # Have to actually work it out
                if not (pagenum==self.exec_page_start):
                    raise Exception("No pad for this pagenum")
                n_pads = self.number_of_pads
                lp_rownum = floor((execnum-1)/(10*n_pads))
                but_in_row = execnum % 10
                exec_if_single = lp_rownum*10+but_in_row
                padnum = abs(exec_if_single +lp_rownum*(n_pads-1)*10 - execnum )/10
                but = buttonfromexec[exec_if_single]
                logging.debug("execnum: {}, lp_rownum: {}, but_in_row: {}, padnum: {}, single: {}, but: {}".format(execnum, lp_rownum, but_in_row, padnum, exec_if_single, but))
                return int(padnum), but

