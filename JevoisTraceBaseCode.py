# Jevois Trace base code.py
'''
changes made:
- 
'''

import time
import smbus
import math
import serial



jevois_baudrate= 115200
com_port1 = '/dev/serial0'
ser1 = serial.Serial(port = com_port1, baudrate = jevois_baudrate,
                    parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS, timeout=1)

# Serial - Arduino
arduino_baudrate = 115200 
com_port2 = '/dev/ttyACM0'    # under the wifi usb
ser2 = serial.Serial(port = com_port2, baudrate = arduino_baudrate, timeout = 0)    # my port = '/dev/ttyACM0'
# serial_string = ""   # initializes string for serial port

### EVENT FUNCTIONS ###
running = True # global flag

def send_to_jevois_program(cmd):
    """Send commands to the Jevois program to control the camera

    Args:
        cmd ([string]): the command to be sent to the jevois program terminal
    """
    # print(cmd)
    ser1.write((cmd + '\n').encode())
    time.sleep(1)
    print('Message was sent to Jevois!')

# global newx_position, newy_position  
def manual_mode(q,p):
    x_to_arduino = b'<' + b'J' + b'x' + str(x).encode() + b'>'
    y_to_arduino = b'<' + b'J' + b'y' + str(y).encode() + b'>'
    print('move to position 1:', x_to_arduino)
    print('move to position 2:', y_to_arduino)

def manual_entry():
    q = motor1_position_entry.get().encode()
    p = motor2_position_entry.get().encode()

    x_to_arduino = b'<' + b'1' + b'p' + q + b'>'
    y_to_arduino = b'<' + b'2' + b'p' + p + b'>'
    print('move to position 1:', x_to_arduino)
    print('move to position 2:', y_to_arduino)
    
    ##serialread2 = ser2.readline()
    ##print(serialread2)
    
    ser2.write(x_to_arduino + y_to_arduino)

def move_motors(x, y):
    global newx_position, newy_position
    
    x_to_arduino = b'<' + b'J' + b'x' + str(x).encode() + b'>'
    y_to_arduino = b'<' + b'J' + b'y' + str(y).encode() + b'>'

    #serialread2 = ser2.readline()
    #print(serialread2)
    
    ser2.write(x_to_arduino + y_to_arduino)


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

        #time.sleep(0.5)  #  <<<< THIS IS WHY THE MOTION WAS CHOPPY
        
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
        else: 
            x = 0
            y = 0
                
    print ('X coordinate: {} | Y coordinate: {}'.format(x,y))
    jevois_reading = 'X coordinate: {} | Y coordinate: {}'.format(x,y)
    jevois_text.set(jevois_reading)
    #if x != 0 or y != 0:
    #if x > 1 or x < -1 or y > 1 or y < -1: # Centering deadzone
    #    move_motors(x, y)
    move_motors(x,y)
    # blink()

    if not running:
        print("this is not running")
        buttercup_text.set("buttercup IMU readings unavailable")
        bubbles_text.set("Bubbles IMU readings unavailable")
 
    # after 0.5 s, call scanning again,  1/2 s = 500
    root.after(1, run)
 
# def close():
#     RPi.GPIO.cleanup()
#     root.destroy()
    
prevTime = 0
while True:
    
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
        else: 
            x = 0
            y = 0   
        
       # dt = time.monotonic()-prevTime
        print ('X coordinate: {} | Y coordinate: {}'.format(x,y))
        jevois_reading = 'X coordinate: {} | Y coordinate: {}'.format(x,y)
        
         #jevois_text.set(jevois_reading)
         #if x != 0 or y != 0:
         #if x > 1 or x < -1 or y > 1 or y < -1: # Centering deadzone
         #    move_motors(x, y)
        move_motors(x,y)
         # blink()
        # prevTime = time.monotonic()
        
        