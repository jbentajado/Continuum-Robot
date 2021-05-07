import smbus
import math
import time
import serial

from tkinter import *
from tkinter import ttk
from math import *
import tkinter as tk
import tkinter.font

class ContinuumGUI:    
    def __init__(self, master, gyro, acc, tau):
        # Class / object / constructor setup
        self.gx = None; self.gy = None; self.gz = None;
        self.ax = None; self.ay = None; self.az = None;

        self.gyroXcal = 0
        self.gyroYcal = 0
        self.gyroZcal = 0

        self.gyroRoll = 0
        self.gyroPitch = 0
        self.gyroYaw = 0

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.dtTimer = 0
        self.tau = tau

        self.gyroScaleFactor, self.gyroHex = self.gyroSensitivity(gyro)
        self.accScaleFactor, self.accHex = self.accelerometerSensitivity(acc)

        self.bus = smbus.SMBus(1)
        self.address = 0x68
        
        # Serial - Jevois
        jevois_baudrate = 115200
        com_port1 = '/dev/ttyACM0'
        self.ser1 = serial.Serial(port = com_port1, baudrate = jevois_baudrate,
                                  parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                  bytesize=serial.EIGHTBITS, timeout=1)
        
        # Serial - Arduino
        arduino_baudrate = 115200 
        com_port2 = '/dev/ttyACM1'    # under the wifi usb
        self.ser2 = serial.Serial(port = com_port2, baudrate = arduino_baudrate, timeout = 0)    # my port = '/dev/ttyACM0'
        ####
        
        # Fonts
        BG = '#222222'
        LABEL_BG = '#ffefdb'
        LITE_BG = '#829AB1'
        WITE_BG = '#F0F4F8'
        DARK_BG = '#334E68'
                
        lite_widget_font = tkinter.font.Font(family='Helvetica', size=12,
                                                  weight="bold")
        dark_widget_font = tkinter.font.Font(family = 'Helvetica', size = 12,
                                                  weight = "bold")

        self.master = master
        master.title("Continuum Robot GUI")
                
        # self.HEIGHT = 500   # pixels
        # self.WIDTH = 1300    
        
        self.HEIGHT = 700
        self.WIDTH = 2600   
             
        canvas = tk.Canvas(master, height=self.HEIGHT, width=self.WIDTH)
        canvas.pack
        
        self.my_notebook = ttk.Notebook(master)
        self.my_notebook.pack(pady = 0)
        
        # define what is inside the tabs using frames
        mode_selection_tab = Frame(self.my_notebook, bd=10,
                                    width=self.WIDTH, height=self.HEIGHT, 
                                    bg=BG)
        manual_tab = Frame(self.my_notebook, bd=10,
                                width=self.WIDTH, height=self.HEIGHT, 
                                bg=BG)
        object_tracing_tab = Frame(self.my_notebook, bd=10,
                                        width=self.WIDTH, height=self.HEIGHT,
                                        bg=BG)
        pattern_tab = Frame(self.my_notebook, bd=10,
                                width=self.WIDTH, height=self.HEIGHT,
                                bg=BG)

        mode_selection_tab.pack(fill='both', expand=1)
        manual_tab.pack(fill='both', expand=1)
        object_tracing_tab.pack(fill='both', expand=1)
        pattern_tab.pack(fill='both', expand=1)

        # designate the tabs
        self.my_notebook.add(mode_selection_tab, text = 'Mode Selection')
        self.my_notebook.add(manual_tab, text = 'Manual Mode')
        self.my_notebook.add(object_tracing_tab, text = 'Object Tracing Mode')
        self.my_notebook.add(pattern_tab, text = 'Pattern Mode')
        
        # hide the different modes
        self.my_notebook.hide(1)
        self.my_notebook.hide(2)
        self.my_notebook.hide(3)
        
        ### WIDGETS ###
        '''
        legend:
            x = relx
            y = rely
            w = width
            h = height
        '''
        
        # Arduino mode chars:
        manual_on = b'<' + b'M' + b'M' + b'1' + b'>'
        manual_off = b'<' + b'M' + b'M' + b'0' + b'>'    
        
        object_tracing_on = b'<' + b'O' + b'T' + b'1' + b'>'
        object_tracing_off = b'<' + b'O' + b'T' + b'1' + b'>'   
        
        pattern_on = b'<' + b'P' + b'M' + b'1' + b'>'
        pattern_off = b'<' + b'P' + b'M' + b'0' + b'>'
        
        home = b'<' + b'H' + b'>' 
        
        joystick_on = b'<' + b'J' + b'S' + b'1' + b'>'
        joystick_off = b'<' + b'J' + b'S' + b'0' + b'>'
        
        circle_on = b'<' + b'C' + b'P' + b'1' + b'>'
        circle_off = b'<' + b'C' + b'P' + b'0' + b'>'
        square_on = b'<' + b'S' + b'P' + b'1' + b'>'
        square_off = b'<' + b'S' + b'P' + b'0' + b'>'

        # GLOBAL MODE TAB WIDGET SIZING #
        title_rel_height = 0.08
        title_rel_width = 0.95
        close_tab_relx = 0.98
        close_rel_height = 0.05
        close_rel_width = 0.02
        tab_title_rely = 0.05
        
        w_homing = 0.08
        h_homing = 0.1
        
        x_homing = 0.92
        y_homing = 0.9
        
        #---# MODE SELECTION TAB #---#

        # DIMENSIONS
        mode_sel_rely = 0.2
        mode_sel_relheight = 0.1
        mode_sel_relwidth = 0.2
        
        # LAYOUT
        select_mode_label = Label(mode_selection_tab, text='Select Control Mode:', 
                          font=dark_widget_font, bg=DARK_BG,
                          fg=WITE_BG)
        select_mode_label.place(relx=0.5, rely=tab_title_rely,
                                relheight=title_rel_height, relwidth=title_rel_width,
                                anchor='n')
        
        # manual mode
        manual_button = Button(mode_selection_tab, text='Manual Mode',
                            font=lite_widget_font, bg=DARK_BG, fg=WITE_BG,
                            command = lambda: self.show_tab(manual_tab, 'Manual Mode', manual_on))
        manual_button.place(relx=0.15, rely=mode_sel_rely,
                            relheight=mode_sel_relheight, relwidth=mode_sel_relwidth)
                
        # object tracing mode
        object_trace_button = Button(mode_selection_tab, text = 'Object Tracing Mode',
                                     font=lite_widget_font, bg=DARK_BG, fg=WITE_BG,
                                     command = lambda: self.show_tab(object_tracing_tab, 'Object Tracing Mode', object_tracing_on))
        object_trace_button.place(relx=0.4, rely=mode_sel_rely,
                                  relheight=mode_sel_relheight, relwidth=mode_sel_relwidth)

        # pattern mode
        pattern_button = Button(mode_selection_tab, text = 'Pattern Mode',
                                font=lite_widget_font, bg=DARK_BG, fg=WITE_BG,
                                command = lambda: self.show_tab(pattern_tab, 'Pattern Mode', pattern_on))
        pattern_button.place(relx=0.65, rely=mode_sel_rely,
                            relheight=mode_sel_relheight, relwidth=mode_sel_relwidth)
        
        # mode descriptions
        manual_description_text = 'Manual Mode: Control the continuum robot manually by inputting the amount of pulses for the motors to move.'
        object_description_text = 'Object Tracing Mode: Utilize computer vision to have the robot follow different colored objects'
        pattern_description_text = 'Pattern Tracing Mode: Select a shape for the robot to trace in coordinates.'

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
                                    command=self.close_window)
        exit_gui_button.place(rely=0.9,
                              relheight=0.1, relwidth=0.2)
        
        #---# MANUAL MODE TAB #---#    
        manual_title = Label(manual_tab, text = 'Manual Mode',
                             font=lite_widget_font, bg=DARK_BG, fg=WITE_BG)
        manual_title.place(relx=0.5, rely=tab_title_rely,
                           relheight=title_rel_height, relwidth=title_rel_width,
                           anchor='n')
        close_manual_tab = Button(manual_tab, text='X',
                                  fg='white', bg='red',
                                  font=lite_widget_font,
                                  command=lambda:self.close_tab(1, manual_off))
        close_manual_tab.place(relx=close_tab_relx, #rely = close_tab_rely,
                               relheight=close_rel_height, relwidth=close_rel_width)
        exit_gui_from_manual = Button(manual_tab, text='Exit GUI', 
                                        bg=DARK_BG, fg=WITE_BG,
                                        command=self.close_window)
        exit_gui_from_manual.place(relx=0.02, rely=0.88,
                                   relheight=0.1, relwidth=0.2)
        
        homing_from_manual = Button(manual_tab, text='Home',
                                    font=lite_widget_font, 
                                    bg=LITE_BG, fg=WITE_BG,
                                    command=lambda:self.set_arduino_mode(home))
        homing_from_manual.place(relx=x_homing, rely=y_homing,
                                 relheight=h_homing, relwidth=w_homing)
                
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
                            command=lambda:self.manual_move_motors(position1, position2))
        run_button.place (relx=x_run, rely=y_run, 
                        relwidth=w_run, relheight=h_run)

        # joystick, on/off
        x_joystick = 0.5
        w_joystick = 0.08
        h_joystick = 0.1

        y_on = 0.3
        y_off = y_on + 0.15

        on_button = Button(manual_tab, text='On',
                            bg=LITE_BG, font=lite_widget_font,
                            command=lambda:self.set_arduino_mode(joystick_on))
        on_button.place (relx=x_joystick, rely=y_on, 
                         relwidth=w_joystick, relheight=h_joystick,
                         anchor = 'n')
        off_button = Button(manual_tab, text='Off',
                            bg=DARK_BG, font=dark_widget_font,
                            command = lambda:self.set_arduino_mode(joystick_off))
        off_button.place (relx=x_joystick, rely=y_off, 
                        relwidth=w_joystick, relheight=h_joystick,
                        anchor = 'n')

        # imu axis labels
        Aw_axis = 0.07
        Ah_position = 0.05
        Ax_axis = 0.675

        # the arm's yaw is about the IMU's y axis
        yaw_label = Label(manual_tab, text = 'yaw:​', 
                          font=lite_widget_font, bg=LITE_BG, fg=WITE_BG)
        yaw_label.place(relx=Ax_axis, rely=y_target1, 
                        relwidth=Aw_axis, relheight=Ah_position)

        # the arm's pitch is about the IMU's x axis
        self.pitch_label = Label(manual_tab, text = 'pitch:​', 
                            font=lite_widget_font, bg=LITE_BG, fg=WITE_BG)
        self.pitch_label.place(relx=Ax_axis, rely=y_encoder1, 
                          relwidth=Aw_axis, relheight=Ah_position)

        # imu axis readings
        Aw_read_axis = 0.205
        Ah_read_axis = Ah_position
        Ax_read_axis = 0.77

        self.yaw_text = StringVar()
        self.yaw_text.set('Yaw Data')
        self.yaw_output = Label(manual_tab, textvariable=self.yaw_text,
                                bg=LITE_BG, fg=WITE_BG)
        self.yaw_output.place(relx=Ax_read_axis, rely=y_target1,
                              relwidth=Aw_read_axis, relheight=Ah_position)

        
        self.pitch_text = StringVar()
        self.pitch_output = Label(manual_tab, textvariable=self.pitch_text,
                            bg=LITE_BG, fg=WITE_BG)
        self.pitch_output.place(relx=Ax_read_axis, rely=y_encoder1,
                        relwidth=Aw_read_axis, relheight=Ah_position)
        self.pitch_text.set('Pitch Reading')

        #---# OBJECT TRACKING TAB #---#
        object_title = Label(object_tracing_tab, text='Object Tracing Mode',
                            font=lite_widget_font, bg=DARK_BG, fg=WITE_BG)
        object_title.place(relx=0.5, rely=tab_title_rely,
                        relheight=title_rel_height, relwidth=title_rel_width,
                        anchor='n')
        close_object_tab = Button(object_tracing_tab, text = 'X',
                            fg='white', bg='red',
                            font=lite_widget_font,
                            command=lambda:self.close_tab(2, object_tracing_off))
        close_object_tab.place(relx=close_tab_relx, #rely = close_tab_rely,
                        relheight=close_rel_height, relwidth=close_rel_width)

        exit_gui_from_object = tk.Button(object_tracing_tab, text="Exit GUI", 
                                        bg=DARK_BG, fg=WITE_BG,
                                        command=self.close_window)
        exit_gui_from_object.place(relx=0.02, rely=0.88,
                            relheight=0.1, relwidth=0.2)
        
        homing_from_object = Button(object_tracing_tab, text='Home',
                                    font=lite_widget_font, 
                                    bg=LITE_BG, fg=WITE_BG,
                                    command=lambda:self.set_arduino_mode(home))
        homing_from_object.place(relx=x_homing, rely=y_homing,
                                 relheight=h_homing, relwidth=w_homing)

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
                                    command=lambda:self.send_to_jevois_program('calibration'))
        calibration_button.place(relx = x_red_calibration, rely=y_mode, 
                                relheight=h_jevois, relwidth=w_jevois)

        obstacle_button = Button(object_tracing_tab, text='obstacle', font=lite_widget_font,
                                command=lambda:self.send_to_jevois_program('obstacle'))
        obstacle_button.place(relx=x_green_obstacle, rely=y_mode, 
                            relheight=h_jevois, relwidth=w_jevois)

        target_button = Button(object_tracing_tab, text='target', font=lite_widget_font,
                            command=lambda:self.send_to_jevois_program('target'))
        target_button.place(relx=x_blue_target, rely=y_mode, 
                            relheight=h_jevois, relwidth=w_jevois)         

        # color selection buttons
        red_button = Button(object_tracing_tab, text='red', font=lite_widget_font, 
                            activebackground='red',
                            command=lambda:self.send_to_jevois_program('red'))
        red_button.place(relx=x_red_calibration, rely=y_color, 
                        relheight=h_jevois, relwidth=w_jevois)

        green_button = Button(object_tracing_tab, text='green', font=lite_widget_font, 
                            activebackground='green',
                            command=lambda:self.send_to_jevois_program('green'))
        green_button.place(relx=x_green_obstacle, rely=y_color, 
                        relheight=h_jevois, relwidth=w_jevois)

        blue_button = Button(object_tracing_tab, text='blue', font=lite_widget_font, 
                            activebackground='blue',
                            command=lambda:self.send_to_jevois_program('blue'))
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
                                command=lambda:self.close_tab(3, pattern_off))
        close_pattern_tab.place(relx=close_tab_relx,
                        relheight=close_rel_height, relwidth=close_rel_width)

        exit_gui_from_pattern = tk.Button(pattern_tab, text="Exit GUI", 
                                        bg=DARK_BG, fg=WITE_BG,
                                        command=self.close_window)
        exit_gui_from_pattern.place(relx=0.02, rely=0.88,
                                    relheight=0.1, relwidth=0.2)
        
        homing_from_pattern = Button(pattern_tab, text='Home',
                                    font=lite_widget_font, 
                                    bg=LITE_BG, fg=WITE_BG,
                                    command=lambda:self.set_arduino_mode(home))
        homing_from_pattern.place(relx=x_homing, rely=y_homing,
                                 relheight=h_homing, relwidth=w_homing)

        # pattern selection
        pattern_space = 0.2

        x_pattern = 0.225
        x_circle = x_pattern + pattern_space
        x_square = x_circle + pattern_space

        on_off_space = 0.15
        y_on = 0.2
        y_off = y_on + on_off_space

        select_pattern = Label(pattern_tab, text='select pattern:', 
                            font=dark_widget_font, 
                            bg=DARK_BG, fg=WITE_BG)
        select_pattern.place(relx=x_pattern, rely=y_on,
                            relheight=h_jevois, relwidth=w_jevois)

        circle_mode_on = Button(pattern_tab, text='circle on', 
                                font=lite_widget_font, bg=LITE_BG,
                                command=lambda:self.set_arduino_mode(circle_on))
        circle_mode_on.place(relx=x_circle, rely=y_on, 
                            relheight=h_jevois, relwidth=w_jevois)

        circle_mode_off = Button(pattern_tab, text='circle off', font=lite_widget_font, 
                                bg=DARK_BG, fg=WITE_BG,
                                command=lambda:self.set_arduino_mode(circle_off))
        circle_mode_off.place(relx=x_circle, rely=y_off, 
                            relheight=h_jevois, relwidth=w_jevois)

        square_mode_on = Button(pattern_tab, text='square on', 
                                font=lite_widget_font, bg=LITE_BG,
                                command=lambda:self.set_arduino_mode(square_on))
        square_mode_on.place(relx=x_square, rely=y_on, 
                            relheight=h_jevois, relwidth=w_jevois)

        square_mode_off = Button(pattern_tab, text='square off', font=lite_widget_font, 
                                bg=DARK_BG, fg=WITE_BG,
                                command=lambda:self.set_arduino_mode(square_off))
        square_mode_off.place(relx=x_square, rely=y_off, 
                            relheight=h_jevois, relwidth=w_jevois)

        self.running = True
     
    def gyroSensitivity(self, x):
        # Create dictionary with standard value of 500 deg/s
        return {
            250:  [131.0, 0x00],
            500:  [65.5,  0x08],
            1000: [32.8,  0x10],
            2000: [16.4,  0x18]
        }.get(x,  [65.5,  0x08])

    def accelerometerSensitivity(self, x):
        # Create dictionary with standard value of 4 g
        return {
            2:  [16384.0, 0x00],
            4:  [8192.0,  0x08],
            8:  [4096.0,  0x10],
            16: [2048.0,  0x18]
        }.get(x,[8192.0,  0x08])

    def setUp(self):
        # Activate the MPU-6050
        self.bus.write_byte_data(self.address, 0x6B, 0x00)

        # Configure the accelerometer
        self.bus.write_byte_data(self.address, 0x1C, self.accHex)

        # Configure the gyro
        self.bus.write_byte_data(self.address, 0x1B, self.gyroHex)

        # Display message to user
        print("MPU set up:")
        print('\tAccelerometer: ' + str(self.accHex) + ' ' + str(self.accScaleFactor))
        print('\tGyro: ' + str(self.gyroHex) + ' ' + str(self.gyroScaleFactor) + "\n")
        time.sleep(2)
             
    def send_to_jevois_program(self, cmd):
        """Send commands to the Jevois program to control the camera

        Args:
            cmd ([string]): the command to be sent to the jevois program terminal
        """
        # print(cmd)
        self.ser1.write((cmd + '\n').encode())
        # time.sleep(1)
        print('Message was sent to Jevois!')
        
    def set_arduino_mode(self,trigger):
        send_char = trigger
        print(send_char)
        self.ser2.write(send_char)    
  
    def manual_move_motors(self, motor1, motor2):
        move_motor1 = b'<' + b'1' + b'p' + motor1.get().encode() + b'>'
        move_motor2 = b'<' + b'2' + b'p' + motor2.get().encode() + b'>'
        print('move to position 1:', move_motor1)
        print('move to position 2:', move_motor2)
        char = move_motor1 + move_motor2
        self.set_arduino_mode(char)
 
    def send_axes(self, pitch, yaw):
        # robot pitch = Ix
        # robot yaw = Iy
        
        x_theta = b'<' + b'I' + b'x' + pitch.encode() + b'>'
        y_theta = b'<' + b'I' + b'y' + yaw.encode() + b'>'
        char = x_theta + y_theta
        
        # print('send pitch/yaw: ', char)
        self.set_arduino_mode(char)

    # def trace_trace_move_motors(x, y):
    #     global newx_position, newy_position
        
    #     x_to_arduino = b'<' + b'J' + b'x' + str(x).encode() + b'>'
    #     y_to_arduino = b'<' + b'J' + b'y' + str(y).encode() + b'>'
    #     print('move to position 1:', x_to_arduino)
    #     print('move to position 2:', y_to_arduino)
        
    #     serialread2 = self.ser2.readline()
    #     print(serialread2)
        
    #     self.ser2.write(x_to_arduino + y_to_arduino) 
    
    def show_tab(self, mode_frame, mode_selection, mode):
        self.my_notebook.add(mode_frame, text = mode_selection)
        self.set_arduino_mode(mode)
        self.my_notebook.tab(0, state='disabled')
    
    def close_tab(self, i_tab, mode):
        self.my_notebook.hide(i_tab)
        self.set_arduino_mode(mode)
        
        self.my_notebook.tab(0, state='normal')
        self.my_notebook.select(0)
    
    def close_window(self):
        self.master.destroy()

    # def eightBit2sixteenBit(self, reg):
    #     # Reads high and low 8 bit values and shifts them into 16 bit
    #     h = self.bus.read_byte_data(self.address, reg)
    #     l = self.bus.read_byte_data(self.address, reg+1)
    #     val = (h << 8) + l

    #     # Make 16 bit unsigned value to signed value (0 to 65535) to (-32768 to +32767)
    #     if (val >= 0x8000):
    #         return -((65535 - val) + 1)
    #     else:
    #         return val
        
    # def getRawData(self):
    #     self.gx = self.eightBit2sixteenBit(0x43)
    #     self.gy = self.eightBit2sixteenBit(0x45)
    #     self.gz = self.eightBit2sixteenBit(0x47)

    #     self.ax = self.eightBit2sixteenBit(0x3B)
    #     self.ay = self.eightBit2sixteenBit(0x3D)
    #     self.az = self.eightBit2sixteenBit(0x3F)
        
    # def calibrateGyro(self, N):
    #     # Display message
    #     print("Calibrating gyro with " + str(N) + " points. Do not move!")

    #     # Take N readings for each coordinate and add to itself
    #     for ii in range(N):
    #         self.getRawData()
    #         self.gyroXcal += self.gx
    #         self.gyroYcal += self.gy
    #         self.gyroZcal += self.gz

    #     # Find average offset value
    #     self.gyroXcal /= N
    #     self.gyroYcal /= N
    #     self.gyroZcal /= N

    #     # Display message and restart timer for comp filter
    #     print("Calibration complete")
    #     print("\tX axis offset: " + str(round(self.gyroXcal,1)))
    #     print("\tY axis offset: " + str(round(self.gyroYcal,1)))
    #     print("\tZ axis offset: " + str(round(self.gyroZcal,1)) + "\n")
    #     time.sleep(2)
    #     self.dtTimer = time.time()
        
    # def processIMUvalues(self):
    #     # Update the raw data
    #     self.getRawData()

    #     # # Subtract the offset calibration values
    #     # self.gx -= self.gyroXcal
    #     # self.gy -= self.gyroYcal
    #     # self.gz -= self.gyroZcal

    #     # Convert to instantaneous degrees per second
    #     self.gx /= self.gyroScaleFactor
    #     self.gy /= self.gyroScaleFactor
    #     self.gz /= self.gyroScaleFactor

    #     # # Convert to g force
    #     self.ax /= self.accScaleFactor
    #     self.ay /= self.accScaleFactor
    #     self.az /= self.accScaleFactor
    

    def compFilter(self):
        if self.running: 
            # # Get the processed values from IMU
            # self.processIMUvalues()

            # # Get delta time and record time for next call
            # dt = time.time() - self.dtTimer
            # self.dtTimer = time.time()

            # # Acceleration vector angle
            # accPitch = math.degrees(math.atan2(self.ay, self.az))
            # accRoll = math.degrees(math.atan2(self.ax, self.az))

            # # Gyro integration angle
            # self.gyroRoll -= self.gy * dt # y
            # self.gyroPitch += self.gx * dt # x
            # self.gyroYaw += self.gz * dt
            # self.yaw = self.gyroYaw
            
            # # Comp filter
            # # imu roll = robot pitch = Ix
            # self.roll = (self.tau)*(self.roll + self.gy*dt) + (1-self.tau)*(accRoll)
            # # imu pitch = robot yaw = Iy
            # self.pitch = (self.tau)*(self.pitch + self.gx*dt) + (1-self.tau)*(accPitch)
            
            # self.roll_str = round(self.roll, 2)
            # self.roll_str = '%.1f' % round(self.roll_str, 1)
            
            # self.pitch_str = round(self.pitch, 2)
            # self.pitch_str = '%.1f' % round(self.pitch_str, 1)
            
            # # Print data - robot's pitch and yaw
            # self.yaw_text.set(self.pitch_str)
            # self.pitch_text.set(self.roll_str)
            
            # print(" R: " \
            #     + " P: " + str(round(self.roll,1)) \
            #     + " Y: " + str(round(self.pitch,1)))
            
            # # print("Get IMU Data")
            # # print("\tRobot Yaw: " + self.pitch_str)
            # # print("\tRobot Pitch: " + self.roll_str)

            # # Send pitch and yaw to arduino
            # # def send_axes(self, pitch, yaw):
            # self.send_axes(self.roll_str, self.pitch_str)  
                    

            # # print(" R: " + str(round(self.roll,1)) \
            # #     + " P: " + str(round(self.pitch,1)))
            # #     + " Y: " + str(round(self.yaw,1)))
            time.sleep(0.5)
            
        self.master.after(20, self.compFilter)
        
def main():
    ## Set up class
    root = Tk()
    gyro = 250      # 250, 500, 1000, 2000 [deg/s]
    acc = 2         # 2, 4, 7, 16 [g]
    tau = 0.98
    
    cbot = ContinuumGUI(root, gyro, acc, tau)
    cbot.setUp()
    # cbot.calibrateGyro(300)
    cbot.compFilter()
    root.mainloop()

    # End
    print("Closing")

if __name__ == '__main__':
	main()