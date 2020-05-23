# Copyright: Gemalto M2M 2018, Marten Petschke

import sys
if sys.version_info < (3,0,0):                # Python2 / Python3 difference
   import Tkinter as tk                        # Python2
   import tkFileDialog as tkfiledialog         # Python2
else:
   import tkinter as tk                         # Python3
   import tkinter.filedialog as tkfiledialog    # Python3
import serial                              # see mylib folder
import serial.tools.list_ports             # list ports does not list modem ports
import threading
import os          # path
import subprocess  # call exe; nonblocking: Popen
import time
import mylib       # classes: COMparser, Hauptfenster, config, buttons

LIGHTGRAY = "#F0F0ED" # standard background colour: Gray
GREEN     = "chartreuse"
RED2      = "#FF0001"

class mmi:
   def __init__(mmi, print_and_log,
                headline    = "headline",       # string
                description = "description",    # string
                script1 = None,
                script2 = None,
                script3 = None,
                no_of_com_ports = None):    # possible numbers: 1-4Ports

      mmi.script1 = script1
      mmi.script2 = script2
      mmi.script3 = script3
      mmi.print_and_log = print_and_log
      mmi.headline = headline        # string
      mmi.description = description  # string
      mmi.logfilename = None         # string
      mmi.Script_running=False;
      if  no_of_com_ports :
         mmi.no_of_com_ports = no_of_com_ports
      else :
         mmi.no_of_com_ports = 2     # default is 2 COM windows
         try :
            mmi.no_of_com_ports = mylib.config.no_of_com_ports;
         except : pass
         
      mmi.generate_new_COMport_list()
      
      # open 1-4 COM port instances; COM ports stay closed
      mmi.serA = mylib.COMparser(   print_and_log=mmi.print_and_log)
      if mmi.no_of_com_ports >= 2 :
         mmi.serB = mylib.COMparser(print_and_log=mmi.print_and_log)                                      
      if mmi.no_of_com_ports >= 3 :
         mmi.serC = mylib.COMparser(print_and_log=mmi.print_and_log)
      if mmi.no_of_com_ports >= 4 :
         mmi.serD = mylib.COMparser(print_and_log=mmi.print_and_log)

      mmi.window = mylib.Hauptfenster(mmi = mmi)    # string

   def open_diagram(mmi):               # For test only
      diagram = mylib.diagram(
         headline=mmi.headline,
#         x_min=0,
#         x_tick=10,   # grid
#         x_max=50,
#         y_min=0,
#         y_tick=20,   # grid
         y_max=50,
#         highlightthickness=10,
#         relief='ridge'
         )
      diagram.plot_point(x=0, y=20, color='blue')
      diagram.plot_point(x=3, y=42, color='red')
      diagram.plot_point(x=80, y=42, color='red')
      diagram.plot_point(x=12, y=38, color='RED2') #different red for separate line
      diagram.plot_point(x=70, y=38, color='RED2')
      diagram.plot_point(x=5, y=0, color='green')
      diagram.plot_point(x=7, y=20, color='green')
      diagram.plot_point(x=9, y=0, color='green')
      diagram.plot_point(x=11, y=40, color='blue')
      diagram.plot_point(x=19, y=0, color='green')
      diagram.plot_point(x=20, y=40, color='blue')

   def open_logfile(mmi, filename):             # main log file
      try: 
         logfile = open(filename, "a+") 
      except IOError: 
         print ("error reading file", filename)
         sys.exit() 
      return logfile


   def start_script(mmi, script):
      if mmi.Script_running==False :
         if mmi.window.logging.get() :                  # check window button status
            filename = mmi.window.logfilename.get()     # grab filemame from window
            mmi.logfile = mmi.open_logfile(filename)
 #          file_text = ff.logfile.readline()  # readline and write doesn't work at the same time
            mmi.logfile.write("\nTest logfile from " + time.strftime("%d.%m.%Y") + "\n")
            mmi.logfile.close()
         mmi.Script_running=True    # global Flag

         th=threading.Thread(target=script, args=())    # main part of script
         th.daemon=True
         th.start()


   def stop_script(mmi):
      mmi.Script_running=False   # There is no kill task command. User has to handle this. 
      mmi.window.b1_script['bg'] = LIGHTGRAY
      mmi.window.b2_script['bg'] = LIGHTGRAY
      mmi.window.b3_script['bg'] = LIGHTGRAY
#      print("script stopped")

   def close_all_com_ports(mmi) : # here we do not change the button color any more, just close
      mmi.Script_running=False 
      try :
         mmi.serA.closecom()
         mmi.serB.closecom()
         mmi.serC.closecom()
         mmi.serD.closecom()
      except : pass    

   def generate_windows_COMport_list(mmi):
      if float(serial.VERSION) >= (3.0):                # serial2 / 3 difference
         comlist = [p.device for p in serial.tools.list_ports.comports()] # does not show module modem port
      else :
         comlist = [p[0] for p in serial.tools.list_ports.comports()] # does not show module modem port
      return comlist

   def generate_new_COMport_list(mmi):
      """ Lists serial port names 1...256"""
      allports = ['COM%s' % (i + 1) for i in range(256)]
      winlist = mmi.generate_windows_COMport_list()             # does not show module modem port
      
      mmi.comlist = []
      for port in allports:
         if port in winlist:
            mmi.comlist.append(port)
         else :
            try :
               s = serial.Serial(port)
               s.close()
               mmi.comlist.append(port)
            except (OSError, serial.SerialException):
               pass
      
      if mmi.comlist==[]  : mmi.comlist.append("no COM port") # output: global COM port list 

   def sel_com_port(mmi, AB):
      mmi.burned_com_list = []
      preferred_com_list  = []
      
      try :
         if (AB == 'A') or (AB == '') :
            preferred_com_list = mylib.config.preferredCOMA 
         elif (AB == 'B') :
            preferred_com_list = mylib.config.preferredCOMB
         elif (AB == 'C') :
            preferred_com_list = mylib.config.preferredCOMC
         elif (AB == 'D') :
            preferred_com_list = mylib.config.preferredCOMD
      except : pass

      try :
         for port in preferred_com_list :
            if port in mmi.comlist:
               if port not in mmi.burned_com_list:
                  mmi.burned_com_list.append(port) # do not use this port again
                  return port
         for port in mmi.comlist:
            if port not in mmi.burned_com_list:
               mmi.burned_com_list.append(port)   # do not use this port again
               return port
      except : pass
      return "no COM port"

   def quitall(mmi):    # not needed at the moment
      mmi.Script_running=False 
      mmi.serA.closecom()
      mmi.serB.closecom()
      

# use mmi.sleep(sec) in order to make script interruptable
   def sleep(mmi, t):
      if mmi.Script_running==True :
         time.sleep(t)


# try also int()
   def atoi(mmi, astr):
    num = 0
    sign = 1    
    start = 0
    for c in astr:
        if c == '-' and start == 0 :
            sign = -1
        if '0' <= c <= '9':
            start = 1
            num  = num * 10 + ord(c) - ord('0')
        else:
           if start == 1 :
              return sign*num
    return sign*num
    
# use mmi.ms_time() to get a time string including millisec
   def ms_time(mmi):
      t = time.time()
      msec = int(t*1000)-1000*int(t)
      return time.strftime("%H:%M:%S.",time.localtime(t))+str(msec).zfill(3)+": " 
#      return time.strftime("%H:%M:%S.%f ")   #doesn't work