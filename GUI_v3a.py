# GUI_v3a.py
'''
changes made:
- add kalman filter this one is hard
- add tabs
'''

import time
import smbus
import math
# import matplotlib.pyplot as plt
import serial
import board
 
from tkinter import *
from tkinter import ttk
import tkinter as tk
import tkinter.font
import tkinter.messagebox as MessageBox
import RPi.GPIO # for cleanup
RPi.GPIO.setmode(RPi.GPIO.BCM)

from adafruit_mpu6050 import MPU6050

newx_position = 0 
newy_position = 0   
 
### HARDWARE ### 
# I2C - IMU
# blossom_mpu6050 = MPU6050(board.I2C())           # base accel & gyro sensor
# Power management registers - MPU6050
# power_mgmt_1 = 0x6b
# power_mgmt_2 = 0x6c
 
# gyro_scale = 131.0
# accel_scale = 16384.0
 
# address = 0x68  # This is the address value read via the i2cdetect command

# Serial - Jevois
# jevois_baudrate= 115200
# com_port1 = '/dev/serial0'
# ser1 = serial.Serial(port = com_port1, baudrate = jevois_baudrate,
#                     parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
#                     bytesize=serial.EIGHTBITS, timeout=1)

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

myFont = tkinter.font.Font(family = 'Helvetica',
                           size = 12,
                           weight = "bold")

# define what is inside the tabs using frames
mode_selection_tab = Frame(my_notebook, bd = 10,
                             width = WIDTH, height = HEIGHT, 
                             bg = '#80c1ff')
manual_tab = Frame(my_notebook, bd = 10,
                          width = WIDTH, height = HEIGHT, 
                          bg = '#80c1ff')
object_tracing_tab = Frame(my_notebook, bd = 10,
                                  width = WIDTH, height = HEIGHT,
                                  bg = '#80c1ff')
pattern_tab= Frame(my_notebook, bd = 10,
                           width = WIDTH, height = HEIGHT,
                           bg = '#80c1ff')

mode_selection_tab.pack(fill = 'both', expand = 1)
manual_tab.pack(fill = 'both', expand = 1)
object_tracing_tab.pack(fill = 'both', expand = 1)
pattern_tab.pack(fill = 'both', expand = 1)

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
  
def trace_trace_move_motors(x, y):
    global newx_position, newy_position
    
    x_to_arduino = b'<' + b'J' + b'x' + str(x).encode() + b'>'
    y_to_arduino = b'<' + b'J' + b'y' + str(y).encode() + b'>'
    print('move to position 1:', x_to_arduino)
    print('move to position 2:', y_to_arduino)
    
    serialread2 = ser2.readline()
    print(serialread2)
    
    ser2.write(x_to_arduino + y_to_arduino)

# def round_float(imu_reading):
#     round_to_decimal = 2
#     round_float.imu_reading = round(imu_reading, round_to_decimal)
#     # return imu_reading
#     # print("imu reading:", imu_reading)

def blink():
    y = b'<'+ b'B'+ b'>'
    ser2.write(y)

def run():
    if running:
        
        # blossom - base
        round_to_decimal = 2
        blossom_accel = blossom_mpu6050.acceleration    # reads blossom accel, tuple
        blossom_gyro = blossom_mpu6050.gyro             # reads blossom gyro, tuple
        accel_x, accel_y, accel_z = blossom_accel       # unpacks tuple
        gyro_x, gyro_y, gyro_z = blossom_gyro           
        
        accel_x = round(accel_x, round_to_decimal)                   # rounds float to 2 decimal places
        accel_y = round(accel_y, round_to_decimal)
        accel_z = round(accel_z, round_to_decimal)
        
        gyro_x = round(gyro_x, round_to_decimal)
        gyro_y = round(gyro_y, round_to_decimal)
        gyro_z = round(gyro_z, round_to_decimal)

        blossom_accel_string = "Acceleration: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2".format(*blossom_accel)
        blossom_gyro_string = "Amngular Velocity: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} rad.s".format(*blossom_gyro)
        blossom_Atext.set(blossom_accel_string)
        blossom_Gtext.set(blossom_gyro_string)

        time.sleep(0.5)
        
        # Jevois Reading
        ser1.flushInput()

        serialread = ser1.readline().rstrip().decode('utf8')
        data_list = serialread.split('x')
        list_check = str(data_list)
        no = "['']"
                
        if list_check != no:
            #using map() to turn string array into int array
            data_list = list(map(int, data_list))
            x = data_list[0]     # int
            y = data_list[1]     # int
                    
            print ('X coordinate: {} | Y coordinate: {}'.format(x,y))
            jevois_reading = 'X coordinate: {} | Y coordinate: {}'.format(x,y)
            jevois_text.set(jevois_reading)
            if x != 0:
                trace_move_motors(x, y)
                # blink()
                
    if not running:
        print("this is not running")
        buttercup_text.set("buttercup IMU readings unavailable")
        bubbles_text.set("Bubbles IMU readings unavailable")
 
    # after 1 s, call scanning again,  1/2 s = 500
    root.after(1, run)
    
def show_tab(mode_frame, mode_selection):
    my_notebook.add(mode_frame, text = mode_selection)
    
def close_tab(i_tab):
    my_notebook.hide(i_tab)
    
### WIDGETS ###

# GLOBAL MODE TAB WIDGET SIZING #
title_rel_height = 0.05
title_rel_width = 0.95
close_tab_relx = 0.98
# close_tab_rely = 0.9
close_rel_height = 0.05
close_rel_width = 0.02
tab_title_rely = 0.05

#---# MODE SELECTION TAB #---#

# DIMENSIONS
mode_sel_rely = 0.2
mode_sel_relheight = 0.1
mode_sel_relwidth = 0.2

# WIDGETS
select_mode_label = Label(mode_selection_tab, text = 'Select Control Mode:', 
                          font = myFont, bg = 'white')
select_mode_label.place(relx = 0.5, rely = tab_title_rely,
                        relheight = title_rel_height, relwidth = title_rel_width,
                        anchor = 'n')

# A = manual mode
manual_button = Button(mode_selection_tab, text = 'Manual Mode',
                       font = myFont, 
                       command = lambda: show_tab(manual_tab, 'Manual Mode'))
manual_button.place(relx = 0.15, rely = mode_sel_rely,
                    relheight = mode_sel_relheight, relwidth = mode_sel_relwidth)

# B = object tracing mode
object_trace_button = Button(mode_selection_tab, text = 'Object Tracing Mode',
                             font = myFont,
                             command = lambda: show_tab(object_tracing_tab, 'Object Tracing Mode'))
object_trace_button.place(relx = 0.4, rely = mode_sel_rely,
                          relheight = mode_sel_relheight, relwidth = mode_sel_relwidth)

# C = pattern mode
pattern_button = Button(mode_selection_tab, text = 'Pattern Mode',
                        font = myFont,
                        command = lambda: show_tab(pattern_tab, 'Pattern Mode'))
pattern_button.place(relx = 0.65, rely = mode_sel_rely,
                     relheight = mode_sel_relheight, relwidth = mode_sel_relwidth)

manual_description_text = 'Manual Mode: Control the continuum robot manually by inputting the amount of pulses for the motors to move.'
object_description_text = 'Object Tracing Mode: <add description later>.'
pattern_description_text = 'Pattern Tracing Mode: <add description later>.'

mode_descriptions_text = ('{:<} \n \n {:<} \n \n {:<}'.format(manual_description_text, object_description_text, pattern_description_text))

mode_descriptions = Label(mode_selection_tab, text = mode_descriptions_text,
                          font = myFont, bg = 'white',
                          anchor = 'w', justify = LEFT,
                          wraplength = 760)
mode_descriptions.place(relx = 0.5, rely = 0.35,
                        relheight = 0.3, relwidth = title_rel_width,
                        anchor = 'n')

exit_gui_button = tk.Button(mode_selection_tab, text = "Exit GUI", command = close_window)
exit_gui_button.place(rely = 0.9,
                      relheight = 0.1, relwidth = 0.2)

#---# A, MANUAL MODE TAB #---#
manual_title = Label(manual_tab, text = 'Manual Mode',
                          font = myFont, bg = 'white')
manual_title.place(relx = 0.5, rely = tab_title_rely,
                   relheight = title_rel_height, relwidth = title_rel_width,
                   anchor = 'n')
close_manual_tab = Button(manual_tab, text = 'X',
                      fg = 'white', bg = 'red',
                      font = myFont,
                      command = lambda: close_tab(1))
close_manual_tab.place(relx = close_tab_relx, #rely = close_tab_rely,
                   relheight = close_rel_height, relwidth = close_rel_width)
exit_gui_from_manual = tk.Button(manual_tab, text = "Exit GUI", command = close_window)
exit_gui_from_manual.place(relx = 0.02, rely = 0.88,
                      relheight = 0.1, relwidth = 0.2)

# A - control dimensions #
'''
legend:
    x = relx
    y = rely
    w = width
    h = height
    A = motor control tab
'''

# category labels (position, analog control, imu)

Aw_category = 0.2
Aw_position_category = 0.3
Aw_imu_category = 0.25
Ah_category = 0.05
Ay_category = 0.2

Ax_position_category = 0.025
Ax_analog_category = 0.49
Ax_imu_category = 0.72

Aposition_label = Label(manual_tab, text = 'Position Input Motion Control​', 
                       font = myFont)
Aposition_label.place(relx = Ax_position_category, rely = Ay_category, 
                     relwidth = Aw_position_category, relheight = Ah_category)
Aanalog_label = Label(manual_tab, text = 'Analog Control​', 
                       font = myFont)
Aanalog_label.place(relx = Ax_analog_category, rely = Ay_category, 
                     relwidth = Aw_category, relheight = Ah_category)
Aimu_label = Label(manual_tab, text = 'IMU Readings', 
                       font = myFont)
Aimu_label.place(relx = Ax_imu_category, rely = Ay_category, 
                     relwidth = Aw_imu_category, relheight = Ah_category)

# separators #
s = ttk.Style()
s.configure('white.TSeparator', background = 'white')

Aw_separator = 0.001
Ah_separator = 0.5
Ay_separator = 0.2

Ax_separator1 = 0.34
Ax_separator2 = 0.475
Ax_separator3 = 0.705


separator1 = ttk.Separator(manual_tab, orient = 'vertical',
                           style = 'white.TSeparator')
separator1.place(relx = Ax_separator1, rely = Ay_separator, 
                 relwidth = Aw_separator, relheight = Ah_separator)

separator2 = ttk.Separator(manual_tab, orient = 'vertical',
                           style = 'white.TSeparator')
separator2.place(relx = Ax_separator2, rely = Ay_separator, 
                 relwidth = Aw_separator, relheight = Ah_separator)

separator3 = ttk.Separator(manual_tab, orient = 'vertical',
                           style = 'white.TSeparator')
separator3.place(relx = Ax_separator3, rely = Ay_separator, 
                 relwidth = Aw_separator, relheight = Ah_separator)

# position labels (target1, current1, target2, current2)
Aw_position = 0.15
Ah_position = 0.05
Ax_position = 0.025

Ay_target1 = 0.3
Ay_encoder1 = 0.4
Ay_target2 = 0.5
Ay_encoder2 = 0.6

A_target1 = Label(manual_tab, text = 'Target Position 1:', font = myFont)
A_target1.place(relx = Ax_position, rely = Ay_target1, 
                relwidth = Aw_position, relheight = Ah_position)

Acurrent_position1_label = Label(manual_tab, text = 'Current Position 1:', 
                                 font = myFont)
Acurrent_position1_label.place(relx = Ax_position, rely = Ay_encoder1,
                               relwidth = Aw_position, relheight = Ah_position)

A_target2 = Label(manual_tab, text = 'Target Position 2:', font = myFont)
A_target2.place(relx = Ax_position, rely = Ay_target2, 
                relwidth = Aw_position, relheight = Ah_position)

Acurrent_position1_label = Label(manual_tab, text = 'Current Position 2:', 
                                 font = myFont)
Acurrent_position1_label.place(relx = Ax_position, rely = Ay_encoder2,
                               relwidth = Aw_position, relheight = Ah_position)

# position entries (target1, curren1, target 2, current 2)
Aw_position_in = 0.125
Ah_position_in = 0.05
Ax_position_in = 0.2

enter_position_motor1 = Entry(manual_tab)#, textvariable = position_motor1_txt)
enter_position_motor1.place(relx = Ax_position_in, rely = Ay_target1,
                            relwidth = Aw_position_in, relheight = Ah_position_in)

encoder1_label = tk.Label(manual_tab, font = myFont, bg = 'white')
encoder1_label.place(relx = Ax_position_in, rely = Ay_encoder1, 
                     relwidth = Aw_position_in, relheight = Ah_position_in)

enter_position_motor1 = Entry(manual_tab)#, textvariable = position_motor1_txt)
enter_position_motor1.place(relx = Ax_position_in, rely = Ay_target2,
                            relwidth = Aw_position_in, relheight = Ah_position_in)

encoder1_label = tk.Label(manual_tab, font = myFont, bg = 'white')
encoder1_label.place(relx = Ax_position_in, rely = Ay_encoder2, 
                     relwidth = Aw_position_in, relheight = Ah_position_in)

# executing buttons (run, stop, home)
Aw_execute = 0.08
Ah_execute = 0.1
Ax_execute = 0.368

Ay_run = 0.3
Ay_stop = 0.45
Ay_home = 0.6

Arun_button = Button(manual_tab, text = 'Run',
                    bg = 'green', font = myFont)
                      #command = lambda: send_to_jevois_program('obstacle'))
Arun_button.place (relx = Ax_execute, rely = Ay_run, 
                  relwidth = Aw_execute, relheight = Ah_execute)
Astop_button = Button(manual_tab, text = 'Stop',
                    bg = 'red', font = myFont)
                      #command = lambda: send_to_jevois_program('obstacle'))
Astop_button.place (relx = Ax_execute, rely = Ay_stop, 
                  relwidth = Aw_execute, relheight = Ah_execute)
Ahome_button = Button(manual_tab, text = 'Home',
                    bg = 'blue', font = myFont)
                      #command = lambda: send_to_jevois_program('obstacle'))
Ahome_button.place (relx = Ax_execute, rely = Ay_home, 
                  relwidth = Aw_execute, relheight = Ah_execute)

# analog control buttons (up, down, left, right)
Aw_updown_analog = 0.04
Ah_updown_analog = 0.1
Aw_leftright_analog = 0.038
Ah_leftright_analog = 0.1


Aw_dpad_fill = 0.07
Ah_dpad_fill = 0.1

Ax_dpad_fill = 0.55
Ax_updown = 0.57
Ay_leftright = 0.4

Ax_left = 0.528 #.043
Ax_right = 0.613
Ay_up = 0.3
Ay_down = 0.5

Aup_button = Button(manual_tab, text = '△',
                    font = myFont)
                      #command = lambda: send_to_jevois_program('obstacle'))
Aup_button.place (relx = Ax_updown, rely = Ay_up, 
                  relwidth = Aw_updown_analog, relheight = Ah_updown_analog)
Aleftright_label = tk.Label(manual_tab, font = myFont)
Aleftright_label.place(relx = Ax_dpad_fill, rely = Ay_leftright, 
                       relwidth = Aw_dpad_fill, relheight = Ah_dpad_fill)

Aleft_button = Button(manual_tab, text = '◁',
                    font = myFont)
                      #command = lambda: send_to_jevois_program('obstacle'))
Aleft_button.place (relx = Ax_left, rely = Ay_leftright, 
                    relwidth = Aw_leftright_analog, relheight = Ah_leftright_analog)

Aright_button = Button(manual_tab, text = '▷',
                       font = myFont)
                      #command = lambda: send_to_jevois_program('obstacle'))
Aright_button.place (relx = Ax_right, rely = Ay_leftright, 
                     relwidth = Aw_leftright_analog, relheight = Ah_leftright_analog)
Adown_button = Button(manual_tab, text = '▽',
                      font = myFont)
                      #command = lambda: send_to_jevois_program('obstacle'))
Adown_button.place (relx = Ax_updown, rely = Ay_down, 
                    relwidth = Aw_updown_analog, relheight = Ah_updown_analog)

# imu axis labels
Aw_axis = 0.06
Ah_axis = Ah_position
Ax_axis = 0.72

Axaxis_label = Label(manual_tab, text = 'x-axis:​', 
                     font = myFont)
Axaxis_label.place(relx = Ax_axis, rely = Ay_target1, 
                   relwidth = Aw_axis, relheight = Ah_position)

Ayaxis_label = Label(manual_tab, text = 'y-axis:​', 
                     font = myFont)
Ayaxis_label.place(relx = Ax_axis, rely = Ay_encoder1, 
                   relwidth = Aw_axis, relheight = Ah_position)

Azaxis_label = Label(manual_tab, text = 'z-axis:​', 
                     font = myFont)
Azaxis_label.place(relx = Ax_axis, rely = Ay_target2, 
                   relwidth = Aw_axis, relheight = Ah_position)

# imu axis readings
Aw_read_axis = 0.162
Ah_read_axis = Ah_position
Ax_read_axis = 0.81

A_ximu_txt = StringVar()
A_ximu_txt.set('X-Axis Data')
A_ximu_output = Label(manual_tab, textvariable = A_ximu_txt)
A_ximu_output.place(relx = Ax_read_axis, rely = Ay_target1,
                   relwidth = Aw_read_axis, relheight = Ah_position)

A_yimu_txt = StringVar()
A_yimu_txt.set('Y-Axis Data')
A_yimu_output = Label(manual_tab, textvariable = A_yimu_txt)
A_yimu_output.place(relx = Ax_read_axis, rely = Ay_encoder1,
                   relwidth = Aw_read_axis, relheight = Ah_position)
A_zimu_txt = StringVar()
A_zimu_txt.set('Z-Axis Data')
A_zimu_output = Label(manual_tab, textvariable = A_zimu_txt)
A_zimu_output.place(relx = Ax_read_axis, rely = Ay_target2,
                   relwidth = Aw_read_axis, relheight = Ah_position)

#---# B, OBJECT TRACKING TAB #---#
object_title = Label(object_tracing_tab, text = 'Object Tracing Mode',
                     font = myFont, bg = 'white')
object_title.place(relx = 0.5, rely = tab_title_rely,
                   relheight = title_rel_height, relwidth = title_rel_width,
                   anchor = 'n')
close_object_tab = Button(object_tracing_tab, text = 'X',
                      fg = 'white', bg = 'red',
                      font = myFont,
                      command = lambda: close_tab(2))
close_object_tab.place(relx = close_tab_relx, #rely = close_tab_rely,
                   relheight = close_rel_height, relwidth = close_rel_width)
exit_gui_from_object = tk.Button(object_tracing_tab, text = "Exit GUI", command = close_window)
exit_gui_from_object.place(relx = 0.02, rely = 0.88,
                      relheight = 0.1, relwidth = 0.2)

# # PATTERN TAB #
pattern_title = Label(pattern_tab, text = 'Pattern Mode',
                     font = myFont, bg = 'white')
pattern_title.place(relx = 0.5, rely = tab_title_rely, 
                    relheight = title_rel_height, relwidth = title_rel_width,
                    anchor = 'n')
close_pattern_tab = Button(pattern_tab, text = 'X',
                      fg = 'white', bg = 'red',
                      font = myFont,
                      command = lambda: close_tab(3))
close_pattern_tab.place(relx = close_tab_relx, #rely = close_tab_rely,
                   relheight = close_rel_height, relwidth = close_rel_width)
exit_gui_from_pattern = tk.Button(pattern_tab, text = "Exit GUI", command = close_window)
exit_gui_from_pattern.place(relx = 0.02, rely = 0.88,
                      relheight = 0.1, relwidth = 0.2)

'''
start_button = Button(root, text = 'Display IMU Reading',
                      font = myFont, command = start,
                      bg = 'bisque2', height = 1,
                      width = 24)
start_button.grid(row=0, column=1) 
start_button.config(relief='raised')
 
stop_button = Button(root, text = 'Hide IMU Reading',
                     font = myFont, command = stop,
                     bg = 'bisque2', height = 1,
                     width = 24)
stop_button.grid(row=0, column=2)                 # location in gui
stop_button.config(relief='raised')
'''

'''
## Jevois - CV ##
# j = jevois, row = r, column = c
jr1_rely = 0.3
jr2_rely = 0.7
jc1_relx = 0.25
jc2_relx = 0.5
jc3_relx = 0.75
j_relheight = 0.3
j_relwidth = 0.2

jevois_label = tk.Label(upper_frame, text = 'Computer Vision Control', font = myFont)
jevois_label.place(relx = 0.5, 
                   relheight = 0.25, relwidth = 0.25,
                   anchor = 'n')

mode_label = tk.Label(upper_frame, text = 'select mode:', font = myFont, bg = 'white')
mode_label.place(rely = jr1_rely, 
                 relheight = j_relheight, relwidth = j_relwidth)

color_label = tk.Label(upper_frame, text='select color:', font = myFont, bg = 'white')
color_label.place(rely = jr2_rely, 
                  relheight = j_relheight, relwidth = j_relwidth)

jevois_text = StringVar()
jevois_text.set("Jevois Camera Readings")
jevois_output = Label(lower_frame, textvariable = jevois_text, bg = 'white')
jevois_output.place(rely = 0.6,
                    relheight = 0.15, relwidth = 1)

calibration_button = Button(upper_frame, text = 'calibration', font = myFont,
                            command = lambda: send_to_jevois_program('calibration'))
calibration_button.place(relx = jc1_relx, rely = jr1_rely, 
                         relheight = j_relheight, relwidth = j_relwidth)

obstacle_button = Button(upper_frame, text = 'obstacle', font = myFont,
                         command = lambda: send_to_jevois_program('obstacle'))
obstacle_button.place(relx = jc2_relx, rely = jr1_rely, 
                      relheight = j_relheight, relwidth = j_relwidth)

target_button = Button(upper_frame, text = 'target', font = myFont,
                       command = lambda: send_to_jevois_program('target'))
target_button.place(relx = jc3_relx, rely = jr1_rely, 
                    relheight = j_relheight, relwidth = j_relwidth)

red_button = Button(upper_frame, text = 'red', font = myFont, 
                    activebackground = 'red',
                    command = lambda: send_to_jevois_program('red'))
red_button.place(relx = jc1_relx, rely = jr2_rely, 
                 relheight = j_relheight, relwidth = j_relwidth)

green_button = Button(upper_frame, text = 'green', font = myFont, 
                      activebackground = 'green',
                      command = lambda: send_to_jevois_program('green'))
green_button.place(relx = jc2_relx, rely = jr2_rely, 
                   relheight = j_relheight, relwidth = j_relwidth)

blue_button = Button(upper_frame, text = 'blue', font = myFont, 
                     activebackground = 'blue',
                     command = lambda: send_to_jevois_program('blue'))
blue_button.place(relx = jc3_relx, rely = jr2_rely, 
                  relheight = j_relheight, relwidth = j_relwidth)

## Arduino - Motors ##

ar4_rely =  0.6       # row 3: motor 3 info
ar5_rely = 0.75       # row 4: motor 4 info
ar6_rely = 0.9        # row 5: buttons row
ac3_relx = 0.7        # column 3: encoder feedback
stepper_enable_relx = 0.63
run_relx = 0.85
run_relwidth = 0.1
warning_relwidth = 0.25


arduino_label = tk.Label(middle_frame, text = 'Arduino Communication', font = myFont)
arduino_label.place(relx = 0.5, 
                    relwidth = 0.25, relheight = a_relheight, 
                    anchor = 'n')



speed_label = tk.Label(middle_frame, text = 'speed (steps/s)', font = myFont)
speed_label.place(relx = ac2_relx, rely = ar1_rely, 
                  relwidth = a_relwidth, relheight = a_relheight)

speed_warning_label = tk.Label (middle_frame, text = 'warning: do not exceed 200 steps/s', font = myFont)
speed_warning_label.place(rely = ar6_rely, 
                          relwidth = warning_relwidth, relheight = a_relheight)


motor1_speed_entry = tk.Entry(middle_frame)
motor1_speed_entry.place(relx = ac2_relx, rely = ar2_rely, 
                         relwidth = a_relwidth, relheight = a_relheight)

motor2_speed_entry = tk.Entry(middle_frame)
motor2_speed_entry.place(relx = ac2_relx, rely = ar3_rely, 
                         relwidth = a_relwidth, relheight = a_relheight)


stepper_enable_button = Button(middle_frame, text = 'Stepper Motors Disabled!', 
                               bg = 'red', font = myFont)
                            #    command = stepper_enable)
stepper_enable_button.place(relx = stepper_enable_relx, rely = ar6_rely, 
                            relwidth = a_relwidth, relheight = a_relheight)



## IMU Readings ##

'''

# root.after(1000, run) # after 1 s, call scanning
root.mainloop()