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
import subprocess   # call exe; nonblocking: Popen

# --------------------------- USER code ----------------------------------------
no_of_com_ports = 4                 # select 1-4 visible COM ports
headline    =    "Audio test"
description =    "Audio test for DSB \n using 4 COM ports"
#logfilename = "logfile.log"
   

def button1_script():               # is being called when UI button is pressed

    loops = mmi.window.loopcount.get()
    phone1 = mmi.window.phoneB.get()
    phone2 = mmi.window.phoneC.get()
    result1=[]
    result2=[]
    result3=[]
    result4=[]

    comA.write_and_check_answer("slave")      # slave mode (default)       
    comB.setRTS(True)
    comB.write_and_check_answer("ATI")
    comB.write_and_check_answer("AT^SAIC=1,\"\",\"\",\"\",0,0,1,0,0") # module master mode(default)
#   comB.write_and_check_answer("AT^SXRAT=0")
#   comB.write_and_check_answer('AT+cpin="1111"')
    comB.write_and_check_answer("AT^SNFS=1")
    comB.write_and_check_answer("AT+COPS=0")
    
   
    comC.setRTS(True)
    comC.write_and_check_answer("ATI")
    comC.write_and_check_answer("AT^SAIC=1,\"\",\"\",\"\",0,0,1,0,0") # module master mode(default)
#   comC.write_and_check_answer("AT^SXRAT=0")
    comC.write_and_check_answer('AT+cpin="1111"')
    comC.write_and_check_answer("AT^SNFS=1")
    comC.write_and_check_answer("AT+COPS=0")
    comD.write_and_check_answer("slave")               # slave mode (default)

    time.sleep(5)                                      # wait 5s for network connection
    
    comB.write_and_check_answer("atd"+ phone2 +";")    # module1 call module2

    answerstr1 = comC.check_urc_answer(["RING"],5.0)
    if "RING" in answerstr1 :
        comC.write_and_check_answer("ata")
        
    comD.write_and_check_answer("DSP=off")
    comD.write_and_check_answer("DSP=detect, netw")
    
    for n in range(loops) :     
       comA.write("SINUS=750Hz, 200ms, -8dB, netw")            # comA sending and comD receiving
       comD.grab_receive_stream([])                               # start collecting answers
       time.sleep(1.0)
       answerlist1 = comD.grab_receive_stream(["detected"])        # return all answers received
       for k in range (len(answerlist1)):
             a1=answerlist1[k].replace('=',',')                 # e.g. >  f= 750Hz, -34dB, 533msec detected
             tok1 = a1.split(',')
             hz1 = mmi.atoi(tok1[1])
             db1 = mmi.atoi(tok1[2])
             ms1 = mmi.atoi(tok1[3])
             print("Test_MO_send: ", hz1,db1,ms1)                  # now we can start the evaluation
             if ((hz1==750) and (db1 > -20) and (ms1 > 150)) :
                 result1.append("pass")
    comD.write("DSP=OFF")
    comA.write("SINUS=OFF")
    time.sleep(0.5)                                                # wait 0.5 seconds
    
    print (result1)                                                # Print MO sending test result
    print_and_log ("Result_MO_send:"+str(result1.count("pass")))
    
    time.sleep(3)                                                   # wait 3 seconds to swith the sending and receiving side

    comA.write_and_check_answer("DSP=off")
    comA.write_and_check_answer("DSP=detect, netw")
    for n in range(loops) :     
       comD.write("SINUS=750Hz, 200ms, -8dB, netw")            # comD sending and comA receiving 
       comA.grab_receive_stream([])                               # start collecting answers
       time.sleep(1)
       answerlist2 = comA.grab_receive_stream(["detected"])        # return all answers received
       for k in range (len(answerlist2)):
             a2=answerlist2[k].replace('=',',')                 # e.g. >  f= 750Hz, -34dB, 533msec detected
             tok2 = a2.split(',')
             hz2 = mmi.atoi(tok2[1])
             db2 = mmi.atoi(tok2[2])
             ms2 = mmi.atoi(tok2[3])
             print("Test_MT_send: ", hz2,db2,ms2)                  # now we can start the evaluation
             if ((hz2==750) and (db2 > -20) and (ms2 > 150)) :
                 result2.append("pass")
    comA.write("DSP=OFF")
    comD.write("SINUS=OFF")
    time.sleep(0.5)                                 # wait 0.5 seconds
           
    print (result2)                                     # Print MT sending test result
    print_and_log ("Result_MT_send:"+str(result2.count("pass")))
    comB.write_and_check_answer("ath")   # end the call after the test (module1 call module2: wbca1 sending,wbca2 receiving and then wbca2 sending,wbca1 receiving)
    
    time.sleep(2)

    comB.write_and_check_answer("at+cfun=1,1")
    comC.write_and_check_answer("at+cfun=1,1")      #Restart the modules for next round test
    time.sleep(20)                                   #wait 15s for module restart
    
    comA.write_and_check_answer("slave")      # slave mode (default)       
#   comC.setRTS(True)
    comC.write_and_check_answer("ATI")
    comC.write_and_check_answer("AT^SAIC=1,\"\",\"\",\"\",0,0,1,0,0") # module master mode(default)
#   comC.write_and_check_answer("AT^SXRAT=0")
    comC.write_and_check_answer('AT+cpin="1111"')
    comC.write_and_check_answer("AT^SNFS=1")
    comC.write_and_check_answer("AT+COPS=0")
    
#   comB.setRTS(True)
    comB.write_and_check_answer("ATI")
    comB.write_and_check_answer("AT^SAIC=1,\"\",\"\",\"\",0,0,1,0,0") # module master mode(default)
#   comB.write_and_check_answer("AT^SXRAT=0")
    comB.write_and_check_answer('AT+cpin="1111"')
    comB.write_and_check_answer("AT^SNFS=1")
    comB.write_and_check_answer("AT+COPS=0")
    comD.write_and_check_answer("slave")               # slave mode (default)

    time.sleep(5)                                      # wait 5s for network connection
    
    comC.write_and_check_answer("atd"+ phone1 +";")    # module2 call module1

    answerstr3 = comB.check_urc_answer(["RING"],5.0)
    if "RING" in answerstr3 :
        comB.write_and_check_answer("ata")
        
    time.sleep(5)
     
    comD.write_and_check_answer("DSP=off")
    comD.write_and_check_answer("DSP=detect, netw")
    
    
    for n in range(loops) :     
       comA.write("SINUS=750Hz, 200ms, -8dB, netw")             # comA sending and comD receiving
       comD.grab_receive_stream([])                             # start collecting answers
       time.sleep(1)
       answerlist3 = comD.grab_receive_stream(["detected"])     # return all answers received
       for k in range (len(answerlist3)):
             a3=answerlist3[k].replace('=',',')                 # e.g. >  f= 750Hz, -34dB, 533msec detected
             tok3 = a3.split(',')
             hz3 = mmi.atoi(tok3[1])
             db3 = mmi.atoi(tok3[2])
             ms3 = mmi.atoi(tok3[3])
             print("Test_MO_send: ", hz3,db3,ms3)               # now we can start the evaluation
             if ((hz3==750) and (db3 > -20) and (ms3 > 150)) :
                 result3.append("pass")
    comD.write("DSP=OFF")
    comA.write("SINUS=OFF")
    time.sleep(0.5)                                             # wait 0.5 seconds
    
    print (result3)                                                # Print MO sending test result
    print_and_log ("Result_MO_send:"+str(result3.count("pass")))
    
    time.sleep(3)                                                   # wait 3 seconds to swith the sending and receiving side

    comA.write_and_check_answer("DSP=off")
    comA.write_and_check_answer("DSP=detect, netw")
    for n in range(loops) :     
       comD.write("SINUS=750Hz, 200ms, -8dB, netw")             # comD sending and comA receiving 
       comA.grab_receive_stream([])                             # start collecting answers
       time.sleep(1)
       answerlist4 = comA.grab_receive_stream(["detected"])     # return all answers received
       for k in range (len(answerlist4)):
             a4=answerlist4[k].replace('=',',')                 # e.g. >  f= 750Hz, -34dB, 533msec detected
             tok4 = a4.split(',')
             hz4 = mmi.atoi(tok4[1])
             db4 = mmi.atoi(tok4[2])
             ms4 = mmi.atoi(tok4[3])
             print("Test_MT_send: ", hz4,db4,ms4)                  # now we can start the evaluation
             if ((hz4==750) and (db4 > -20) and (ms4 > 150)) :
                 result4.append("pass")
    comA.write("DSP=OFF")
    comD.write("SINUS=OFF")
    time.sleep(0.5)                                 # wait 0.5 seconds
           
    print (result4)                                     # Print MT sending test result
    print_and_log ("Result_MT_send:"+str(result4.count("pass")))
    comC.write_and_check_answer("ath") 

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
                no_of_com_ports = no_of_com_ports,
                print_and_log = print_and_log,# function
                headline = headline,          # string
                description = description)    # string
try :
   comA=mmi.window.comA       # com port related objects and functions
   comB=mmi.window.comB       # com port related objects and functions
   comC=mmi.window.comC       # com port related objects and functions
   comD=mmi.window.comD       # com port related objects and functions
except : pass
                            
print("Start")
#print (sys.version_info)  #Python version

mmi.window.mainloop()      # runs until main window is closed


# ---------------- EXIT - closing all threads and cleaning up ---------------------
       # don't call any window functions from this moment
mmi.Script_running=False 
try :
   mmi.serA.closecom()
   mmi.serB.closecom()
   mmi.serC.closecom()
   mmi.serD.closecom()
except : pass

print("Stop")

