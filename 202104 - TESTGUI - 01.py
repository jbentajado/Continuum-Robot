import serial
import tkinter as tk

comPort = "COM9" 
ser = serial.Serial(comPort, baudrate = 115200, timeout = 0) #timeout is in seconds
serialString = "" #initilizes string for serial port

def run():
    Position1 = b'<' + b'1' + b'p' + DCMotorPosition1_Entry.get().encode() + b'>' # .encode() converts the char type into byte types
    Position2 = b'<' + b'2' + b'p' + DCMotorPosition2_Entry.get().encode() + b'>'
    x = Position1 + Position2
    ser.write(x)    
    print(x)

def ManualEntryMode_ON():
    ManualModeLabel.config(text = "Manual Entry ON", fg = 'green')
    MEM1 = b'<' + b'M' + b'M' + B'1' + b'>'
    ser.write(MEM1) 
    print(MEM1)
    x1 = ser.readline()
    print(x1)
    
def ManualEntryMode_OFF():
    ManualModeLabel.config(text = "Manual Entry OFF", fg = 'red')
    MEM0 = b'<' + b'M' + b'M' + B'0' + b'>'
    ser.write(MEM0) 
    print(MEM0)
    x2 = ser.readline()
    print(x2)

def JoystickMode_ON():
    JoystickModeLabel.config(text = "Joystick ON", fg = 'green')
    JSM1 = b'<' + b'J' + b'S' + b'M' + B'1' + b'>'
    ser.write(JSM1) 
    print(JSM1)
    x3 = ser.readline()
    print(x3)

def JoystickMode_OFF():
    JoystickModeLabel.config(text = "Joystick OFF", fg = 'red')
    JSM0 = b'<' + b'J' + b'S' + b'M' + B'0' + b'>'
    ser.write(JSM0) 
    print(JSM0)
    x4 = ser.readline()
    print(x4)

def JevoisMode_ON():
    JevoisModeLabel.config(text = "Jevois ON", fg = 'green')
    JM1 = b'<' + b'J' + b'M' + B'1' + b'>'
    ser.write(JM1) 
    print(JM1)
    x5 = ser.readline()
    print(x5)

def JevoisMode_OFF():
    JevoisModeLabel.config(text = "Jevois OFF", fg = 'red')
    JM0 = b'<' + b'J' + b'M' + B'0' + b'>'
    ser.write(JM0) 
    print(JM0)
    x6 = ser.readline()
    print(x6)

def PatternMode_ON():
    PatternModeLabel.config(text = "Pattern ON", fg = 'green')
    PM1 = b'<' + b'P' + b'M' + B'1' + b'>'
    ser.write(PM1) 
    print(PM1)
    x7 = ser.readline()
    print(x7)

def PatternMode_OFF():
    PatternModeLabel.config(text = "Pattern OFF", fg = 'red')
    PM0 = b'<' + b'P' + b'M' + B'0' + b'>'
    ser.write(PM0) 
    print(PM0)     
    x8 = ser.readline()
    print(x8)

#def updatelabel():
#    serialData = ser.readline()
#    StringDecode = serialData.decode('Ascii')
#    label1=tk.Label(root, text = StringDecode)
#    label1.grid(row=3,column=2)
#    root.after(20,updatelabel)

root = tk.Tk() #this starts and creates the GUI
#-------------------------------------------------------------- Size and Title of GUI --------------------------------------------------------
root.geometry("1000x500")
root.title('Continuum Robot GUI')
run_button = tk.Button(root, text ="run", command=run, font = 'sans 16 bold')
run_button.grid(row=0, column=0) 
#root.bind("<Return>", run) #this allows you to just press enter to execute the "run"

DCMotorPosition1 = tk.Label(root, text = "Position 1 (Pulses): " , bd = 2)
DCMotorPosition1.grid(row=0,column=5)

DCMotorPosition1_Entry = tk.Entry(root, bd=1)
DCMotorPosition1_Entry.grid(row=0,column=6)

DCMotorPosition2 = tk.Label(root, text = "Position 2 (Pulses): " , bd = 2)
DCMotorPosition2.grid(row=1,column=5)

DCMotorPosition2_Entry = tk.Entry(root, bd=1)
DCMotorPosition2_Entry.grid(row=1,column=6)

#--------------------------------------------- MANUAL ENTRY -------------------------------------------------------
ManualModeButton_ON = tk.Button(root, text ="Manual Entry ON", command=ManualEntryMode_ON, font = 'sans 16 bold')
ManualModeButton_ON.grid(row=1, column=0)

ManualModeButton_OFF = tk.Button(root, text ="Manual Entry OFF", command=ManualEntryMode_OFF, font = 'sans 16 bold')
ManualModeButton_OFF.grid(row=1, column=1) 

ManualModeLabel = tk.Label(root, text = "Manual OFF", font = 'sans 16 bold', fg = 'red')
ManualModeLabel.grid(row=1, column=2) 
#--------------------------------------------- JOYSTICK -------------------------------------------------------
JoystickModeButton_ON = tk.Button(root, text ="Joystick ON", command=JoystickMode_ON, font = 'sans 16 bold')
JoystickModeButton_ON.grid(row=2, column=0)

JoystickModeButton_OFF = tk.Button(root, text = "Joystick OFF", command=JoystickMode_OFF, font = 'sans 16 bold')
JoystickModeButton_OFF.grid(row=2, column=1)

JoystickModeLabel = tk.Label(root, text = "Joystick OFF", font = 'sans 16 bold', fg = 'red')
JoystickModeLabel.grid(row=2, column=2) 
#--------------------------------------------- JEVOIS -------------------------------------------------------
JevoisModeButton_ON = tk.Button(root, text ="JEVOIS ON", command=JevoisMode_ON, font = 'sans 16 bold')
JevoisModeButton_ON.grid(row=3, column=0)

JevoisModeButton_OFF = tk.Button(root, text ="JEVOIS OFF", command=JevoisMode_OFF, font = 'sans 16 bold')
JevoisModeButton_OFF.grid(row=3, column=1)

JevoisModeLabel = tk.Label(root, text = "JEVOIS OFF", font = 'sans 16 bold', fg = 'red')
JevoisModeLabel.grid(row=3, column=2) 
#--------------------------------------------- PATTERN -------------------------------------------------------
PatternModeButton_ON = tk.Button(root, text ="Pattern ON", command=PatternMode_ON, font = 'sans 16 bold')
PatternModeButton_ON.grid(row=4, column=0)

PatternModeButton_OFF = tk.Button(root, text ="Pattern OFF", command=PatternMode_OFF, font = 'sans 16 bold')
PatternModeButton_OFF.grid(row=4, column=1)

PatternModeLabel = tk.Label(root, text = "Pattern OFF", font = 'sans 16 bold', fg = 'red')
PatternModeLabel.grid(row=4, column=2) 

root.mainloop() #This ends the GUI