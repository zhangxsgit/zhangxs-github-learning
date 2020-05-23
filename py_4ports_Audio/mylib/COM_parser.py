# Copyright: Gemalto M2M 2018, Marten Petschke

import sys
if sys.version_info < (3,0,0):                  # Python2 / Python3 difference
   import Tkinter as tk                         # Python2
   import thread
else:
   import tkinter as tk                         # Python3
   import _thread as thread                     # Python3
import serial
#import threading
import time
import mylib

        

#----------------------------------------------------------
# returns a list of answered lines until OK
#
class COMparser(serial.Serial):
    def __init__(ser, print_and_log, *args, **kwargs):
        kwargs['timeout'] = 0.1
        serial.Serial.__init__(ser, *args, **kwargs)
        ser.print_and_log = print_and_log  # customer logging defined by main script 
        ser.rx_buffer = ""
        ser.answerflag=0                # within an AT command?
        ser.URCrcvflag=0                # 
        ser.answerlist=[]
        ser.URCrcvlist=[]
        ser.receive_thread_active=0
        ser.rts_    = False             # default values
        ser.dtr_    = False             # default values
        ser.rtscts_ = False             # default values

    def collect_line(ser):              # thread
       while ser.receive_thread_active: # thread guard
          try :
           nr = ser.inWaiting()       # Python 2: char available?
#            nr = ser.in_waiting        # Python 3: char available?
           if nr:  
             char = ser.read(1)
             #print(char)
             if (char == b'\r' or char == b'\n'):
                if  ser.rx_buffer != "": #skip empty lines
                    #ser.print_and_log('.')
                    ser.check_line(ser.rx_buffer)
                    ser.rx_buffer = ""            
             else : 
#                if (char == b'>'):   # SMS feature
#                       ser.rx_buffer += char.decode('latin-1')
#                       ser.checkline(ser.rx_buffer)
#                       ser.rx_buffer = ""            
#                else:
                   ser.rx_buffer += char.decode('latin-1')
          except  : pass
#             return 0

    def check_line(ser, line): 
       ser.cb_checkline(line)          # logging is done in ui_com_frame.py
       if ser.answerflag==1:           # are we within an AT command?
          ser.answerlist.append(line)
       if ser.URCrcvflag==1:           # do we collect URC*s?
          ser.URCrcvlist.append(line)

                   
    def opencom(ser, comstring, baudrate, cb_checkline):
        ser.cb_checkline = cb_checkline #callback
        ser.port     = comstring        # configure instance
        ser.baudrate = baudrate         # configure instance
        try :
           ser.open()
        except IOError:
               print ("=> could not open " + ser.port + " !")
               return 0
        ser.setRTS(True)    # reset MC-Test4
        ser.setDTR(False)
        ser.setRTS(ser.rts_)
        ser.setDTR(ser.dtr_)
        ser.receive_thread_active = 1
        print("opened: " + ser.port)
#        ser.th=threading.Thread(target=ser.collect_line, args=())
        #ser.th.daemon=True
#        ser.th.start()
        ser.th = thread.start_new_thread(ser.collect_line,())
        return ser


    def write_(ser, content):              # just write, don't wait for answers
       if ser.isOpen():
          if '\x1A' not in content:        # Ctrl-Z for sending SMS
             content += "\r"       
          try :
             ser.write(content.encode('latin-1'))      # write on serial IF
          except : pass
       
    def closecom(ser):
        ser.receive_thread_active=0                     # stop the rx-threads
        if ser.isOpen():
           try :
              ser.close()
           except : pass
           print ("closing " + ser.port)


#----------------------------------------------------------
