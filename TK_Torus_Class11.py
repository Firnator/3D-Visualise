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

#startet die tk umgebung
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
root = Tk.Tk()
#root.resizable(width=False,height=False)
root.configure(background='white')
#Grid.rowconfigure(root,1,weight=1)
#Grid.columnconfigure(root,0,weight=1)
root.wm_title("3D-Controll")

###start datawork
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM5'

def UpdatePlotWidget(i):
    global plotBody
    x,y,z=Body.updatePos(B1)
    plotBody.clear()#löscht den alten plot, damit nicht neue figuren auf alte geplotet werden
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
        Body.ParamTorus(self,10,5) #bei initialisierung wird im Konstruktor der Körper Parametrisiert
        #BodyPosition.ParamKegel(self,10,10)
    
    def ParamTorus(self,Ra,Ri):
        #Parametrisiesrung Torus
        p,t= np.mgrid[0:2*np.pi:10j, 0:2*np.pi:10j] #auflösung des Körpers 
        self.x  = (Ra+Ri*np.cos(p))*np.cos(t)
        self.y  = (Ra+Ri*np.cos(p))*np.sin(t)
        self.z  = Ri*np.sin(p)
        
    def ParamKegel(self,h,r):
        #Parametrisiesrung Kegel
        u,v= np.mgrid[-np.pi:np.pi:5j, 0:h:5j]
        self.x = r/h * v * np.cos(u)
        self.y = r/h * v * np.sin(u)
        self.z = v #h-v aufrechter kegel
        
    def readSensor(self):
        if ser.is_open:
            s =ser.readline().decode().split(',')
        else:
            s=[0,0,0,0]
        phi=float(s[0])*np.pi/180
        teta=float(s[1])*np.pi/180
        psi=float(s[2])*np.pi/180
        return phi,teta,psi
        
    def updatePos(self):
        phi,teta,psi=Body.readSensor(self)
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

#erzeugt ein element body
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

###----------------------###    
###     TKGui design     ###
###----------------------###
strBackground='white'
##erstellung Frames    
mainFrameLeft=Frame(master=root)
mainFrameRight=Frame(master=root)
mainFrameCenter=Frame(master=root)    
mainFrameLeft.pack(side=LEFT,padx=5, pady=5)
mainFrameCenter.pack(side=LEFT,padx=5, pady=5)    
mainFrameRight.pack(side=RIGHT,padx=5, pady=5)    
mainFrameLeft.configure(background=strBackground)
mainFrameRight.configure(background=strBackground)
mainFrameCenter.configure(background=strBackground)

#==========================================================================================
##frameLeft
button1 = Button(master=mainFrameLeft, text='Quit', command=_quit)
button1.pack(side=BOTTOM,anchor = 'center')
#==========================================================================================
#frameCenter
#figure in canvas erzeugen 
fig=Figure(figsize=(4,4), dpi=100) 
canvas = FigureCanvasTkAgg(fig, master=mainFrameCenter)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP,anchor = 'center', fill=Tk.BOTH, expand=3)
plotBody = fig.add_subplot(111, projection='3d')


#==========================================================================================
#frameRight
#------------------------------------------------------------------------------------------
framePlotSettings=Frame(master=mainFrameRight)
framePlotSettings.pack(side=TOP,anchor = 'n',padx=30, pady=30)
framePlotSettings.configure(background=strBackground)
#ratiobutton erzeugen----------------------------------------------
auswahl=["Torus","Kegel"]
auswahlParam=Tk.StringVar()
auswahlParam.set("Torus")
def _settingParam():
    toSet=auswahlParam.get()
    if toSet=="Torus":
        _ParamTorus()
    if toSet=="Kegel":
        _ParamKegel()
for text in auswahl:
    but=Radiobutton(master=framePlotSettings,text=text,value=text,padx = 20, variable=auswahlParam, command=_settingParam,background=strBackground)
    but.pack(side=TOP,anchor = 'n')
#button erzeugen---------------------------------------------------    
buttonQuit = Button(master=framePlotSettings, text='Quit', command=_quit)
buttonQuit.pack(side=BOTTOM,anchor = 'center')
buttonComC = Button(master=framePlotSettings, text='Com Port Connect', command=_comC)
buttonComC.pack(side=BOTTOM,anchor = 's')
Tz = Text(master=framePlotSettings, height=2, width=30)
Tz.insert(END,"-z->")
Tz.pack(side=BOTTOM)
#MotorControllButton---------------------------------------------------------------------------
frameMotorControll=Frame(master=mainFrameRight)
frameMotorControll.pack(side=BOTTOM,anchor = 's',padx=30, pady=30)
frameMotorControll.configure(background=strBackground)
#--

x,y,z=Body.readSensor(B1)
controllWidth=3
buttonPhiP=Button(master=frameMotorControll, text='+', command=_quit,width=controllWidth)
buttonPhiM=Button(master=frameMotorControll, text='-', command=_quit,width=controllWidth)
buttonTetaP=Button(master=frameMotorControll, text='+', command=_quit,width=controllWidth)
buttonTetaM=Button(master=frameMotorControll, text='-', command=_quit,width=controllWidth)
buttonPsiP=Button(master=frameMotorControll, text='+', command=_quit,width=controllWidth)
buttonPsiM=Button(master=frameMotorControll, text='-', command=_quit,width=controllWidth)
rollLab = Label(master=frameMotorControll, text="\u03A6",background=strBackground)
pitchLab = Label(master=frameMotorControll, text="\u0398",background=strBackground)
yawLab = Label(master=frameMotorControll, text="\u03A8",background=strBackground)
#rollShow = Label(master=frameMotorControll, text=repr(x),background=strBackground)
pitchShow = Label(master=frameMotorControll, text=repr(y),background=strBackground)
yawShow = Label(master=frameMotorControll, text=repr(z),background=strBackground)
#canvasRollShow = Canvas(master=frameMotorControll)
#canvasRollShow.create_text(text=repr(x))
#canvasRollShow.grid(row=3, column=0)
#--
#rollShow.grid(row=3, column=0)
pitchShow.grid(row=3, column=1)
yawShow.grid(row=3, column=2)
rollLab.grid(row=1, column=0)
pitchLab.grid(row=1, column=1)
yawLab.grid(row=1, column=2)
buttonPhiP.grid(row=0, column=0,padx=2)
buttonPhiM.grid(row=2, column=0,padx=2)
buttonTetaP.grid(row=0, column=1,padx=2)
buttonTetaM.grid(row=2, column=1,padx=2)
buttonPsiP.grid(row=0, column=2,padx=2)
buttonPsiM.grid(row=2, column=2,padx=2)



ani = animation.FuncAnimation(fig, UpdatePlotWidget, interval=1)
Tk.mainloop()