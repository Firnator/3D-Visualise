'''
=========================
Version2.2
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
import sys #startet die tk umgebung
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
root = Tk.Tk()
#root.wm_title("3D-Controll")


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
    
def ReadSensor():
    if ser.is_open:
        try:
            s=ser.readline().decode().split(',')
        except IndexError:
            s=[0,0,0,0]
    else:
        s=[0,0,0,0]
    return s

tiltSave=[0,0,0,0]  
  
  
class Body:
    def __init__(self):
        Body.ParamTorus(self,10,2) #bei initialisierung wird im Konstruktor der Körper Parametrisiert
        self.speedfield=[0,0,0] #stores last phi,teta,psi for use in calculateSpeed()
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
        
    def updatePos(self):
        tilt=ReadSensor()
        try:
            phi=float(tilt[0])*np.pi/180
            teta=float(tilt[1])*np.pi/180
            psi=float(tilt[2])*np.pi/180
        except (ValueError,IndexError):
            return (0,0,0)
        drawRectangle(xspeed=calculateSpeed(listval=self.speedfield[0], val = phi), yspeed=calculateSpeed(listval=self.speedfield[1], val = teta), zspeed=calculateSpeed(listval=self.speedfield[2], val = psi))
        self.speedfield=[phi,teta,psi]
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

   
##Controll Funnktinonen      
def _ParamTorus():
    Body.ParamTorus(B1,10,2)    
def _ParamKegel():
    Body.ParamKegel(B1,10,10)
def _comC():
    ser.open()   
def _quit():
    root.quit()     # stop mainloop
    root.destroy()  # beugt einem Fatal Python Error vor: PyEval_RestoreThread: NULL tstate

        
fig=Figure(figsize=(4,4), dpi=100)     
plotBody = fig.add_subplot(111, projection='3d')    
#=========================================================================================================================
###----------------------###    
###     TKGui design     ###
###----------------------###
class Application(Frame):        
    def __init__(self,master=None):
        
        #startet die tk umgebung
        Frame.__init__(self, master)
        self.master.title("3D-Controll")    
        strBackground='white'
        ##erstellung Frames    
        self.mainFrameLeft=Frame(master)
        self.mainFrameRight=Frame(master)
        self.mainFrameCenter=Frame(master)    
        self.mainFrameLeft.pack(side=LEFT,padx=5, pady=5)
        self.mainFrameCenter.pack(side=LEFT,padx=5, pady=5)    
        self.mainFrameRight.pack(side=RIGHT,padx=5, pady=5)    
        self.mainFrameLeft.configure(background=strBackground)
        self.mainFrameRight.configure(background=strBackground)
        self.mainFrameCenter.configure(background=strBackground)
        buttonComC = Button(self.mainFrameCenter, text='Com Port Connect', command=_comC)
        buttonComC.pack(side=BOTTOM,anchor = 's')
        Application.centerFrame(self)
        Application.rightFrame(self)
        Application.leftFrame(self)
        
    def centerFrame(self):
        global fig
        #figure in canvas erzeugen 
        canvas = FigureCanvasTkAgg(fig, self.mainFrameCenter)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.TOP,anchor = 'center', fill=Tk.BOTH, expand=3)
        
    def rightFrame(self):
        global blub
        strBackground='white'
        framePlotSettings=Frame(self.mainFrameRight)
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
            but=Radiobutton(framePlotSettings,text=text,value=text,padx = 20, variable=auswahlParam, command=_settingParam,background=strBackground)
            but.pack(side=TOP,anchor = 'n')
        #button erzeugen---------------------------------------------------    
        buttonQuit = Button(framePlotSettings, text='Quit', command=_quit)
        buttonQuit.pack(side=BOTTOM,anchor = 'center')
        buttonComC = Button(framePlotSettings, text='Com Port Connect', command=_comC)
        buttonComC.pack(side=BOTTOM,anchor = 's')
        #Tz = Text(master=framePlotSettings, height=2, width=5)
        #Tz.insert(END,"-z->")
        #Tz.pack(side=BOTTOM)
        #MotorControllButton---------------------------------------------------------------------------
        frameMotorControll=Frame(self.mainFrameRight)
        frameMotorControll.pack(side=BOTTOM,anchor = 's',padx=30, pady=30)
        frameMotorControll.configure(background=strBackground)
        #--

        #x,y,z=Body.readSensor(B1)
        controllWidth=3
        buttonPhiP=Button(frameMotorControll, text='+', command=_quit,width=controllWidth)
        buttonPhiM=Button(frameMotorControll, text='-', command=_quit,width=controllWidth)
        buttonTetaP=Button(frameMotorControll, text='+', command=_quit,width=controllWidth)
        buttonTetaM=Button(frameMotorControll, text='-', command=_quit,width=controllWidth)
        buttonPsiP=Button(frameMotorControll, text='+', command=_quit,width=controllWidth)
        buttonPsiM=Button(frameMotorControll, text='-', command=_quit,width=controllWidth)
        rollLab = Label(frameMotorControll, text="\u03A6",background=strBackground)
        pitchLab = Label(frameMotorControll, text="\u0398",background=strBackground)
        yawLab = Label(frameMotorControll, text="\u03A8",background=strBackground)
        #rollShow = Label(master=frameMotorControll, text=,background=strBackground)
        #pitchShow = Label(master=frameMotorControll, text=repr(y),background=strBackground)
        #yawShow = Label(master=frameMotorControll, text=repr(z),background=strBackground)
        #print(tiltSave[0])
        #def showTilt():
        #tiltSave=[0,0,0,0]
        #canvasRollShow = Canvas(master=frameMotorControll)
        #iptext=canvasRollShow.create_text( 1,1,anchor="nw")
        #canvasRollShow.grid(row=3, column=0)
        #canvasRollShow.itemconfigure(iptext, text=str(tiltSave[0]))
        #frameMotorControll.after(1, showTilt)

        #--
        #rollShow.grid(row=3, column=0)
        #pitchShow.grid(row=3, column=1)
        #yawShow.grid(row=3, column=2)
        rollLab.grid(row=1, column=0)
        pitchLab.grid(row=1, column=1)
        yawLab.grid(row=1, column=2)
        buttonPhiP.grid(row=0, column=0,padx=2)
        buttonPhiM.grid(row=2, column=0,padx=2)
        buttonTetaP.grid(row=0, column=1,padx=2)
        buttonTetaM.grid(row=2, column=1,padx=2)
        buttonPsiP.grid(row=0, column=2,padx=2)
        buttonPsiM.grid(row=2, column=2,padx=2)
#?????app.leftFrame.sml
    def leftFrame(self):
        strBackground='white'
        leftLeftFrame = Frame(self.mainFrameLeft,background=strBackground)
        centerLeftFrame= Frame(self.mainFrameLeft,background=strBackground)
        rightLeftFrame = Frame(self.mainFrameLeft,background=strBackground)
        leftLeftFrame.pack(side=LEFT,padx=5, pady=5)
        centerLeftFrame.pack(side=LEFT,padx=5, pady=5)    
        rightLeftFrame.pack(side=RIGHT,padx=5, pady=5) 
        
        self.sml = Canvas(leftLeftFrame, width=50, height=200)
        self.smc = Canvas(centerLeftFrame, width=50, height=200) # Canvas for Speedometer
        self.smr = Canvas(rightLeftFrame, width=50, height=200)
        self.sml.pack(side='top')
        self.smc.pack(side='top')
        self.smr.pack(side='top')
        leftRollLab = Label(leftLeftFrame, text="\u03A6",background=strBackground)
        leftPitchLab = Label(centerLeftFrame, text="\u0398",background=strBackground)
        leftYawLab = Label(rightLeftFrame, text="\u03A8",background=strBackground)

        leftRollLab.pack(side='bottom')
        leftPitchLab.pack(side='bottom')
        leftYawLab.pack(side='bottom') 



def drawRectangle(xspeed,yspeed,zspeed):
    app.sml.delete('all')
    app.smc.delete('all')
    app.smr.delete('all')
    app.sml.create_rectangle(0,100,52,xspeed+100, fill='black')
    app.smc.create_rectangle(0,100,52,yspeed+100, fill='black')
    app.smr.create_rectangle(0,100,52,zspeed+100, fill='black')

def calculateSpeed(listval,val):
    aspeed=val - listval
    return aspeed*100
    
    
    
    
app = Application(master=root)    
#erzeugt ein element body
B1=Body()     
#change_text()
ani = animation.FuncAnimation(fig, UpdatePlotWidget, interval=1)
#ani = animation.FuncAnimation(fig, UpdatePlotWidget, interval=1)
app.mainloop()



