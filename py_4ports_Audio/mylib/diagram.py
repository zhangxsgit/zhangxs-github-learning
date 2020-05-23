# Copyright: Gemalto M2M 2018, Marten Petschke

import sys
if sys.version_info < (3,0,0):                  # Python2 / Python3 difference
   import Tkinter as tk                         # Python2
else:
   import tkinter as tk                         # Python3
import time
from decimal import Decimal
import math                                     # log

bg_color = "white"
fg_color = "black"

class diagram(tk.Frame):

    def __init__(diagram, headline, 
                 x_min  = 0, x_max  = 100,
                 y_min  = 0, y_max  = 100,
                 x_tick = 0, y_tick = 0,
                 w_width = 450,
                 h_height = 200, 
                 x_text = "x", 
                 y_text = "y",                 
                 **options):

        diagram.master = tk.Toplevel()   # store on class level to use "master.destroy and master.bind
        tk.Frame.__init__(diagram, master=diagram.master, **options)
        diagram.master.title(headline)                      #Ueberschrift
        diagram.master.wm_iconbitmap('mylib\diagram.ico')
#        diagram.master.resizable(True, True)
        
        diagram.x_min = x_min
        diagram.x_max = x_max
        diagram.x_text = x_text
        diagram.y_min = y_min
        diagram.y_max = y_max
        diagram.y_text = y_text
        diagram.x_diff = diagram.x_max - diagram.x_min
        diagram.y_diff = diagram.y_max - diagram.y_min
        diagram.w_width = w_width
        diagram.h_height = h_height
        if x_tick==0 :
           diagram.x_tick = round(diagram.x_diff, -(int(math.log(diagram.x_diff,10))))/10 # we want 10 ticks
        else : diagram.x_tick = x_tick
        if y_tick==0 :
           diagram.y_tick = round(diagram.y_diff, -(int(math.log(diagram.y_diff,10))))/5 # we want 5 ticks
        else : diagram.y_tick = y_tick

        diagram.list_of_points=[]  # [[x, y, color]]
        diagram.list_of_colors=[]  # ["color",...]
        diagram.list_of_curves=[]  # [ [x,y],...]
        diagram.o=5                # left and bottom offset pixel
        diagram.r=20               # upper and right headroom pixel
        diagram.y_width  = 55      # 5 char + 1 line
        diagram.x_height = 40      # 2 lines
    
        #        diagram.frame = tk.Frame(diagram,bg=bg_color, width=300, height=210, pady=0)
        diagram.frame = tk.Frame(diagram, bg=bg_color, pady=0)
        diagram.frame.grid( sticky="NSEW", columnspan=2, rowspan=2)
        diagram.canvas = tk.Canvas(diagram.frame, width = diagram.w_width, height = diagram.h_height, bd=0, highlightthickness=0, bg = bg_color) # Hintergrund Diagramm
        diagram.canvas.grid(row=0, column=1, sticky='NSEW')

        diagram.ycanvas = tk.Canvas(diagram.frame, width = diagram.y_width, height = 100, bg=bg_color, bd=0, highlightthickness=0, relief='ridge')     # 100pxs nur ein Platzhalter
        diagram.ycanvas.grid(row=0, column=0, sticky='NSEW')

        diagram.xcanvas = tk.Canvas(diagram.frame, width = 100,height = diagram.x_height, bg=bg_color, bd=0, highlightthickness=0, relief='ridge')
        diagram.xcanvas.grid(row=1, column=1, sticky='NSEW')
        diagram.redraw_canvas()
        
        diagram.bind("<Configure>", diagram.on_resize) # sends window events to on_resize()

    def on_resize(diagram,event):
#        print("event.width: %s" , diagram.winfo_width())
#        print("winfo_height: %s" , diagram.winfo_height())
#        print ("winfo_geometry: %s" , diagram.winfo_geometry())
        diagram.d_width  = diagram.winfo_width() -diagram.y_width   # remaining width for diagram
        diagram.d_height = diagram.winfo_height()-diagram.x_height  # remaining higth for diagram

#        print (diagram.winfo_width(), diagram.winfo_height(), diagram.d_width, diagram.d_height)

        # resize the canvas 
        diagram.canvas.config(width=diagram.d_width, height=diagram.d_height)
        diagram.calc_new_xy_max_limits()
        diagram.redraw_canvas()                          # after rescaling we have to redraw the empty diagram
        diagram.redraw_all_curves()

    def redraw_canvas(diagram):                 #after rescaling we have to redraw the empty diagram
        diagram.canvas.delete('all')
        diagram.xcanvas.delete('all')
        diagram.ycanvas.delete('all')
        diagram.w = float(diagram.canvas.config('width')[4])-1   # fetching the current window size
        diagram.h = float(diagram.canvas.config('height')[4])-1
        diagram.px_x = (diagram.w-diagram.r) / (diagram.x_diff / diagram.x_tick) # pixel pro Teilstrich
        diagram.px_y = (diagram.h-diagram.r) / (diagram.y_diff / diagram.y_tick)
        diagram.xcanvas.create_text(diagram.w/2, 25, font=("Arial",10,'italic'),fill = fg_color, text=diagram.x_text, anchor='center') # X text
        for x in diagram.frange(diagram.x_min, diagram.x_max + 1, diagram.x_tick):
            x_step = (diagram.px_x * (-diagram.x_min + x)) / diagram.x_tick
            value = Decimal(x)

            if diagram.x_min <= value <= diagram.x_max :
                coord = x_step + diagram.o, diagram.h, x_step + diagram.o, 0
                diagram.canvas.create_line(coord, fill="light blue",dash=(2, 2))                                 # grid Y axis

            if (diagram.x_max - diagram.x_min) > 30 :
               label = round(value, 0)
            else :
               label = round(value, 1)            
            coord = x_step + 9, 10
            diagram.xcanvas.create_text(coord, font=("Arial",10,'bold'),fill = fg_color, text=label,anchor='center') # X units

        if sys.version_info > (3,0,0):                  # only Python3.x can rotate
           diagram.ycanvas.create_text(12, diagram.h/2, font=("Arial",10,'italic'),fill = fg_color, text=diagram.y_text, anchor='center', angle=90) # Y text
        else :                                         # Python2  difference
           diagram.ycanvas.create_text(12, diagram.h/2, font=("Arial",10,'italic'),fill = fg_color, text=diagram.y_text[0], anchor='center') # Y text
        for y in diagram.frange(diagram.y_min, diagram.y_max + 1, diagram.y_tick):
            y_step = (diagram.px_y * (-diagram.y_min + y)) / diagram.y_tick
            value = Decimal(y)

            if diagram.y_min <= value <= diagram.y_max :
                coord = 0, diagram.h - diagram.o - y_step, diagram.w , diagram.h - diagram.o - y_step
                diagram.canvas.create_line(coord, fill="light blue",dash=(4, 2))                                 # grid X axis

            if (diagram.y_max - diagram.y_min) > 30 :
               label = round(value, 0)
            else :
               label = round(value, 1)            
            coord = 55 - diagram.o, diagram.h - y_step - diagram.o
            diagram.ycanvas.create_text(coord, font=("Arial",10,'bold'),fill = fg_color, text=label, anchor='e') # Y units

        diagram.canvas.create_line(diagram.o, diagram.h, diagram.o , 0, fill="black")                                     # Y axis
        diagram.canvas.create_polygon(diagram.o+3, 15, diagram.o-3, 15, diagram.o , 0, fill="black")                      # Y axis arrow
        diagram.canvas.create_line(0, diagram.h-diagram.o, diagram.w , diagram.h-diagram.o, fill="black")                       # X axis
        diagram.canvas.create_polygon(diagram.w - 15, diagram.h-diagram.o - 3, diagram.w - 15, diagram.h-diagram.o + 3, diagram.w , diagram.h-diagram.o, fill="black") # X axis arrow
        diagram.pack(side="left", fill=tk.BOTH, expand=True)

    def convert_dpoint_to_pxpoint(diagram, dpoint):
        x, y, visible, color, size = dpoint
        xp = (diagram.px_x * (x - diagram.x_min)) / diagram.x_tick
        yp = (diagram.px_y * (diagram.y_max - y)) / diagram.y_tick
        return (xp + diagram.o, yp + diagram.r - diagram.o)               # add pixel offsets and headrooms

        
    def calc_new_xy_max_limits(diagram):
        for color in diagram.list_of_colors : # each color is one curve
           diagram.list_of_points = diagram.list_of_curves[diagram.list_of_colors.index(color)]
           ll=len(diagram.list_of_points)
           if ll :
              for this_dpoint in diagram.list_of_points :
                  xx, yy, visible, color, size = this_dpoint
                  if diagram.y_max < yy : diagram.y_max = yy
                  if diagram.y_min > yy : diagram.y_min = yy
                  if diagram.x_max < xx : diagram.x_max = xx
                  if diagram.x_min > xx : diagram.x_min = xx
        
        
    def redraw_all_curves(diagram) :
        for color in diagram.list_of_colors : # each color is one curve
           diagram.list_of_points = diagram.list_of_curves[diagram.list_of_colors.index(color)]
           ll=len(diagram.list_of_points)
           prev_point=0
           if ll :
              for this_dpoint in diagram.list_of_points :
                  xx, yy, visible, color, size = this_dpoint
#                 if visible:
                  size = int(size/2) if int(size/2) > 1 else 1
                  this_point = diagram.convert_dpoint_to_pxpoint(this_dpoint)  
                  x, y = this_point

                  diagram.canvas.create_oval(
                     x-size, y-size,
                     x+size, y+size,
                     fill=color, outline=color
                  )
                  if prev_point :
                     try :
                        diagram.canvas.create_line(prev_point, this_point, fill=color)
                     except : pass
                  prev_point = this_point
        
    def plot_point(diagram, x, y, visible=True, color='red', size=2):     # red is default
        this_dpoint = x, y, visible, color, size
        this_point = diagram.convert_dpoint_to_pxpoint(this_dpoint)         # 

        if color not in diagram.list_of_colors : # each color is one curve
           diagram.list_of_colors.append(color)
           diagram.list_of_curves.append(list()) # new list of points
        diagram.list_of_ppoints = diagram.list_of_curves[diagram.list_of_colors.index(color)]
           
        ll=len(diagram.list_of_ppoints)
        diagram.list_of_ppoints.append(this_dpoint)
        if visible:
            size = int(size/2) if int(size/2) > 1 else 1
            x, y = this_point

            diagram.canvas.create_oval(
                x-size, y-size,
                x+size, y+size,
                fill=color, outline=color
            )
        if ll :                                 # exclude the first point
           prev_point = diagram.convert_dpoint_to_pxpoint(diagram.list_of_ppoints[ll-1])
           try :              
              diagram.canvas.create_line(prev_point, this_point, fill=color)
           except : pass
        return this_point
        

    @staticmethod
    def frange(start, stop, step, digits_to_round=3):
        while start < stop:
            yield round(start, digits_to_round)
            start += step


