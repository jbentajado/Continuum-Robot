from mpu6050 import mpu6050
import time
import math
mpu = mpu6050(0x68)

dtTimer = 0
imu_roll = 0
imu_pitch = 0

gyroRoll = 90
gyroPitch = 90
gyroYaw = 90

def complementaryFilter():
    while True:
        accel_data = mpu.get_accel_data()
        # print("Acc X : "+str(accel_data['x']))
        # print("Acc Y : "+str(accel_data['y']))
        # print("Acc Z : "+str(accel_data['z']))
        # print()

        gyro_data = mpu.get_gyro_data()
        # print("Gyro X : "+str(gyro_data['x']))
        # print("Gyro Y : "+str(gyro_data['y']))
        # print("Gyro Z : "+str(gyro_data['z']))
        # print()
        # print("-------------------------------")
        # time.sleep(1)
        
        dt = time.time() - dtTimer
        dtTimer = time.time()
        
        # Accelerometer angle
        accPitch = math.degrees(math.atan2(accel_data['y'], accel_data['z']))
        accRoll = math.degrees(math.atan2(accel_data['x'], accel_data['z']))
        
        # Gyroscope integration angle
        gyroRoll -= gyro_data['y']*dt 
        gyroPitch += gyro_data['x']*dt
        gyroYaw += gyro_data['z']*dt
        yaw = gyroYaw 
        
        # Complementary Filter - about IMU axes
        tau = 0.98
        imu_roll = (tau)*(imu_roll + gyro_data['y']*dt) + (1-tau)*(accRoll)
        imu_pitch = (tau)*(imu_pitch + gyro_data['x']*dt) + (1-tau)*(accPitch)
        
        cbot_yaw = imu_pitch
        cbot_pitch = imu_roll
        
        print(" R: " \
                    + "Robot P: " + str(round(cbot_pitch,1)) \
                    + "Robot Y: " + str(round(cbot_yaw,1)))
    

