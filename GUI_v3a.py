# GUI_v3a.py
'''
changes made:
- calculate pitch and roll
    source: https://roboticsclubiitk.github.io/2017/12/21/Beginners-Guide-to-IMU.html
- add complimentary filter
- add tabs
'''

import time
import smbus
import serial
import board
 
from tkinter import *
from tkinter import ttk
from math import *
import tkinter as tk
import tkinter.font
import tkinter.messagebox as MessageBox
import RPi.GPIO # for cleanup
RPi.GPIO.setmode(RPi.GPIO.BCM)

from adafruit_mpu6050 import MPU6050

import mpu6050_complimentary_filter
from mpu6050_complimentary_filter import getRawData

radToDeg = 180/pi

newx_position = 0 
newy_position = 0   
 
### HARDWARE ### 
# I2C - IMU
# mpu6050 = MPU6050(board.I2C())           # base accel & gyro sensor

# Setup
bus = smbus.SMBus(1)
address = 0x68

# From setUp()
accHex = 0
gyroHex = 0

accScaleFactor = 16384.0
gyroScaleFactor = 131.0

# activate the mpu6050
bus.write_byte_data(address, 0x6B, 0x00)

# configure the accelerometer
bus.write_byte_data(address, 0x1C, accHex)

# configure the gyroscope
bus.write_byte_data(address, 0x1B, gyroHex)

# From gyroscope calibration - offsets
gyroXcal = -322.1
gyroYcal = -354.6
gyroZcal = -223.3

dtTimer = 0
gyroRoll = 0
gyroPitch = 0
gyroYaw = 0

roll = 0
pitch = 0
yaw = 0
# Serial - Jevois
# jevois_baudrate = 115200
# com_port1 = '/dev/serial0'
# ser1 = serial.Serial(port = com_port1, baudrate = jevois_baudrate,
#                      parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
#                      bytesize=serial.EIGHTBITS, timeout=1)

# Serial - Arduino
# arduino_baudrate = 115200 
# com_port2 = '/dev/ttyACM0'    # under the wifi usb
# ser2 = serial.Serial(port = com_port2, baudrate = arduino_baudrate, timeout = 0)    # my port = '/dev/ttyACM0'

### GUI DEFINITIONS ###
HEIGHT = 500   # pixels
WIDTH = 1300

root = Tk()                                      # create Tkinter root
root.title("Continuum Robot GUI")

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack

my_notebook = ttk.Notebook(root)
my_notebook.pack(pady = 0)
BG = '#222222'
LABEL_BG = '#ffefdb'
LITE_BG = '#829AB1'
WITE_BG = '#F0F4F8'
DARK_BG = '#334E68'

lite_widget_font = tkinter.font.Font(family='Helvetica', size=12,
                                     weight="bold")
dark_widget_font = tkinter.font.Font(family = 'Helvetica', size = 12,
                                     weight = "bold")

# define what is inside the tabs using frames
mode_selection_tab = Frame(my_notebook, bd=10,
                             width=WIDTH, height=HEIGHT, 
                             bg=BG)
manual_tab = Frame(my_notebook, bd=10,
                          width=WIDTH, height=HEIGHT, 
                          bg=BG)
object_tracing_tab = Frame(my_notebook, bd=10,
                                  width=WIDTH, height=HEIGHT,
                                  bg=BG)
pattern_tab = Frame(my_notebook, bd=10,
                           width=WIDTH, height=HEIGHT,
                           bg=BG)

mode_selection_tab.pack(fill='both', expand=1)
manual_tab.pack(fill='both', expand=1)
object_tracing_tab.pack(fill='both', expand=1)
pattern_tab.pack(fill='both', expand=1)

# designate the tabs
my_notebook.add(mode_selection_tab, text = 'Mode Selection')
my_notebook.add(manual_tab, text = 'Manual Mode')
my_notebook.add(object_tracing_tab, text = 'Object Tracing Mode')
my_notebook.add(pattern_tab, text = 'Pattern Mode')

# hide the different modes
my_notebook.hide(1)
my_notebook.hide(2)
my_notebook.hide(3)

### EVENT FUNCTIONS ###
running = True # global flag

def close_window():
    root.destroy()

def send_to_jevois_program(cmd):
    """Send commands to the Jevois program to control the camera

    Args:
        cmd ([string]): the command to be sent to the jevois program terminal
    """
    # print(cmd)
    ser1.write((cmd + '\n').encode())
    time.sleep(1)
    print('Message was sent to Jevois!')
  
def manual_move_motorse(motor1, motor2):
    move_motor1 = b'<' + b'1' + b'p' + motor1.get().encode() + b'>'
    move_motor2 = b'<' + b'2' + b'p' + motor2.get().encode() + b'>'
    print('move to position 1:', move_motor1)
    print('move to position 2:', move_motor2)
    
    # serialread2 = ser2.readline()
    # print(serialread2)
    
    # ser2.write(x_to_arduino + y_to_arduino)

def trace_trace_move_motors(x, y):
    global newx_position, newy_position
    
    x_to_arduino = b'<' + b'J' + b'x' + str(x).encode() + b'>'
    y_to_arduino = b'<' + b'J' + b'y' + str(y).encode() + b'>'
    print('move to position 1:', x_to_arduino)
    print('move to position 2:', y_to_arduino)
    
    serialread2 = ser2.readline()
    print(serialread2)
    
    ser2.write(x_to_arduino + y_to_arduino)

def set_arduino_mode(trigger):
    send_char = trigger
    print(send_char)
    # ser2.write(send_char)
        
def eightBit2sixteenBit(reg):
        # Reads high and low 8 bit values and shifts them into 16 bit
        h = bus.read_byte_data(address, reg)
        l = bus.read_byte_data(address, reg+1)
        val = (h << 8) + l

        # Make 16 bit unsigned value to signed value (0 to 65535) to (-32768 to +32767)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val


def show_tab(mode_frame, mode_selection, mode):
    my_notebook.add(mode_frame, text = mode_selection)
    set_arduino_mode(mode)
    my_notebook.tab(0, state='disabled')
    
def close_tab(i_tab, mode):
    my_notebook.hide(i_tab)
    set_arduino_mode(mode)
    
    my_notebook.tab(0, state='normal')
    my_notebook.select(0)

def blink():
    y = b'<'+ b'B'+ b'>'
    ser2.write(y)

def run():
    global gyroRoll, gyroPitch, gyroYaw, roll, pitch, yaw
    if running:
        mpu.getRawData
        print(gx)
        ## IMU READINGS ##
        round_to_decimal = 2

        dtTimer = 0
        dt = time.time() - dtTimer
        dtTimer = time.time()
        
        # get_raw_data()
        # # read the accelerometer and gyroscope
        # read_accel = mpu6050.acceleration    # reads accel, tuple
        # read_gyro = mpu6050.gyro             # reads gyro, tuple

        # # unpack the accel/gyro tuples
        # ax, ay, az = read_accel       # unpacks tuple
        # gx, gy, gz = read_gyro           
        
        # ax = round(ax, round_to_decimal)                   # rounds float to 2 decimal places
        # ay = round(ay, round_to_decimal)
        # az = round(az, round_to_decimal)
        
        # gx = round(gx, round_to_decimal)
        # gy = round(gy, round_to_decimal)
        # gz = round(gyroZ, round_to_decimal)
        
        # # calculate roll and pitch
        # imu_pitch = atan2(ay, az)*radToDeg     # about IMU x axis, equivalent to arm's roll
        # imu_roll = atan2(ax, az)*radToDeg      # about IMU y axis, equivalent to arm's pitch
        
        ##### COPY FROM FILTER
        # Process IMU values #
        # Get Raw Data
        gx = eightBit2sixteenBit(0x43)
        gy = eightBit2sixteenBit(0x45)
        gz = eightBit2sixteenBit(0x47)
        
        print("Get Raw Data")
        print("\tgx: " + str(round(gx,1)))
        print("\tgy: " + str(round(gy,1)))
        print("\tgz: " + str(round(gz,1)))
        
        ax = eightBit2sixteenBit(0x3B)
        ay = eightBit2sixteenBit(0x3D)
        az = eightBit2sixteenBit(0x3F)
        
        # print("Get Raw Data")
        # print("\tgx: " + str(round(gx,1)))
        # print("\tgy: " + str(round(gy,1)))
        # print("\tgz: " + str(round(gz,1)) + "\n")
        
        # print("\tax: " + str(round(ax,1)))
        # print("\tay: " + str(round(ay,1)))
        # print("\taz: " + str(round(az,1)))
        
        # Subtract the offset calibration values
        gx -= gyroXcal
        gy -= gyroYcal
        gz -= gyroZcal
        
        # Convert to instantaneous degrees per second
        gx /= gyroScaleFactor
        gy /= gyroScaleFactor
        gz /= gyroScaleFactor
        
        
        # print("Get Raw Data")
        # print("\tgx: " + str(round(gx,1)))
        # print("\tgy: " + str(round(gy,1)))
        # print("\tgz: " + str(round(gz,1)))
        # Convert to g force
        ax /= accScaleFactor
        ay /= accScaleFactor
        az /= accScaleFactor
        
        # Complementary filter #
        # Get delta time and record time for next call
        dt = time.time() - dtTimer
        dtTimer = time.time()
        
        # Acceleration vector angle
        accPitch = degrees(atan2(ay, az))
        accRoll = degrees(atan2(ax, az))

        # Gyro integration angle
        gyroRoll -= gy * dt
        gyroPitch += gx * dt
        gyroYaw += gz * dt
        yaw = gyroYaw
        
        # print("Get Raw Data")
        # print("\tgyroRoll: " + str(round(gx,1)))
        # print("\tgyroPitch: " + str(round(gy,1)))
        # print("\tgyroYaw: " + str(round(gz,1)))

        # Comp filter
        tau = 0.98
        roll = (tau)*(roll - gy*dt) + (1-tau)*(accRoll)
        pitch = (tau)*(pitch + gx*dt) + (1-tau)*(accPitch)

        # Print data
        print("accPitch: " + str(accPitch))
        print("accRoll: " +str(accRoll))
        
        print("gyroRoll: " + str(gyroRoll))
        print("gyroPitch: " + str(gyroPitch))
        
        print(" R: " + str(round(roll,1)) \
            + " P: " + str(round(pitch,1)) \
            + " Y: " + str(round(yaw,1)))
        
        ## END COPY FROM FILTER
        
        # complementary filter (about IMU axes)
        # alpha = 0.9
        # comp_filter_roll = 0
        # comp_filter_pitch = 0
        
        # comp_filter_roll =  alpha*(comp_filter_roll + gy*dt) + (1-alpha)*(imu_roll)
        # comp_filter_pitch = alpha*(comp_filter_pitch + gx*dt) + (1-alpha)*(imu_pitch)

        # # string format accel/gyro readings
        # accel_string = "Acceleration: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2".format(*read_accel)
        # gyro_string = "Angular Velocity: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} degrees/s".format(*read_gyro)

        # # string format roll/pitch readings
        # imu_roll_string = str(imu_roll)
        # imu_pitch_string = str(imu_pitch)

        # print('Roll: ', str(imu_roll))
        # print('Pitch: ', str(imu_pitch))
        # print(accel_string)

        # pitch_text.set(imu_roll_string)
        # roll_text.set(imu_pitch_string)

        time.sleep(0.5)
                
    if not running:
        print("this is not running")
        buttercup_text.set("buttercup IMU readings unavailable")
        bubbles_text.set("Bubbles IMU readings unavailable")
 
    # after 1 s, call scanning again,  1/2 s = 500
    root.after(1, run)

    
### WIDGETS ###

# GLOBAL MODE TAB WIDGET SIZING #
title_rel_height = 0.08
title_rel_width = 0.95
close_tab_relx = 0.98
close_rel_height = 0.05
close_rel_width = 0.02
tab_title_rely = 0.05

#---# MODE SELECTION TAB #---#

# DIMENSIONS
mode_sel_rely = 0.2
mode_sel_relheight = 0.1
mode_sel_relwidth = 0.2

# WIDGETS
select_mode_label = Label(mode_selection_tab, text='Select Control Mode:', 
                          font=dark_widget_font, bg=DARK_BG,
                          fg=WITE_BG)
select_mode_label.place(relx=0.5, rely=tab_title_rely,
                        relheight=title_rel_height, relwidth=title_rel_width,
                        anchor='n')

# A = manual mode
manual_on = b'<' + b'M' + b'M' + b'1' + b'>'
manual_off = b'<' + b'M' + b'M' + b'0' + b'>'
manual_button = Button(mode_selection_tab, text='Manual Mode',
                       font=lite_widget_font, bg=DARK_BG, fg=WITE_BG,
                       command = lambda: show_tab(manual_tab, 'Manual Mode', manual_on))
manual_button.place(relx=0.15, rely=mode_sel_rely,
                    relheight=mode_sel_relheight, relwidth=mode_sel_relwidth)

# B = object tracing mode
object_tracing_on = b'<' + b'O' + b'T' + b'1' + b'>'
object_tracing_off = b'<' + b'O' + b'T' + b'1' + b'>'
object_trace_button = Button(mode_selection_tab, text = 'Object Tracing Mode',
                             font = lite_widget_font, bg=DARK_BG, fg=WITE_BG,
                             command = lambda: show_tab(object_tracing_tab, 'Object Tracing Mode', object_tracing_on))
object_trace_button.place(relx = 0.4, rely = mode_sel_rely,
                          relheight = mode_sel_relheight, relwidth = mode_sel_relwidth)

# C = pattern mode
pattern_on = b'<' + b'P' + b'M' + b'1' + b'>'
pattern_off = b'<' + b'P' + b'M' + b'0' + b'>'
pattern_button = Button(mode_selection_tab, text = 'Pattern Mode',
                        font = lite_widget_font, bg=DARK_BG, fg=WITE_BG,
                        command = lambda: show_tab(pattern_tab, 'Pattern Mode', pattern_on))
pattern_button.place(relx = 0.65, rely = mode_sel_rely,
                     relheight = mode_sel_relheight, relwidth = mode_sel_relwidth)

manual_description_text = 'Manual Mode: Control the continuum robot manually by inputting the amount of pulses for the motors to move.'
object_description_text = 'Object Tracing Mode: <add description later>.'
pattern_description_text = 'Pattern Tracing Mode: <add description later>.'

mode_descriptions_text = ('{:<} \n \n {:<} \n \n {:<}'.format(manual_description_text, object_description_text, pattern_description_text))

mode_descriptions = Label(mode_selection_tab, text=mode_descriptions_text,
                          font=lite_widget_font, bg=LITE_BG, fg=WITE_BG,
                          anchor='w', justify=LEFT,
                          wraplength=760)
mode_descriptions.place(relx=0.5, rely=0.35,
                        relheight=0.3, relwidth=title_rel_width,
                        anchor='n')

exit_gui_button = tk.Button(mode_selection_tab, text="Exit GUI", 
                            bg=DARK_BG, fg=WITE_BG,
                            command=close_window)
exit_gui_button.place(rely=0.9,
                      relheight=0.1, relwidth=0.2)

#---# MANUAL MODE TAB #---#
manual_title = Label(manual_tab, text = 'Manual Mode',
                          font = lite_widget_font, bg=DARK_BG, fg=WITE_BG)
manual_title.place(relx = 0.5, rely = tab_title_rely,
                   relheight = title_rel_height, relwidth = title_rel_width,
                   anchor = 'n')
close_manual_tab = Button(manual_tab, text = 'X',
                      fg = 'white', bg = 'red',
                      font = lite_widget_font,
                      command = lambda: close_tab(1, manual_off))
close_manual_tab.place(relx = close_tab_relx, #rely = close_tab_rely,
                   relheight = close_rel_height, relwidth = close_rel_width)
exit_gui_from_manual = tk.Button(manual_tab, text = "Exit GUI", 
                                 bg=DARK_BG, fg=WITE_BG,
                                 command = close_window)
exit_gui_from_manual.place(relx = 0.02, rely = 0.88,
                      relheight = 0.1, relwidth = 0.2)

'''
legend:
    x = relx
    y = rely
    w = width
    h = height
'''

# category labels (position, analog control, imu)

w_category = 0.2
w_position_category = 0.3
w_imu_category = 0.25
h_category = 0.05
y_category = 0.2

x_position_category = 0.025
x_joystick_category = 0.5
x_imu_category = 0.675

position_label = Label(manual_tab, text='Position Input Motion Control​', 
                       font=lite_widget_font, bg=DARK_BG, fg=WITE_BG)
position_label.place(relx=x_position_category, rely=y_category, 
                     relwidth=w_position_category, relheight=h_category)

joystick_label = Label(manual_tab, text='Joystick Toggle​', 
                       font=lite_widget_font, bg=DARK_BG, fg=WITE_BG)
joystick_label.place(relx=x_joystick_category, rely=y_category, 
                     relwidth=w_category, relheight=h_category,
                     anchor='n')

imu_label = Label(manual_tab, text='IMU Readings', 
                       font=lite_widget_font, bg=DARK_BG, fg=WITE_BG)
imu_label.place(relx=x_imu_category, rely=y_category, 
                relwidth=w_position_category, relheight=h_category)

# separators #
s = ttk.Style()
s.configure('white.TSeparator', background = 'white')

w_separator = 0.001
h_separator = 0.5
y_separator = 0.2

x_separator1 = 0.363
x_separator2 = 0.636

separator1 = ttk.Separator(manual_tab, orient = 'vertical',
                           style = 'white.TSeparator')
separator1.place(relx = x_separator1, rely = y_separator, 
                 relwidth = w_separator, relheight = h_separator)

separator2 = ttk.Separator(manual_tab, orient = 'vertical',
                           style = 'white.TSeparator')
separator2.place(relx = x_separator2, rely = y_separator, 
                 relwidth = w_separator, relheight = h_separator)

# position labels (target1, current1, target2, current2)
w_position = 0.15
h_position = 0.05
x_position = 0.025

y_target1 = 0.3
y_encoder1 = y_target1 + 0.1
y_target2 = y_target1 + 0.2
y_encoder2 = y_target1 + 0.3

target1 = Label(manual_tab, text='Target Position 1:', 
                font=lite_widget_font, bg=LITE_BG, fg=WITE_BG)
target1.place(relx=x_position, rely=y_target1, 
              relwidth=w_position, relheight=h_position)

current_position1 = Label(manual_tab, text='Current Position 1:', 
                          font=lite_widget_font, bg=LITE_BG, fg=WITE_BG)
current_position1.place(relx=x_position, rely=y_encoder1,
                        relwidth=w_position, relheight=h_position)

A_target2 = Label(manual_tab, text='Target Position 2:', 
                  font=lite_widget_font, bg=LITE_BG, fg=WITE_BG)
A_target2.place(relx=x_position, rely=y_target2, 
                relwidth=w_position, relheight=h_position)

current_position2 = Label(manual_tab, text='Current Position 2:', 
                          font=lite_widget_font, bg=LITE_BG, fg=WITE_BG)
current_position2.place(relx=x_position, rely=y_encoder2,
                               relwidth=w_position, relheight=h_position)

# position entries (target1, curren1, target 2, current 2)
w_position_in = 0.125
h_position_in = 0.05
x_position_in = 0.2

# motor 1
position1 = StringVar()
position1.set('')
enter_position1 = Entry(manual_tab, bg=LITE_BG, fg=WITE_BG,
                        textvariable = position1)
enter_position1.place(relx=x_position_in, rely=y_target1,
                      relwidth=w_position_in, relheight=h_position_in)

encoder1_label = tk.Label(manual_tab, font=lite_widget_font, 
                          bg=LITE_BG, fg=WITE_BG)
encoder1_label.place(relx=x_position_in, rely=y_encoder1, 
                     relwidth=w_position_in, relheight=h_position_in)

# motor 2
position2 = StringVar()
position2.set('')
enter_position2 = Entry(manual_tab, bg=LITE_BG, fg=WITE_BG,
                        textvariable = position2)
enter_position2.place(relx=x_position_in, rely=y_target2,
                            relwidth=w_position_in, relheight=h_position_in)

encoder2_label = tk.Label(manual_tab, font=lite_widget_font,
                          bg=LITE_BG, fg=WITE_BG)
encoder2_label.place(relx=x_position_in, rely=y_encoder2, 
                     relwidth=w_position_in, relheight=h_position_in)

# send user input to the arduino
x_run = 0.125
y_run = 0.7
w_run = 0.08
h_run = 0.1

run_button = Button(manual_tab, text='Run',
                    font=lite_widget_font, bg='#b3ffb3', fg='black',
                    command=lambda: manual_move_motorse(position1, position2))
                    #   command = lambda: send_to_jevois_program('obstacle'))
run_button.place (relx=x_run, rely=y_run, 
                  relwidth=w_run, relheight=h_run)

# joystick, on/off
x_joystick = 0.5
w_joystick = 0.08
h_joystick = 0.1

y_on = 0.3
y_off = y_on + 0.15

joystick_on = b'<' + b'J' + b'S' + b'1' + b'>'
joystick_off = b'<' + b'J' + b'S' + b'0' + b'>'

on_button = Button(manual_tab, text='On',
                    bg=LITE_BG, font=lite_widget_font,
                    command = lambda: set_arduino_mode(joystick_on))
on_button.place (relx=x_joystick, rely=y_on, 
                 relwidth=w_joystick, relheight=h_joystick,
                 anchor = 'n')
off_button = Button(manual_tab, text='Off',
                    bg=DARK_BG, font=dark_widget_font,
                    command = lambda: set_arduino_mode(joystick_off))
off_button.place (relx=x_joystick, rely=y_off, 
                  relwidth=w_joystick, relheight=h_joystick,
                  anchor = 'n')

# imu axis labels
Aw_axis = 0.07
Ah_position = 0.05
Ax_axis = 0.675

# the arm's pitch is about the IMU's y axis
# the arm's roll is about the IMU's x axis
roll_label = Label(manual_tab, text = 'roll:​', 
                    font = lite_widget_font, bg=LITE_BG, fg=WITE_BG)
roll_label.place(relx = Ax_axis, rely = y_target1, 
                  relwidth = Aw_axis, relheight = Ah_position)

pitch_label = Label(manual_tab, text = 'pitch:​', 
                   font = lite_widget_font, bg=LITE_BG, fg=WITE_BG)
pitch_label.place(relx = Ax_axis, rely = y_encoder1, 
                 relwidth = Aw_axis, relheight = Ah_position)

# imu axis readings
Aw_read_axis = 0.205
Ah_read_axis = Ah_position
Ax_read_axis = 0.77

pitch_text = StringVar()
pitch_text.set('Pitch Reading')
pitch_output = Label(manual_tab, textvariable=pitch_text,
                     bg=LITE_BG, fg=WITE_BG)
pitch_output.place(relx=Ax_read_axis, rely=y_encoder1,
                   relwidth=Aw_read_axis, relheight=Ah_position)

roll_text = StringVar()
roll_text.set('Roll Data')
roll_output = Label(manual_tab, textvariable=roll_text,
                    bg=LITE_BG, fg=WITE_BG)
roll_output.place(relx=Ax_read_axis, rely=y_target1,
                   relwidth=Aw_read_axis, relheight=Ah_position)

#---# OBJECT TRACKING TAB #---#
object_title = Label(object_tracing_tab, text='Object Tracing Mode',
                     font=lite_widget_font, bg=DARK_BG, fg=WITE_BG)
object_title.place(relx=0.5, rely=tab_title_rely,
                   relheight=title_rel_height, relwidth=title_rel_width,
                   anchor='n')
close_object_tab = Button(object_tracing_tab, text = 'X',
                      fg='white', bg='red',
                      font=lite_widget_font,
                      command=lambda: close_tab(2, object_tracing_off))
close_object_tab.place(relx=close_tab_relx, #rely = close_tab_rely,
                   relheight=close_rel_height, relwidth=close_rel_width)

exit_gui_from_object = tk.Button(object_tracing_tab, text="Exit GUI", 
                                 bg=DARK_BG, fg=WITE_BG,
                                 command=close_window)
exit_gui_from_object.place(relx=0.02, rely=0.88,
                      relheight=0.1, relwidth=0.2)

# selection labels
x_category = 0.125
y_mode = 0.2
y_color = y_mode + 0.175

h_jevois = 0.1
w_jevois = 0.15

mode_label = tk.Label(object_tracing_tab, 
                      text='select mode:', font=lite_widget_font, 
                      bg=DARK_BG, fg=WITE_BG)
mode_label.place(relx=x_category, rely=y_mode, 
                 relheight=h_jevois, relwidth=w_jevois)

color_label = tk.Label(object_tracing_tab, 
                       text='select color:', font=lite_widget_font, 
                       bg=DARK_BG, fg=WITE_BG)
color_label.place(relx=x_category, rely=y_color, 
                  relheight=h_jevois, relwidth=w_jevois)\
                      
# mode selection buttons
mode_space = 0.2
x_red_calibration = x_category + mode_space
x_green_obstacle = x_red_calibration + mode_space
x_blue_target = x_green_obstacle + mode_space

calibration_button = Button(object_tracing_tab, text='calibration', font=lite_widget_font,
                            command=lambda: send_to_jevois_program('calibration'))
calibration_button.place(relx = x_red_calibration, rely=y_mode, 
                         relheight=h_jevois, relwidth=w_jevois)

obstacle_button = Button(object_tracing_tab, text='obstacle', font=lite_widget_font,
                         command=lambda: send_to_jevois_program('obstacle'))
obstacle_button.place(relx=x_green_obstacle, rely=y_mode, 
                      relheight=h_jevois, relwidth=w_jevois)

target_button = Button(object_tracing_tab, text='target', font=lite_widget_font,
                       command=lambda: send_to_jevois_program('target'))
target_button.place(relx=x_blue_target, rely=y_mode, 
                    relheight=h_jevois, relwidth=w_jevois)         

# color selection buttons
red_button = Button(object_tracing_tab, text='red', font=lite_widget_font, 
                    activebackground='red',
                    command=lambda: send_to_jevois_program('red'))
red_button.place(relx=x_red_calibration, rely=y_color, 
                 relheight=h_jevois, relwidth=w_jevois)

green_button = Button(object_tracing_tab, text='green', font=lite_widget_font, 
                      activebackground='green',
                      command=lambda: send_to_jevois_program('green'))
green_button.place(relx=x_green_obstacle, rely=y_color, 
                   relheight=h_jevois, relwidth=w_jevois)

blue_button = Button(object_tracing_tab, text='blue', font=lite_widget_font, 
                     activebackground='blue',
                     command=lambda: send_to_jevois_program('blue'))
blue_button.place(relx=x_blue_target, rely=y_color, 
                  relheight=h_jevois, relwidth=w_jevois)

#---# PATTERN TAB #---#
pattern_title = Label(pattern_tab, text='Pattern Mode',
                     font=lite_widget_font, bg=DARK_BG, fg=WITE_BG)
pattern_title.place(relx=0.5, rely=tab_title_rely, 
                    relheight=title_rel_height, relwidth=title_rel_width,
                    anchor='n')

close_pattern_tab = Button(pattern_tab, text='X',
                           fg = 'white', bg = 'red',
                           font=lite_widget_font,
                           command=lambda: close_tab(3, pattern_off))
close_pattern_tab.place(relx=close_tab_relx,
                   relheight=close_rel_height, relwidth=close_rel_width)

exit_gui_from_pattern = tk.Button(pattern_tab, text="Exit GUI", 
                                  bg=DARK_BG, fg=WITE_BG,
                                  command=close_window)
exit_gui_from_pattern.place(relx=0.02, rely=0.88,
                            relheight=0.1, relwidth=0.2)

# pattern selection
pattern_space = 0.2

x_pattern = 0.225
x_circle = x_pattern + pattern_space
x_square = x_circle + pattern_space

on_off_space = 0.15
y_on = 0.2
y_off = y_on + on_off_space

circle_on = b'<' + b'C' + b'P' + b'1' + b'>'
circle_off = b'<' + b'C' + b'P' + b'0' + b'>'
square_on = b'<' + b'S' + b'P' + b'1' + b'>'
square_off = b'<' + b'S' + b'P' + b'0' + b'>'


select_pattern = Label(pattern_tab, text='select pattern:', 
                       font=dark_widget_font, 
                       bg=DARK_BG, fg=WITE_BG)
select_pattern.place(relx=x_pattern, rely=y_on,
                     relheight=h_jevois, relwidth=w_jevois)

circle_mode_on = Button(pattern_tab, text='circle on', 
                        font=lite_widget_font, bg=LITE_BG,
                        command=lambda: set_arduino_mode(circle_on))
circle_mode_on.place(relx=x_circle, rely=y_on, 
                     relheight=h_jevois, relwidth=w_jevois)

circle_mode_off = Button(pattern_tab, text='circle off', font=lite_widget_font, 
                         bg=DARK_BG, fg=WITE_BG,
                         command=lambda: set_arduino_mode(circle_off))
circle_mode_off.place(relx=x_circle, rely=y_off, 
                      relheight=h_jevois, relwidth=w_jevois)

square_mode_on = Button(pattern_tab, text='square on', 
                        font=lite_widget_font, bg=LITE_BG,
                        command=lambda: set_arduino_mode(square_on))
square_mode_on.place(relx=x_square, rely=y_on, 
                     relheight=h_jevois, relwidth=w_jevois)

square_mode_off = Button(pattern_tab, text='square off', font=lite_widget_font, 
                         bg=DARK_BG, fg=WITE_BG,
                         command=lambda: set_arduino_mode(square_off))
square_mode_off.place(relx=x_square, rely=y_off, 
                      relheight=h_jevois, relwidth=w_jevois)

root.after(1000, run) # after 1 s, call run()
root.mainloop()
