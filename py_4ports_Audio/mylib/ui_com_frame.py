# This class draws the Window for each COM port
# Copyright: Gemalto M2M 2018, Marten Petschke

import sys
if sys.version_info < (3,0,0):                  # Python2 / Python3 difference
   import Tkinter as tk                         # Python2
else:
   import tkinter as tk                         # Python3
import time
import mylib       # classes: COMparser, Hauptfenster, config, buttons

LIGHTGRAY = "#F0F0ED" # standard background colour: Gray
GREEN     = "chartreuse"
BLUE      = "skyblue"

class COMfenster(tk.Frame):        # draws a window for each Com port
    def __init__(cc, mainwindow, mmi, ser, AB, print_and_log):
        cc.mainwindow = mainwindow # class
        cc.ser = ser               # class
        cc.mmi = mmi               # class
        cc.AB = AB                 # string "A" or "B"
        cc.print_and_log = print_and_log  # function
        cc.open_close_toggle = 0            # Flag
        cc.inter_at_timeout = time.time()
        cc.Cinterion=0             # local var
        
        cc.frameCOM =        tk.Frame(mainwindow, relief=tk.RIDGE, bd=2) #we place the frame later

        cc.module_name =     tk.Label(cc.frameCOM, text="", borderwidth=1, fg="dark orange")
        cc.module_name.grid  (row=1, column=1, columnspan=10, sticky="EW")

        cc.comport =         tk.StringVar()
        cc.comport.set       (cc.mmi.sel_com_port(AB))     # selects the current COM port 
        cc.COMselect_b =     tk.OptionMenu(cc.frameCOM, cc.comport, *(mmi.comlist))
        cc.COMselect_b.grid  (row=5, column=1, sticky="EWNS")
        cc.COMselect_b.config(font=("arial",8))
        cc.comport.trace     ("w", cc.com_var_mod)         # if value was modified close com port
        cc.comport.trace     ("r", cc.com_var_read)

        cc.open_b =          tk.Button(cc.frameCOM, text="Open", command=cc.openclose, font=("arial",7) )
        cc.open_b.grid       (row=5, column=2, pady=2, sticky="EWNS")

        baudrate_list =      ["9600", "19200", "14400", "57600", "115200", "230400", "460800", "921600", "3000000"]
        cc.baudrate =        tk.StringVar()
        cc.baudrate.set      ("115200")                    # selects the default Baudrate 
        cc.br_b =            tk.OptionMenu(cc.frameCOM, cc.baudrate, *(baudrate_list))
        cc.br_b.grid         (row=5, column=3, sticky="EWNS")
        cc.br_b.config       (font=("arial",6))
        cc.baudrate.trace    ("w", cc.baud_var_mod)        # if value was modified change physical BR

#        cc.flow_b =          tk.Button(cc.frameCOM, text="Flow", command=cc.setHWflow, font=("Arial",7))
#        cc.flow_b.grid       (row=5, column=4, pady=2, sticky="EWNS")

        cc.rts_b =           tk.Button(cc.frameCOM, text="RTS", command=cc.setRTS, font=("Arial",7))
        cc.rts_b.grid        (row=5, column=5, pady=2, sticky="EWNS")

        cc.dtr_b =           tk.Button(cc.frameCOM, text="DTR", command=cc.setDTR, font=("Arial",7))
        cc.dtr_b.grid        (row=5, column=6, pady=2, sticky="EWNS")


        cc.clear_b =         tk.Button(cc.frameCOM, text="Clear Rx", command=cc.clear_listbox, font=("Arial",7))
        cc.clear_b.grid      (row=5, column=9, columnspan=2, pady=2, sticky="EWNS")
        
        cc.ATcommand =       tk.StringVar() # additional var needed to change the display later
        cc.ATcommand.set     ("")          
        cc.ATcommand_e =     tk.Entry(cc.frameCOM, textvariable = cc.ATcommand, font=("courier new",9))
        cc.ATcommand_e.grid  (row=10, column=1, columnspan=10, ipady=2, pady=5, sticky="WE")
        cc.ATcommand_b =     tk.Button(cc.frameCOM, text="send", command=cc.insert_AT_cmd, font=("arial",7))
        cc.ATcommand_b.grid  (row=10, column=10, sticky="E")

        cc.listbox =         tk.Listbox(cc.frameCOM, selectmode = tk.EXTENDED, font=("courier new",9), width = 30) # , height = 12, width = 40)   # height,widthcharacters
        cc.vscrollbar =      tk.Scrollbar(cc.frameCOM, command=cc.listbox.yview, orient=tk.VERTICAL)
        cc.hscrollbar =      tk.Scrollbar(cc.frameCOM, command=cc.listbox.xview, orient=tk.HORIZONTAL)
        cc.listbox.config    (yscrollcommand = cc.vscrollbar.set)
        cc.listbox.config    (xscrollcommand = cc.hscrollbar.set)
        cc.listbox.grid      (row=12, column=1, columnspan=10, sticky="WENS")
        cc.vscrollbar.grid   (row=12, column=10, rowspan=9 , sticky="NSE")
        cc.hscrollbar.grid   (row=22, column=1, columnspan=9, sticky="WSE")

        cc.ATcommand_e.bind("<Return>", cc.enter )
        cc.ATcommand_e.bind("<Key>",    cc.key )
        cc.history = []
        cc.hist_current = 0

    def com_var_mod(cc,a,b,c):
#        print ("com changed",a,b,c)
        cc.close()

    def com_var_read(cc,a,b,c):
#        print ("com read",a,b,c)
       if cc.mmi.Script_running == False :  cc.refresh_comlist()

    def baud_var_mod(cc,a,b,c):
#        print ("baud changed",a,b,c)
       try :
          cc.ser.baudrate = int(cc.baudrate.get())
       except : pass
			 
    def clear_listbox(cc):
        cc.listbox.delete(0,tk.END)

    def check_RTS_DTR_flow_display(cc):
       if cc.ser.isOpen():
           if cc.ser.rts_ == True :
              cc.rts_b['bg']  = BLUE
           else :
              cc.rts_b['bg']  = LIGHTGRAY
           if cc.ser.dtr_ == True :
              cc.dtr_b['bg']  = BLUE
           else :
              cc.dtr_b['bg']  = LIGHTGRAY
           try :
              if cc.ser.rtscts_ == True :
                 cc.flow_b['bg'] = BLUE
              else :
                 cc.flow_b['bg'] = LIGHTGRAY
           except : pass
       else :
          cc.rts_b['bg']      = LIGHTGRAY
          cc.dtr_b['bg']      = LIGHTGRAY
          try :
             cc.flow_b['bg']     = LIGHTGRAY
          except : pass
             
    def setHWflow(cc, val=None):
       if cc.ser.isOpen():
           if val==None :
              if cc.ser.rtscts_== False :
                 cc.ser.rtscts_ = True
              else :
                 cc.ser.rtscts_= False
           else :
               cc.ser.rtscts_= val

           if cc.ser.rtscts_== True :
              cc.ser.rtscts = cc.ser.rtscts_  # Pyserial v2/3
              cc.ser.rts_ = False
#              cc.ser.rts  = cc.ser.rts_   # Pyserial v3:
              cc.ser.setRTS (cc.ser.rts_)  # Pyserial v2:
           else :
              cc.ser.rtscts = cc.ser.rtscts_  # Pyserial v2/3
       cc.check_RTS_DTR_flow_display()

    def setRTS(cc, val=None):
       if cc.ser.isOpen():
           if val==None :
              if cc.ser.rts_== False :
                 cc.ser.rts_ = True
              else :
                 cc.ser.rts_= False
           else :
               cc.ser.rts_ = val

           if cc.ser.rts_== True :
#              cc.ser.rts  = cc.ser.rts_   # Pyserial v3:
              cc.ser.setRTS (cc.ser.rts_)  # Pyserial v2:
              cc.ser.rtscts_ = False
              cc.ser.rtscts = cc.ser.rtscts_  # Pyserial v2/3
           else :
#              cc.ser.rts  = cc.ser.rts_   # Pyserial v3:
              cc.ser.setRTS (cc.ser.rts_)  # Pyserial v2:
       cc.check_RTS_DTR_flow_display()

    def setDTR(cc, val=None):
       if cc.ser.isOpen():
          if val==None :
             if cc.ser.dtr_== False :
                 cc.ser.dtr_ = True
             else :
                 cc.ser.dtr_= False
          else :
               cc.ser.dtr_ = val

#         cc.ser.dtr  = cc.ser.dtr_   # Pyserial v3:
          cc.ser.setDTR (cc.ser.dtr_)  # Pyserial v2:
       cc.check_RTS_DTR_flow_display()
        
# ----------- This function is part of the receive thread ---------------      
    def received_line(cc, line):           # all received data arrives in this call back function
        cc.print_and_log(cc.AB + ": " + line)
        cc.listbox.insert(tk.END, line)    # copy all received data to tk-listbox 
        cc.listbox.see(tk.END)
        cc.check_for_ATI(line)
# -----------------------------------------------------------------------
  
    def check_for_ATI(cc, line):
        if cc.Cinterion == 1 :
           cc.Cinterion=0
           cc.module_name["text"]=line     # this line should contain the module name
        if "Cinterion" in line :
           if "\"" not in line :           # because of ^SCFG contains Cinterion too
              cc.Cinterion=1
           
    def insert_AT_cmd(cc):
         line=cc.ATcommand.get()
         cc.write(line) #access the Serial driver


    def openclose(cc):
        if cc.open_close_toggle == 0 :
           cc.open()
        else :
           cc.close()

    def refresh_comlist(cc):       
       cc.COMselect_b['menu'].delete(0, 'end') # Reset var and delete all old options

       cc.mmi.generate_new_COMport_list()  # global list
       for item in cc.mmi.comlist:         # Insert list of new options (tk._setit hooks them up to var)
          cc.COMselect_b['menu'].add_command(label=item, command=tk._setit(cc.comport, item))

    def enter(cc, enter):
       try :
#        if cc.mainwindow.focus_get() == cc.ATcommand_e :
           command=cc.ATcommand.get()
           cc.history.append(command)
           cc.hist_current = len(cc.history)-1
           cc.write(command)
       except : pass

    def key(cc, keyname):         # up and down
       try :
#        if cc.mainwindow.focus_get() == cc.ATcommand_e :
           if keyname.keycode == 38 :
              if cc.hist_current > 0 :
                 cc.hist_current -= 1
                 cc.ATcommand.set(cc.history[cc.hist_current])
           if keyname.keycode == 40 :
              if cc.hist_current < len(cc.history)-1 :
                 cc.hist_current += 1
                 cc.ATcommand.set(cc.history[cc.hist_current])
       except : pass

# ------------------------ User commands: ---------------------------
           
    def isOpen(cc):
        cc.ser.isOpen()
        
    def open(cc):
        if cc.ser.opencom(cc.comport.get(), int(cc.baudrate.get()) , cc.received_line):      #grab string from MMI and open
           cc.COMselect_b['bg'] =GREEN
           cc.open_close_toggle = 1              
           cc.check_RTS_DTR_flow_display()

    def close(cc):
        cc.ser.closecom()
        cc.COMselect_b['bg']=LIGHTGRAY
        cc.open_close_toggle = 0
        cc.check_RTS_DTR_flow_display()

    def write(cc, line):       #is called for Enter key and SEND button
       if cc.ser.isOpen()   == False : return[]

       cc.ser.write_(line)
       if (cc.mainwindow.echo.get()) :                    # check the button status
          cc.print_and_log(cc.AB + "> " + line)
          cc.listbox.insert(tk.END, line)
          cc.listbox.see(tk.END)

    def write_and_check_answer(cc, command, rqanswerlist=["OK", "ERROR"], timeout=1.0): # blocking until answer received
       if cc.ser.isOpen()       == False : return[]
       if cc.mmi.Script_running == False : return[]       # this allows to stop the script in some way 
       
       wait=(cc.inter_at_timeout - time.time())           # wait 100msec between commands
       if (wait > 0) : time.sleep (wait)
       cc.ser.answerflag = 1                              # begin writing into answer list
       cc.ser.answerlist = []
       cc.write(command)                                  # write to COM port and logg
       
       cc._check_urc_answer_(rqanswerlist, timeout)
       
       cc.inter_at_timeout = time.time() + mylib.config.time_between_AT_cmds
       return cc.ser.answerlist                           # returns the whole list of answers including "OK"


    def check_urc_answer(cc, rqanswerlist=[], timeout = 2):  # blocking until answer received
       if cc.ser.isOpen()       == False : return ""
       if cc.mmi.Script_running == False : return ""       # this allows to stop the script in some way 

       cc.ser.answerflag = 1                           # rcv task begins writing into answer list
       cc.ser.answerlist = []
       answer = cc._check_urc_answer_(rqanswerlist, timeout)

       return answer                                      # returns last answer string 

          
    def grab_receive_stream(cc, rqanswerlist=[], reset=0):      # not blocking answer received
       if cc.ser.isOpen()       == False : return[]
       if cc.mmi.Script_running == False : return[]       # this allows to stop the script in some way 

       if reset == 1 :
          cc.ser.URCrcvflag = 0                           # reset
          cc.ser.URCrcvlist = []
          return
          
       cc.ser.URCrcvflag = 1
       retlist = cc._check_urc_answer2_(rqanswerlist, cc.ser.URCrcvlist)
       return retlist
          
       
#     private function:
    def _check_urc_answer2_(cc, rqanswerlist, URCrcvlist):  # not blocking 
       retlist=[]
    
       for nr in range (len(URCrcvlist)) :
          if (rqanswerlist == [] ) :
             retlist.append(URCrcvlist[0])
          else :
             for i in range(len(rqanswerlist)) :            # waiting for receive thread
                if rqanswerlist[i] in URCrcvlist[0] :
                   retlist.append(URCrcvlist[0])
          del URCrcvlist[0]  
       
       return retlist

       
    def _check_urc_answer_(cc, rqanswerlist, timeout=2.0):  # blocking until answer received

       t=time.time() + timeout
       nr = 0
       while cc.mmi.Script_running and (t > time.time()): # timer!
          len_answers = len(cc.ser.answerlist)            # new line received?
          if len_answers > nr :
             for i in range(len(rqanswerlist)) :          # waiting for receive thread
                   if rqanswerlist[i] in cc.ser.answerlist[nr] :
#                   t = time.time()                       # break doesn't work here
#                   print(cc.ser.answerlist[nr])
                      cc.ser.answerflag = 0
                      return cc.ser.answerlist[nr]
             nr += 1
             time.sleep(0.01)        # magic! just to give some time to the receive thread
       cc.ser.answerflag = 0
       
       return ""
        
#---------------------------------------------------------------------------------------------
