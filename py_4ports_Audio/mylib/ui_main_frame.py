# This class draws the main window
# Copyright: Gemalto M2M 2018, Marten Petschke

import sys
if sys.version_info < (3,0,0):                 # Python2 / Python3 difference
   import Tkinter as tk                        # Python2
   import tkFileDialog as tkfiledialog         # Python2
   import tkFont as tkFont
else:
   import tkinter as tk                         # Python3
   import tkinter.filedialog as tkfiledialog    # Python3
   import tkinter.font as tkFont

#import serial                              # see mylib folder
#import serial.tools.list_ports
import threading
import os          # path
import subprocess  # call exe; nonblocking: Popen
import time
import mylib       # classes: COMparser, Hauptfenster, config, buttons

LIGHTGRAY = "#F0F0ED" #"white smoke"
GREEN     = "chartreuse"
ORANGE     = "orange"

class Hauptfenster(tk.Frame):
    def __init__(ff, mmi): 

        ff.mmi = mmi
        ff.master = tk.Tk()   # store on class level to use "master.destroy and master.bind
        tk.Frame.__init__(ff, master=ff.master)
        ff.master.title(mmi.headline)                      # Window title
        ff.master.wm_iconbitmap('mylib\Gemalto.ico')       # Window icon
        ff.master.geometry("800x450+0+0")                  # initial size
        ff.pack(side="left")
        ff.pack(fill=tk.BOTH, expand=True)

        # ++++++++++ setup user screen ++++++++++
        ff.createHeadline()
        ff.createLogfileWidget()
        ff.createCheckbuttonWidget()
        ff.createPhoneNoWidget()
        ff.createActionWidgets()  # horizontal
        ff.createCOMport_frame_Widgets()
        ff.createActionWidgets2()  # vertical
        ff.master.bind("<Configure>", ff.resize_window)
        # ---------------------------------------

# ++++++++++++++++++++++++++++++ Initialization: ++++++++++++++++++++++++++++        

    def createHeadline(ff):

        ff.hello = tk.Label(ff, text=ff.mmi.description, font =( 'Segoe UI',10, "bold"), borderwidth=1)
        ff.hello.grid(row=1,column=20, columnspan=25)

    def createLogfileWidget(ff):
#       Select file dialog line 2:
        ff.logfilename_l     = tk.Label(ff, text="Logfile:", borderwidth=1)
        ff.logfilename_l.grid  (row=3, column=1, ipadx=10, sticky="W")

        ff.logfilename       = tk.StringVar(ff)
        ff.logfilename.set     (mylib.config.logfilename)              # set it to some value
        ff.logfilename_e     = tk.Entry (ff, textvariable=ff.logfilename)
        ff.logfilename_e.grid  (row=3, column=20, columnspan=20, ipady=2, pady=5, sticky="WE")

        ff.logfilename_sel   = tk.Button(ff, text="...", command=ff.open_logfilemenue)
        ff.logfilename_sel.grid(row=3, column=39, sticky="E")

        if ff.mmi.no_of_com_ports == 1 :
           ff.logfilename_e.grid  (row=3, column=20, columnspan=10, ipady=2, pady=5, sticky="WE")
           ff.logfilename_sel.grid(row=3, column=29, sticky="E")


    def createCheckbuttonWidget(ff):

        ff.loopcount_l       = tk.Label(ff, text="Number of loops:", borderwidth=1)
        ff.loopcount_l.grid    (row=5, column=1, ipadx=10, sticky="W")

        ff.loopcount         = tk.IntVar(ff)
        ff.loopcount.set       (mylib.config.no_of_loops)              # set it to some value
        ff.loopcount_e       = tk.Entry(ff, textvariable = ff.loopcount, width = 6) #6 digits = 9.9Mio
        ff.loopcount_e.grid    (row=5, column=20, columnspan=3, ipady=2, pady=5, sticky="W")

        ff.timestamp         = tk.IntVar(ff)
        ff.time_b            = tk.Checkbutton(ff, text="Timestamps", variable=ff.timestamp)
        ff.time_b.deselect()
        ff.time_b.grid         (row=5, column=23, columnspan=3, sticky="W")

        ff.logging           = tk.IntVar(ff)
        ff.logging.set        (mylib.config.logging)                        # set it to some value
        ff.log_b             = tk.Checkbutton(ff, text="Log file", variable=ff.logging)
        ff.log_b.grid         (row=5, column=26, columnspan=4, sticky="W")

        ff.echo              = tk.IntVar(ff)
        ff.echo.set            (mylib.config.local_cmd_echo)                # set it to some value
        ff.echo_b            = tk.Checkbutton(ff, text="local Echo", variable=ff.echo)
#        ff.echo_b.deselect()
        ff.echo_b.grid         (row=5,column=30, columnspan=3, sticky="W")

#        ff.check =     tk.IntVar(ff)
#        ff.check_b =   tk.Checkbutton(ff, text="stop Script on error", variable=ff.check)
#        ff.check_b.deselect()
#        ff.check_b.grid        (row=5,column=5, columnspan=3, sticky="W")
        if ff.mmi.no_of_com_ports == 1 :
           ff.time_b.grid         (row=5, column=22, columnspan=2, sticky="W")
           ff.log_b.grid         (row=5, column=24, columnspan=2, sticky="W")
           ff.echo_b.grid         (row=5,column=26, columnspan=2, sticky="W")


    def createPhoneNoWidget(ff):
       try :
         ff.phoneA            = tk.StringVar(ff)
         ff.phoneA.set         (mylib.config.phoneA)              # set it to some value
         ff.phoneA_e          = tk.Entry (ff, textvariable=ff.phoneA)
         ff.phoneA_e.grid     (row=9, column=21, columnspan=9, ipadx=30, ipady=2, pady=5, sticky="EW")

         ff.phoneA_l          = tk.Label(ff, text="phoneA:", borderwidth=1)
         ff.phoneA_l.grid      (row=9, column=20, ipadx=10, sticky="W")
       except : pass

       try :
         ff.phoneB            = tk.StringVar(ff)
         ff.phoneB.set         (mylib.config.phoneB)              # set it to some value
         ff.phoneB_e          = tk.Entry (ff, textvariable=ff.phoneB)
         ff.phoneB_e.grid     (row=9, column=31, columnspan=9, ipadx=30, ipady=2, pady=5, sticky="EW")

         ff.phoneB_l          = tk.Label(ff, text="phoneB:", borderwidth=1)
         ff.phoneB_l.grid      (row=9, column=30, ipadx=10, sticky="W")
       except : pass
         
       try :
         ff.phoneC            = tk.StringVar(ff)
         ff.phoneC.set         (mylib.config.phoneC)              # set it to some value
         ff.phoneC_e          = tk.Entry (ff, textvariable=ff.phoneC)
         ff.phoneC_e.grid     (row=9, column=41, columnspan=9, ipadx=30, ipady=2, pady=5, sticky="EW")

         ff.phoneC_l          = tk.Label(ff, text="phoneC:", borderwidth=1)
         ff.phoneC_l.grid      (row=9, column=40, ipadx=10, sticky="W")
       except : pass

       try :
         ff.phoneD            = tk.StringVar(ff)
         ff.phoneD.set         (mylib.config.phoneD)              # set it to some value
         ff.phoneD_e          = tk.Entry (ff, textvariable=ff.phoneD)
         ff.phoneD_e.grid     (row=9, column=51, columnspan=9, ipadx=30, ipady=2, pady=5, sticky="EW")

         ff.phoneD_l          = tk.Label(ff, text="phoneD:", borderwidth=1)
         ff.phoneD_l.grid      (row=9, column=50, ipadx=10, sticky="W")
       except : pass

    def createActionWidgets(ff):
#       Start button line 3:
        ff.functions   = tk.Label(ff, text="Functions:", borderwidth=1)
        ff.functions.grid(row=8, column=1, ipadx=10, sticky="W")

        if ff.mmi.no_of_com_ports >= 2 :
           ff.Opencom     = tk.Button(ff, text="Open COMs",    command=ff.opencoms)
           ff.Opencom.grid  (row=8, column=20, columnspan=3, ipadx=15, pady=5, sticky="WENS")

           ff.Closecom    = tk.Button(ff, text="Close COMs",   command=ff.closecoms)
           ff.Closecom.grid (row=8, column=23, columnspan=3, ipadx=15, pady=5, sticky="WENS")

        if ff.mmi.script1 : txt="Script1"
        else :              txt="no script1"
        ff.b1_script    = tk.Button(ff, text=txt, command=ff.cb_start_script1) # no parameters possible in cb function 
        ff.b1_script.grid (row=8, column=26, columnspan=4, ipadx=1, pady=5, sticky="WENS")

        if ff.mmi.script2 : txt="Script2"
        else :              txt="no script2"
        ff.b2_script    = tk.Button(ff, text=txt, command=ff.cb_start_script2) # no parameters possible in cb function 
        ff.b2_script.grid (row=8, column=30, columnspan=3, ipadx=10, pady=5, sticky="WENS")
        
        if ff.mmi.script3 : 
           txt="Script3"
           ff.b3_script    = tk.Button(ff, text=txt,        command=ff.cb_start_script3) 
        else :
           txt="Diagr. test"
           ff.b3_script =    tk.Button(ff, text=txt, command=ff.mmi.open_diagram)
        ff.b3_script.grid (row=8, column=33, columnspan=3, ipadx=10, pady=5, sticky="WENS")

        ff.stopscript_b    = tk.Button(ff, text="Stop Scripts", command=ff.mmi.stop_script)
        ff.stopscript_b.grid (row=8,column=36, columnspan=4, ipadx=10, pady=5, sticky="WENS")

#        ff.QUIT =        tk.Button(ff, text="QUIT", fg="red",command=ff.master.destroy)
#        ff.QUIT.grid     (row=8,column=7, ipadx=10, pady=5, sticky="WENS")
        if ff.mmi.no_of_com_ports == 1 :
           ff.b1_script.grid (row=8, column=20, columnspan=2, ipadx=1, pady=5, sticky="WENS")
           ff.b2_script.grid (row=8, column=22, columnspan=2, ipadx=10, pady=5, sticky="WENS")
           ff.b3_script.grid (row=8, column=24, columnspan=2, ipadx=10, pady=5, sticky="WENS")
           ff.stopscript_b.grid (row=8,column=26, columnspan=2, ipadx=10, pady=5, sticky="WENS")


# we resize the 1-4 listboxes here:
    def resize_window(ff,event):
        pos_comAx = ff.comA.frameCOM.winfo_x() + ff.comA.listbox.winfo_x()  # 117 + 2
        pos_comAy = ff.comA.frameCOM.winfo_y() + ff.comA.listbox.winfo_y()  # 136 + 86
        font = tkFont.Font(family="courier new", size=9)
        (pxw,pxh) = (font.measure("M"),font.metrics("linespace"))
        textlines = int((ff.winfo_height() - pos_comAy - 22)/(pxh+1))          # =15+1;     font size 9 = 15px x 7px
        char_width = int((ff.winfo_width() - pos_comAx  
                   - ff.mmi.no_of_com_ports*10) / (ff.mmi.no_of_com_ports*pxw))  #font size 9 = 15px x 7px

        ff.comA.listbox.config (height = textlines, width = char_width) # resize the 2-4 listboxes
        if ff.mmi.no_of_com_ports >= 2 :
           ff.comB.listbox.config (height = textlines, width = char_width)
        if ff.mmi.no_of_com_ports >= 3 :
           ff.comC.listbox.config (height = textlines, width = char_width)
        if ff.mmi.no_of_com_ports >= 4 :
           ff.comD.listbox.config (height = textlines, width = char_width)
       
    def createCOMport_frame_Widgets(ff):

        ff.modulename     = tk.Label(ff, text="Module name:", borderwidth=1)
        ff.modulename.grid  (row=14,column=1, ipadx=10, sticky="W")

        ff.comprm         = tk.Label(ff, text="COM param:", borderwidth=1)
        ff.comprm.grid      (row=15, column=1, ipadx=10, sticky="W")

        ff.ATcommandA_l   = tk.Label(ff, text="AT-command:", borderwidth=1)
        ff.ATcommandA_l.grid(row=16, column=1, ipadx=10, sticky="W")

        if ff.mmi.no_of_com_ports > 1 : 
           ff.comA = mylib.COMfenster(mainwindow = ff,     # class
                                   mmi=ff.mmi,          # class
                                   ser=ff.mmi.serA,     # class serial interface driver
                                   AB = "A",
                                   print_and_log=ff.mmi.print_and_log)
           ff.comA.frameCOM.grid     (row=14, column=20, rowspan=11, columnspan=10, sticky="NSWE")
        else :
           ff.comA = mylib.COMfenster(mainwindow = ff,     # class
                                   mmi=ff.mmi,          # class
                                   ser=ff.mmi.serA,     # class serial interface driver
                                   AB = "",
                                   print_and_log=ff.mmi.print_and_log)
           ff.comA.frameCOM.grid     (row=14, column=20, rowspan=11, columnspan=10, sticky="NSWE")

        if ff.mmi.no_of_com_ports >= 2 :
           ff.comB = mylib.COMfenster(mainwindow = ff,     # class
                                   mmi=ff.mmi,          # class
                                   ser=ff.mmi.serB,     # class serial interface driver
                                   AB = "B",
                                   print_and_log=ff.mmi.print_and_log)
           ff.comB.frameCOM.grid     (row=14, column=30, rowspan=11,  columnspan=10, sticky="NSWE")

        if ff.mmi.no_of_com_ports >= 3 :
           ff.comC = mylib.COMfenster(mainwindow = ff,     # class
                                   mmi=ff.mmi,          # class
                                   ser=ff.mmi.serC,     # class serial interface driver
                                   AB = "C",
                                   print_and_log=ff.mmi.print_and_log)
           ff.comC.frameCOM.grid     (row=14, column=40, rowspan=11,  columnspan=10, sticky="NSWE")

        if ff.mmi.no_of_com_ports >= 4 :
           ff.comD = mylib.COMfenster(mainwindow = ff,     # class
                                   mmi=ff.mmi,          # class
                                   ser=ff.mmi.serD,     # class serial interface driver
                                   AB = "D",
                                   print_and_log=ff.mmi.print_and_log)
           ff.comD.frameCOM.grid     (row=14, column=50, rowspan=11,  columnspan=10, sticky="NSWE")

    def createActionWidgets2(ff):

       try :
          ff.cmd1      = tk.Button(ff, text=mylib.config.button1[0], command=ff.cb_command1) # no parameters possible in cb function 
          ff.cmd1.grid   (row=17,column=1, padx=2, pady=2, ipady=0, sticky="WENS")

          ff.cmd2      = tk.Button(ff, text=mylib.config.button2[0], command=ff.cb_command2) # no parameters possible in cb function 
          ff.cmd2.grid   (row=18,column=1, padx=2, pady=2, ipady=0, sticky="WENS")

          ff.cmd3      = tk.Button(ff, text=mylib.config.button3[0], command=ff.cb_command3) # no parameters possible in cb function 
          ff.cmd3.grid   (row=19,column=1, padx=2, pady=2, ipady=0, sticky="WENS")

          ff.cmd4      = tk.Button(ff, text=mylib.config.button4[0], command=ff.cb_command4) # no parameters possible in cb function 
          ff.cmd4.grid   (row=20,column=1, padx=2, pady=2, ipady=0, sticky="WENS")

          ff.cmd5      = tk.Button(ff, text=mylib.config.button5[0], command=ff.cb_command5) # no parameters possible in cb function 
          ff.cmd5.grid   (row=21,column=1, padx=2, pady=2, ipady=0, sticky="WENS")

          ff.cmd6      = tk.Button(ff, text=mylib.config.button6[0], command=ff.cb_command6) # no parameters possible in cb function 
          ff.cmd6.grid   (row=22,column=1, padx=2, pady=2, ipady=0, sticky="WENS")

          ff.cmd7      = tk.Button(ff, text=mylib.config.button7[0], command=ff.cb_command7) # no parameters possible in cb function 
          ff.cmd7.grid   (row=23,column=1, padx=2, pady=2, ipady=0, sticky="WENS")

          ff.cmd8      = tk.Button(ff, text=mylib.config.button8[0], command=ff.cb_command8) # no parameters possible in cb function 
          ff.cmd8.grid   (row=24,column=1, padx=2, pady=2, ipady=0, sticky="WENS")
       except : pass

# ---------------------------- end of init -----------------------------



# ++++++++++++++++++++++++++++++ Actions: ++++++++++++++++++++++++++++        
    def opencoms(ff):
       try :
          ff.comA.open()
          ff.comB.open()
          ff.comC.open()
          ff.comD.open()
       except : pass

    def closecoms(ff):
       try :
          ff.comA.close()
          ff.comB.close()
          ff.comC.close()
          ff.comD.close()
       except : pass


    def cb_command1(ff):
         ff.command(mylib.config.button1[1])
    def cb_command2(ff):
         ff.command(mylib.config.button2[1])
    def cb_command3(ff):
         ff.command(mylib.config.button3[1])
    def cb_command4(ff):
         ff.command(mylib.config.button4[1])
    def cb_command5(ff):
         ff.command(mylib.config.button5[1])
    def cb_command6(ff):
         ff.command(mylib.config.button6[1])
    def cb_command7(ff):
         ff.command(mylib.config.button7[1])
    def cb_command8(ff):
         ff.command(mylib.config.button8[1])

    def command(ff, command):
       done=0
       try :
          if   ff.focus_get() == ff.comB.ATcommand_e :
             ff.comB.write(command)
             done=1
          elif ff.focus_get() == ff.comC.ATcommand_e :
             ff.comC.write(command)
             done=1
          elif ff.focus_get() == ff.comD.ATcommand_e :
             ff.comD.write(command)
             done=1
       except : pass

       if done==0 :
             ff.comA.write(command)

       
    def open_logfilemenue(ff):
        filename = tkfiledialog.askopenfilename(filetypes = (("Template files", "*.py")
                                                             ,("log files", "*.log")
                                                             ,("All files", "*.*") ))
        if filename:
            ff.logfilename.set(filename)


    def cb_start_script1(ff):
       ff.b1_script['bg'] = ORANGE
       ff.mmi.start_script(ff.mmi.script1)
            
    def cb_start_script2(ff):
       ff.b2_script['bg'] = ORANGE
       ff.mmi.start_script(ff.mmi.script2)

    def cb_start_script3(ff):
       ff.b3_script['bg'] = ORANGE
       ff.mmi.start_script(ff.mmi.script3)
            
