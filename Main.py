import threading
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation
from tkinter import *
import sys #startet die tk umgebung
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
    
    
root = Tk.Tk()
var = 0

def countVar(variable):
    while variable < 5:
        variable +=1
        time.sleep(1)
        print(variable)
    print('hi')
        


def createNewThread():
    print('---')
    print(threading.active_count())
    print('---')
    counter = threading.Thread(target = countVar,name = 'test',args=(var,))
    counter.start()


button = Button(root, text = 'Click',command = createNewThread)
labl = Label(root, text = var)
button.pack()
labl.pack(side = 'bottom')
    
    
    
root.mainloop()