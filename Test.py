'''
=========================
Version1.3
=========================

by MARVIN GLOTH
=========================
'''
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
#from matplotlib import style
#style.use('ggplot')

import sys #startet die tk umgebung
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
root = Tk.Tk()
#root.configure(background='white')
#Grid.rowconfigure(root,1,weight=1)
#Grid.columnconfigure(root,0,weight=1)
root.wm_title("3D-Controll")

ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM5'

#figure in canvas erzeugen 
fig=Figure(figsize=(3,3), dpi=100) 
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
plotBody = fig.add_subplot(111, projection='3d')
#canvas.get_tk_widget().pack(side=Tk.LEFT, fill=Tk.BOTH, expand=3)

def UpdatePlotWidget(i):
    global plotBody
    x,y,z=Body.updatePos(B1)
    plotBody.clear()#loescht den alten plot, damit nicht neue figuren auf alte geplotet werden
    ##Plottet in die Figurenumgebung
    plotBody.plot_surface(x, y, z, rstride=1, cstride=1)#cmap=plt.cm.hot
    plotBody.set_anchor('NE')
    plotBody.set_xlim3d(-15, 15 )
    plotBody.set_ylim3d( -15, 15 )
    plotBody.set_zlim3d( -15, 15 )
    plotBody.set_xlabel('X axis')
    plotBody.set_ylabel('Y axis')
    plotBody.set_zlabel('Z axis')
    
class Body:
    def __init__(self):
        Body.ParamTorus(self,10,5) #bei initialisierung wird im Konstruktor der Koerper Parametrisiert
        #BodyPosition.ParamKegel(self,10,10)
    
    def ParamTorus(self,Ra,Ri):
        #Parametrisiesrung Torus
        p,t= np.mgrid[0:2*np.pi:10j, 0:2*np.pi:10j] #aufloesung des Koerpers 
        self.x  = (Ra+Ri*np.cos(p))*np.cos(t)
        self.y  = (Ra+Ri*np.cos(p))*np.sin(t)
        self.z  = Ri*np.sin(p)
        
    def ParamKegel(self,h,r):
        #Parametrisiesrung Kegel
        u,v= np.mgrid[-np.pi:np.pi:5j, 0:h:5j]
        self.x = r/h * v * np.cos(u)
        self.y = r/h * v * np.sin(u)
        self.z = v #h-v aufrechter kegel
        
    def updatePos(self):
        #BodyPosition.readBodySensor(self)
        if ser.is_open:
            s =ser.readline().decode().split(',')
        else:
            s=[0,0,0,0]
        phi=float(s[0])*np.pi/180
        teta=float(s[1])*np.pi/180
        psi=float(s[2])*np.pi/180
        ##nummeric SinCos Calc 
        sinPhi =np.sin(phi)
        cosPhi =np.cos(phi)
        cosTeta=np.cos(teta)
        sinTeta=np.sin(teta)
        cosPsi =np.cos(psi)
        sinPsi =np.sin(psi)
        ##Calc Roll
        x1 = self.x
        y1 = self.y*cosPhi - self.z*sinPhi
        z1 = self.y*sinPhi + self.z*cosPhi
        ##Calc pitch
        x2 = x1*cosTeta + z1*sinTeta
        y2 = y1
        z2 =-x1*sinTeta + z1*cosTeta
        ##Calc yaw
        x3 = x2*cosPsi - y2*sinPsi
        y3 = x2*sinPsi + y2*cosPsi
        z3 = z2
        return x3,y3,z3

    
B1=Body()        
##Controll Elemente     
def _ParamTorus():
    Body.ParamTorus(B1,10,5)    
def _ParamKegel():
    Body.ParamKegel(B1,10,10)
def _comC():
    ser.open()   
def _quit():
    root.quit()     # stop mainloop
    root.destroy()  # beugt einem Fatal Python Error vor: PyEval_RestoreThread: NULL tstate
nButWidth=10                    
button1 = Tk.Button(master=root, text='TORUS', command=_ParamTorus,width=nButWidth)
#button1.pack(side=Tk.R,anchor = 'n')
button2 = Tk.Button(master=root, text='KEGEL', command=_ParamKegel,width=nButWidth)
#button2.pack(side=Tk.TOP,anchor = 'ne')                    
button3 = Tk.Button(master=root, text='Quit', command=_quit,width=nButWidth)
#button3.pack(side=Tk.TOP,anchor = 'center')
button4 = Tk.Button(master=root, text='Com Port Connect', command=_comC,width=nButWidth)
#button4.pack(side=Tk.TOP,anchor = 's')

   
canvas.get_tk_widget().grid(row=0, column=2, columnspan=2, rowspan=2,
                            sticky=W+E+N+S, padx=5, pady=5)
button1.grid(row=2, column=2)
button2.grid(row=2, column=3)
button3.grid(row=0, column=0)
button4.grid(row=0, column=1)

ani = animation.FuncAnimation(fig, UpdatePlotWidget, interval=1)
Tk.mainloop()