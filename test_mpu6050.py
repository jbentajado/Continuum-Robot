# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import matplotlib.pyplot as plt
import numpy as np
from math import *
from adafruit_mpu6050 import MPU6050
from matplotlib.animation import FuncAnimation

radToDeg = 180/pi

# i2c = board.I2C()  # uses board.SCL and board.SDA
# mpu = adafruit_mpu6050.MPU6050(i2c)
blossom_mpu6050 = MPU6050(board.I2C())   


        # pitch = atan2(accelX, sqrt(accelY*accelY + accelZ*accelZ))*radToDeg
        # roll = atan2(accelY, sqrt(accelX*accelX + accelZ*accelZ))*radToDeg
# running = True

fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

x = []
y_pitch = []
y_roll = []

def animate(i):
# while running:
        # read the accel/gyro tuples
        read_accel = blossom_mpu6050.acceleration   
        read_gyro = blossom_mpu6050.gyro           

        # unpack the accel/gyro tuples and assign values to variables
        angular_accelX, angular_accelY, angular_accelZ = read_accel       # unpacks tuple
        angular_velX, angular_velY, angular_velZ = read_gyro           

        # round the angular acceleration and angular velocity to 2 decimals 
        round_to_decimal = 2  
        
        angular_accelX = round(angular_accelX, round_to_decimal)       
        angular_accelY = round(angular_accelY, round_to_decimal)
        angular_accelZ = round(angular_accelZ, round_to_decimal)
                
        angular_velX = round(angular_velX, round_to_decimal)
        angular_velY = round(angular_velY, round_to_decimal)
        angular_velZ = round(angular_velZ, round_to_decimal)
        
        # calculate dt
        dtTimer = time.time()
        dt = time.time() - dtTimer
        x.append(dtTimer)
        
        # calculate theta from gyroscope
        gyroX = 0
        gyroY = 0
        
        gyroX = gyroX + (angular_velX/32.8)*dt
        gyroY = gyroY +(angular_velY/32.8)*dt

        print(gyroX)
        # calculate roll and pitch
        imu_pitch = atan2(angular_accelY, angular_accelZ)*radToDeg     # about IMU x axis, equivalent to arm's roll
        imu_roll = atan2(angular_accelX, angular_accelZ)*radToDeg      # about IMU y axis, equivalent to arm's pitch

        # y_pitch.append(pitch)

        # complementary filter
        alpha = 0.98
        comp_filter_pitch = 0
        comp_filter_roll = 0
        
        # about x axis
        comp_filter_pitch = alpha*(comp_filter_pitch + gyroX*dt) + (1-alpha)*(imu_pitch)
        # about y axis
        comp_filter_roll =  alpha*(comp_filter_roll + gyroY*dt) + (1-alpha)*(imu_roll)
        

        # # Plot Roll
        # ax1.set_title('Unfiltered vs. Filtered Roll')
        # ax1.set_xlabel('time (s)')
        # ax1.set_ylabel('Roll (degrees)')
        # ax1.plot(x, y_roll, color = 'green')
        # ax1.legend()
        # ax1.set_ylim([-180, 180])

        # # Plot Pitch
        # ax2.set_title('Unfiltered vs. Filtered Pitch')
        # ax2.set_xlabel('time (s)')
        # ax2.set_ylabel('Pitch (degrees)')
        # ax2.plot(x, y_pitch, color = 'blue')
        # ax2.legend()
        # ax2.set_ylim([-180, 180])
        # plt.plot(dtTimer, comp_filter_roll, color='red')

        print('dt: ', dt)
        print('pitch: ', imu_pitch)
        print('pitch, complementary filter: ', comp_filter_pitch)
        print('roll: ', imu_roll)
        print('roll, complementary filter: ', comp_filter_roll)
        # print('after 90, pitch: ', pitch2) 
        print('angular_accelX: ', angular_accelX)
        print('angular_accelY: ', angular_accelY)
        print('angular_accelZ: ', angular_accelZ)

        # print('after 90, roll: ', roll2)


        #     time.sleep(0.5)

ani = FuncAnimation(fig, animate, interval=200)

plt.tight_layout()
plt.show()
    # print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (mpu.acceleration))
    # print("Gyro X:%.2f, Y: %.2f, Z: %.2f degrees/s" % (mpu.gyro))
    # print("Temperature: %.2f C" % mpu.temperature)
    # print("")
    # time.sleep(1)
