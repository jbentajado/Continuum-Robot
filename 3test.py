import smbus
import math
import time


class MPU:
    def __init__(self, gyro, acc, tau):
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

        self.gyroXcal = -331.7
        self.gyroYcal = -339.4
        self.gyroZcal = -206.0

        self.accScaleFactor = 16384.0
        self.gyroScaleFactor = 131.0
        
        self.accHex = 0
        self.gyroHex = 0

        # self.gyroScaleFactor, self.gyroHex = self.gyroSensitivity(gyro)
        # self.accScaleFactor, self.accHex = self.accelerometerSensitivity(acc)

        self.bus = smbus.SMBus(1)
        self.address = 0x68
        
    def eightBit2sixteenBit(self, reg):
        # Reads high and low 8 bit values and shifts them into 16 bit
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg+1)
        val = (h << 8) + l

        # Make 16 bit unsigned value to signed value (0 to 65535) to (-32768 to +32767)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val
        
    def getRawData(self):
        self.gx = self.eightBit2sixteenBit(0x43)
        self.gy = self.eightBit2sixteenBit(0x45)
        self.gz = self.eightBit2sixteenBit(0x47)

        self.ax = self.eightBit2sixteenBit(0x3B)
        self.ay = self.eightBit2sixteenBit(0x3D)
        self.az = self.eightBit2sixteenBit(0x3F)
        
    def processIMUvalues(self):
        # Update the raw data
        self.getRawData()
        print("print gx gy gz:")
        print("\tgx: " + str(round(self.gx,1)))
        print("\tgy: " + str(round(self.gy,1)))
        print("\tgz: " + str(round(self.gz,1)))

        # Subtract the offset calibration values
        self.gx -= self.gyroXcal
        self.gy -= self.gyroYcal
        self.gz -= self.gyroZcal

        # Convert to instantaneous degrees per second
        self.gx /= self.gyroScaleFactor
        self.gy /= self.gyroScaleFactor
        self.gz /= self.gyroScaleFactor
        

        # Convert to g force
        self.ax /= self.accScaleFactor
        self.ay /= self.accScaleFactor
        self.az /= self.accScaleFactor

        
    def compFilter(self):
        # Get the processed values from IMU
        self.processIMUvalues()

        # Get delta time and record time for next call
        dt = time.time() - self.dtTimer
        self.dtTimer = time.time()

        # Acceleration vector angle
        accPitch = math.degrees(math.atan2(self.ay, self.az))
        accRoll = math.degrees(math.atan2(self.ax, self.az))

        # Gyro integration angle
        self.gyroRoll -= self.gy * dt # y
        self.gyroPitch += self.gx * dt # x
        self.gyroYaw += self.gz * dt
        self.yaw = self.gyroYaw
        
        # Comp filter
        self.roll = (self.tau)*(self.roll - self.gy*dt) + (1-self.tau)*(accRoll)
        self.pitch = (self.tau)*(self.pitch + self.gx*dt) + (1-self.tau)*(accPitch)

        # Print data
        
        print(self.gyroRoll)
        print(self.gyroPitch)
        
        print(" R: " + str(round(self.roll,1)) \
            + " P: " + str(round(self.pitch,1)) \
            + " Y: " + str(round(self.yaw,1)))
        
def main():
    # # Set up class
    gyro = 250      # 250, 500, 1000, 2000 [deg/s]
    acc = 2         # 2, 4, 7, 16 [g]
    tau = 0.98
    mpu = MPU(gyro, acc, tau)

    # Set up sensor and calibrate gyro with N points
    # mpu.setUp()
    # mpu.calibrateGyro(500)

    # Run for 20 secounds
    startTime = time.time()
    while(time.time() < (startTime + 20)):
        mpu.compFilter()

    # End
    print("Closing")

# Main loop
if __name__ == '__main__':
	main()