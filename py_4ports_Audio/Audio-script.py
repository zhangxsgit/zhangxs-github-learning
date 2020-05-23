# ---------------------------------------------------------------------------
# This is a Python script file intended for quickly setting up test scrips
# It is prepared for 2-4 serial interfaces with log file, time stamps and simple TK surface
#
# usable serial commands:
#   comA.open(), comA.close(), comA.isOpen(), comA.module_name["text"], 
#   answerlist = comA.write_and_check_answer("ATI",       ["OK", "ERROR"],0.5)
#   answerlist = comA.write_and_check_answer("ATI")      # checks per default for ["OK", "ERROR"], 1.0
#                comA.write                 ("ATI")
#   answerstr  = comA.check_urc_answer      (             ["SYSSTART"],0.5)    # blocking with timeout
#   answerlist = comA.grab_receive_stream(                   ["URC"])             # not blocking answer received
#   mmi.atoi(string)
#   mmi.stop_script()
# ---------------------------------------------------------------------------

import sys
import threading
import time
import mylib       # classes: COMparser, Hauptfenster, COM-to-UI-callbacks
import subprocess  # call exe; nonblocking: Popen

# --------------------------- USER code ----------------------------------------
no_of_com_ports = 4                 # select 1-4 visible COM ports
headline    =    "Audio test"
description =    "Audio test for DSB \n using 4 COM ports"
   

def button1_script():               # is being called when UI button is pressed

    loops = mmi.window.loopcount.get()
    phoneB = mmi.window.phoneB.get()
    phoneC = mmi.window.phoneC.get()

    comB.setRTS(True)
    comB.write_and_check_answer("ATI")
    comB.write_and_check_answer("AT^SAIC=1,\"\",\"\",\"\",0,0,1,0,0") # module master mode (default)

    comC.setRTS(True)
    comC.write_and_check_answer("ATI")
    comC.write_and_check_answer("AT^SAIC=1,\"\",\"\",\"\",0,0,1,0,0") # module master mode (default)

    comD.write_and_check_answer("DSP=off")
    comA.write_and_check_answer("slave")               # slave mode (default)
    comD.write_and_check_answer("DSP=detect, netw")

    for n in range(loops) :     
       comA.write("SINUS=750Hz, 200ms, -8dB, netw")
       comD.grab_receive_stream([])                               # start collecting answers
       time.sleep(1.0)
       answerlist = comD.grab_receive_stream(["detected"])        # return all answers received
       for k in range (len(answerlist)) :
             a=answerlist[k].replace('=',',')                 # e.g. >  f= 750Hz, -34dB, 533msec detected
             tok = a.split(',')
             hz = mmi.atoi(tok[1])
             db = mmi.atoi(tok[2])
             ms = mmi.atoi(tok[3])
             print("Test: ", hz,db,ms)                  # now we can start the evaluation
             if ((hz==750) and (db > -13) and (ms > 150)) :
                 result.append("pass")

                 

#       time.sleep(0.5)                                 # wait 0.5 seconds
    print (result)
    print (result.count("pass"))
    print_and_log ("Script A finished")
    mmi.stop_script()

def button2_script():               # is being called when UI button is pressed
    comA.write_and_check_answer("ATI")
    mmi.stop_script()



#---------------------------- Logging and Printing ------------------------------

lock_logfile=threading.Lock()   # synchronizing the threads

def print_and_log(s):           # used by com_parser write_ and by receive thread
    lock_logfile.acquire()      # synchronizing the threads
    if mmi.window.timestamp.get() :             # check window checkmark status
        s = time.strftime("%H:%M,%S: ") + s
    print(s)                    # debug print;  comment this out if logfile is sufficient
    if mmi.window.logging.get() :               # check window checkmark status
       try :
          filename = mmi.window.logfilename.get()  # grab namestring from window
          mmi.logfile = mmi.open_logfile(filename)
          mmi.logfile.write(s +"\n")               # logfile print
          mmi.logfile.close()
       except : pass
    lock_logfile.release()

#---------------------------- MAIN() - do not touch!-----------------------------

mmi = mylib.mmi(script1 = button1_script,
                script2 = button2_script,     
#                script3 = button3_script,
                no_of_com_ports = no_of_com_ports,
                print_and_log = print_and_log,# function
                headline = headline,          # string
                description = description)    # string
try :
   comA=mmi.window.comA       # rename com port related objects and functions
   comB=mmi.window.comB       # rename com port related objects and functions
   comC=mmi.window.comC       # rename com port related objects and functions
   comD=mmi.window.comD       # rename com port related objects and functions
except : pass
                            
print("Start")

mmi.window.mainloop()      # runs until main window is closed
                           # don't call any window functions from this moment
mmi.close_all_com_ports()

print("Stop")

