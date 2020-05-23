
class config:

   no_of_loops = 10   # read this number from screen with   n=window.loopcount.get()

   preferredCOMA = ["COM22", "COM23","COM13"]
   preferredCOMB = ["COM3","COM14"]
   preferredCOMC = ["COM23","COM14"]
   preferredCOMD = ["COM24","COM14"]
   
# 1...8 buttons on the left side format:["name", "AT-command"]
   button1 = ["ATI1","ATI1"]
   button2 = ["AT^SCFG?","AT^SCFG?"]
   button3 = ["AT+cpin?","AT+CPIN?"]
   button4 = ["URC's","AT+cmee=2;^scks=1;+creg=2;+cpin?; +CIND=,,1,1,,1 ; +CMER=2,0,0,2; ^SIND=audio,1"]
   button5 = ["AT^SPOW=1,0,0","AT^SPOW=1,0,0"]
   button8 = ["AT^cicret=swn","AT^cicret=swn"]

   time_between_AT_cmds = 0.05           # seconds
   
   local_cmd_echo = 0                    # checkbutton default
   logging        = 1                    # checkbutton default
   logfilename    = "logfile.log"        # can be changed by mmi
   
#  uncomment if you want to use phone numbers
#   phoneA         = "+86..."            # usage:  str=mmi.window.phoneA.get() 
   phoneB         = "+86..."             # usage:  str=mmi.window.phoneB.get() 
   phoneC         = "+86..."             # usage:  str=mmi.window.phoneC.get()