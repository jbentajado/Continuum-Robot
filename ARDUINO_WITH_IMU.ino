// ---------------------- Revisions --------------------------------------
// Revision 1: Preliminary Version. Code is taken from DCMotorControlPID.ino ver 4. Uses Jevois camera feedback instead of encoders.
//
// ----------------------------------------------------------------------
#include <Wire.h>
#define IN1 21 //DC motor 1
#define IN2 20 //DC motor 1
#define PWM1 11 //DC motor 1 speed

#define IN3 19 //DC motor 2
#define IN4 18 //DC motor 2
#define PWM2 10 // DC motor 2 speed

#define ENCA1 7 //interrupt pin
#define ENCB1 1
#define ENCA2 0 //interrupt pin
#define ENCB2 17

#define JOYSTICK_X A0
#define JOYSTICK_Y A1

int JoyPosition_X = 0;
int JoyPosition_Y = 0;

int pos1 = 0; // This would be the y axis
int pos2 = 0; // This would be the x axis
long prevTime1 = 0;
long prevTime2 = 0;
long prevTime3 = 0;
float eprev1 = 0;
float eprev2 = 0;
float eprev3 = 0;
float eintegral1 = 0;
float eintegral2 = 0;
float etinegral3 = 0;

boolean newData = false;
char startMarker = '<';
char endMarker = '>';
const byte numChars = 32;
char receivedChars[numChars];
char rc;
static byte index = 0;

int16_t Acc_rawX, Acc_rawY, Acc_rawZ,Gyr_rawX, Gyr_rawY, Gyr_rawZ;
float Acceleration_angle[2];
float Gyro_angle[2];
float Total_angle[2];
float elapsedTime, time, timePrev;
int i;
float rad_to_deg = 180/3.141592654;
double throttle=255; //initial value of throttle to the motors
float desired_angle = 0; //This is the angle in which we whant the
                         //balance to stay steady
// ----------------------------------------------- DC MOTOR-RELATED VARIABLES --------------------------------------------------------
float DCMotorPosition1 = 0.0;
float DCMotorPosition2 = 0.0;

float JevoisXaxis = 0.0;
float JevoisYaxis = 0.0;

String StrDCMotorPosition1;
String StrDCMotorPosition2;

String StrJevoisXaxis;
String StrJevoisYaxis;

boolean MotorPositionCondition1 = false;
boolean MotorPositionCondition2 = false;
boolean JevoisConditionX = false;
boolean JevoisConditionY = false;
boolean JoyStickMode = false;
// -----------------------------------------------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  Wire.begin(); //begin the wire comunication
  Wire.beginTransmission(0x68);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
  Serial.begin(250000);
  pinMode(ENCA1, INPUT);
  pinMode(ENCB1, INPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(PWM1, OUTPUT);
  pinMode(ENCA2, INPUT);
  pinMode(ENCB2, INPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(PWM2, OUTPUT);

  pinMode(JOYSTICK_X, INPUT);
  pinMode(JOYSTICK_Y, INPUT);

  attachInterrupt(digitalPinToInterrupt(ENCA1), readEncoder1, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCB1), readEncoder1, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCA2), readEncoder2, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCB2), readEncoder2, RISING);
  time = millis(); //Start counting time in milliseconds
  delay(7000);
}


void loop()
{
  recvWithStartEndMarkers();
  F_CheckSerialProtocol();

    timePrev = time;  // the previous time is stored before the actual time read
    time = millis();  // actual time read
    elapsedTime = (time - timePrev) / 1000; 
  
  /*The tiemStep is the time that elapsed since the previous loop. 
   * This is the value that we will use in the formulas as "elapsedTime" 
   * in seconds. We work in ms so we haveto divide the value by 1000 
   to obtain seconds*/

  /*Reed the values that the accelerometre gives.
   * We know that the slave adress for this IMU is 0x68 in
   * hexadecimal. For that in the RequestFrom and the 
   * begin functions we have to put this value.*/
   
     Wire.beginTransmission(0x68);
     Wire.write(0x3B); //Ask for the 0x3B register- correspond to AcX
     Wire.endTransmission(false);
     Wire.requestFrom(0x68,6,true); 
   
   /*We have asked for the 0x3B register. The IMU will send a brust of register.
    * The amount of register to read is specify in the requestFrom function.
    * In this case we request 6 registers. Each value of acceleration is made out of
    * two 8bits registers, low values and high values. For that we request the 6 of them  
    * and just make then sum of each pair. For that we shift to the left the high values 
    * register (<<) and make an or (|) operation to add the low values.*/
    
     Acc_rawX=Wire.read()<<8|Wire.read(); //each value needs two registres
     Acc_rawY=Wire.read()<<8|Wire.read();
     Acc_rawZ=Wire.read()<<8|Wire.read();

 
    /*///This is the part where you need to calculate the angles using Euler equations///*/
    
    /* - Now, to obtain the values of acceleration in "g" units we first have to divide the raw   
     * values that we have just read by 16384.0 because that is the value that the MPU6050 
     * datasheet gives us.*/
    /* - Next we have to calculate the radian to degree value by dividing 180º by the PI number
    * which is 3.141592654 and store this value in the rad_to_deg variable. In order to not have
    * to calculate this value in each loop we have done that just once before the setup void.
    */

    /* Now we can apply the Euler formula. The atan will calculate the arctangent. The
     *  pow(a,b) will elevate the a value to the b power. And finnaly sqrt function
     *  will calculate the rooth square.*/
     /*---X---*/
     Acceleration_angle[0] = atan((Acc_rawY/16384.0)/sqrt(pow((Acc_rawX/16384.0),2) + pow((Acc_rawZ/16384.0),2)))*rad_to_deg;
     /*---Y---*/
     Acceleration_angle[1] = atan(-1*(Acc_rawX/16384.0)/sqrt(pow((Acc_rawY/16384.0),2) + pow((Acc_rawZ/16384.0),2)))*rad_to_deg;
 
   /*Now we read the Gyro data in the same way as the Acc data. The adress for the
    * gyro data starts at 0x43. We can see this adresses if we look at the register map
    * of the MPU6050. In this case we request just 4 values. W don¡t want the gyro for 
    * the Z axis (YAW).*/
    
   Wire.beginTransmission(0x68);
   Wire.write(0x43); //Gyro data first adress
   Wire.endTransmission(false);
   Wire.requestFrom(0x68,4,true); //Just 4 registers
   
   Gyr_rawX=Wire.read()<<8|Wire.read(); //Once again we shif and sum
   Gyr_rawY=Wire.read()<<8|Wire.read();
 
   /*Now in order to obtain the gyro data in degrees/seconda we have to divide first
   the raw value by 131 because that's the value that the datasheet gives us*/

   /*---X---*/
   Gyro_angle[0] = Gyr_rawX/131.0; 
   /*---Y---*/
   Gyro_angle[1] = Gyr_rawY/131.0;

   /*Now in order to obtain degrees we have to multiply the degree/seconds
   *value by the elapsedTime.*/
   /*Finnaly we can apply the final filter where we add the acceleration
   *part that afects the angles and ofcourse multiply by 0.98 */

   /*---X axis angle---*/
   Total_angle[0] = 0.98 *(Total_angle[0] + Gyro_angle[0]*elapsedTime) + 0.02*Acceleration_angle[0];
   /*---Y axis angle---*/
   Total_angle[1] = 0.98 *(Total_angle[1] + Gyro_angle[1]*elapsedTime) + 0.02*Acceleration_angle[1];
   
   /*Now we have our angles in degree and values from -10º0 to 100º aprox*/
    //Serial.println(Total_angle[1]);
    
    int target1 = 0;
    int target2 = 0;

    //PID GAINS FOR MOTOR 1
    float kp1 = 167.5;
    float kd1 = 1.25;
    float ki1 = 0;

    //PID GAINS FOR MOTOR 2
    float kp2 = 167.5;
    float kd2 = 1.25;
    float ki2 = 0;

    // TIME DIFFERENCE -----------------------------------------------
    long currTime1 = micros();
    long currTime2 = micros();
    float deltaT1 = ((float) (currTime1 - prevTime1)) / ( 1.0e6 );
    float deltaT2 = ((float) (currTime2 - prevTime2)) / ( 1.0e6 );
    prevTime1 = currTime1;
    prevTime2 = currTime2;
    // ERROR ---------------------------------------------------------
    int e1 = Total_angle[0] - target1;
    int e2 = Total_angle[0] - target2;
    // DERIVATIVE ----------------------------------------------------
    float dedt1 = (e1 - eprev1) / (deltaT1);
    float dedt2 = (e2 - eprev2) / (deltaT2);
    // INTEGRAL ------------------------------------------------------
    eintegral1 = eintegral1 + e1 * deltaT1;
    eintegral2 = eintegral2 + e2 * deltaT2;
    // CONTROL SIGNAL EQUATION ---------------------------------------
    float u1 = kp1 * e1 + kd1 * dedt1 + ki1 * eintegral1;
    float u2 = kp2 * e2 + kd2 * dedt2 + ki2 * eintegral2;
    // MOTOR SPEED ---------------------------------------------------
    float pwr1 = fabs(u1); //fab takes a single argument (in double) and returns the absolute value of that number.
    float pwr2 = fabs(u2);
    if ( pwr1 > 255 ) {
      pwr1 = 255;
    }
    if ( pwr2 > 255 ) {
      pwr2 = 255;
    }
    // MOTOR DIRECTION -----------------------------------------------
    int dir1 = 1;
    int dir2 = 1;
    if (u1 < 0) //if the control signal is negative, change the direction of the motors
    {
      dir1 = -1;
  
    }
    if (u2 < 0)
    {
      dir2 = -1;
  
    }
    // ASSIGN SIGNAL TO MOTORS ---------------------------------------
    setMotor1(dir1, pwr1, PWM1, IN1, IN2);
    setMotor2(dir2, pwr2, PWM2, IN3, IN4);
    // STORE PREVIOUS ERROR ------------------------------------------
    eprev1 = e1;
    eprev2 = e2;

}
// -------------------------------- Serial Interface ----------------------------------------------
void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void showNewData() {
  if (newData == true) {
    Serial.println(receivedChars);
  }
}

void F_RunDCPID()
{
  if (MotorPositionCondition1 == true && MotorPositionCondition2 == true)
  {
    // set target position
    int target1 = DCMotorPosition1;
    int target2 = DCMotorPosition2;

    //PID GAINS FOR MOTOR 1
    float kp1 = 167.5;
    float kd1 = 1.25;
    float ki1 = 0;

    //PID GAINS FOR MOTOR 2
    float kp2 = 167.5;
    float kd2 = 1.25;
    float ki2 = 0;

    // TIME DIFFERENCE -----------------------------------------------
    long currTime1 = micros();
    long currTime2 = micros();
    float deltaT1 = ((float) (currTime1 - prevTime1)) / ( 1.0e6 );
    float deltaT2 = ((float) (currTime2 - prevTime2)) / ( 1.0e6 );
    prevTime1 = currTime1;
    prevTime2 = currTime2;
    // ERROR ---------------------------------------------------------
    int e1 = pos1 - target1;
    int e2 = pos2 - target2;
    // DERIVATIVE ----------------------------------------------------
    float dedt1 = (e1 - eprev1) / (deltaT1);
    float dedt2 = (e2 - eprev2) / (deltaT2);
    // INTEGRAL ------------------------------------------------------
    eintegral1 = eintegral1 + e1 * deltaT1;
    eintegral2 = eintegral2 + e2 * deltaT2;
    // CONTROL SIGNAL EQUATION ---------------------------------------
    float u1 = kp1 * e1 + kd1 * dedt1 + ki1 * eintegral1;
    float u2 = kp2 * e2 + kd2 * dedt2 + ki2 * eintegral2;
    // MOTOR SPEED ---------------------------------------------------
    float pwr1 = fabs(u1); //fab takes a single argument (in double) and returns the absolute value of that number.
    float pwr2 = fabs(u2);
    if ( pwr1 > 255 ) {
      pwr1 = 255;
    }
    if ( pwr2 > 255 ) {
      pwr2 = 255;
    }
    // MOTOR DIRECTION -----------------------------------------------
    int dir1 = 1;
    int dir2 = 1;
    if (u1 < 0) //if the control signal is negative, change the direction of the motors
    {
      dir1 = -1;
    }
    if (u2 < 0)
    {
      dir2 = -1;
    }
    // ASSIGN SIGNAL TO MOTORS ---------------------------------------
    setMotor1(dir1, pwr1, PWM1, IN1, IN2);
    setMotor2(dir2, pwr2, PWM2, IN3, IN4);
    // STORE PREVIOUS ERROR ------------------------------------------
    eprev1 = e1;
    eprev2 = e2;

    Serial.print(target1); Serial.print(" "); Serial.print(target2); Serial.print(" "); Serial.print(pos1); Serial.print(" "); Serial.print(pos2); Serial.println();
  }

}

void setMotor1(int dir1, int pwmVal1, int pwm1, int in1, int in2)
{
  analogWrite(pwm1, pwmVal1);
  if (dir1 == 1)
  {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  }
  else if (dir1 == -1)
  {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  }
  else {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
  }
}

void setMotor2(int dir2, int pwmVal2, int pwm2, int in3, int in4) {
  analogWrite(pwm2, pwmVal2);
  if (dir2 == 1)
  {
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
  }
  else if (dir2 == -1)
  {
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);
  }
  else
  {
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
  }
}

void readEncoder1()
{
  int b1 = digitalRead(ENCA1);
  if (b1 > 0)
  {
    pos1++;
  }
  else
  {
    pos1--;
  }
}
void readEncoder2()
{
  int b2 = digitalRead(ENCA2);
  if (b2 > 0)
  {
    pos2++;
  }
  else
  {
    pos2--;
  }
}



void F_CheckSerialProtocol()
{
  if (newData == true)
  {
    if (receivedChars[0] == '1' && receivedChars[1] == 'p')
    {
      StrDCMotorPosition1 = receivedChars;
      StrDCMotorPosition1.remove(0, 2);
      DCMotorPosition1 = StrDCMotorPosition1.toInt();
      MotorPositionCondition1 = true;
    }
    else if (receivedChars[0] == '2' && receivedChars[1] == 'p')
    {
      StrDCMotorPosition2 = receivedChars;
      StrDCMotorPosition2.remove(0, 2);
      DCMotorPosition2 = StrDCMotorPosition2.toInt();
      MotorPositionCondition2 = true;
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'x')
    {
      StrJevoisXaxis = receivedChars;
      StrJevoisXaxis.remove(0, 2);
      JevoisXaxis = StrJevoisXaxis.toInt();
      //Serial.print(JevoisXaxis);
      JevoisConditionX = true;
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'y')
    {
      StrJevoisYaxis = receivedChars;
      StrJevoisYaxis.remove(0, 2);
      JevoisYaxis = StrJevoisYaxis.toInt();
      //Serial.println(JevoisYaxis);
      JevoisConditionY = true;
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'S' && receivedChars[2] == 'O')
    {
      JoyStickMode = true; //Joystick On
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'S' && receivedChars[2] == 'F')
    {
      JoyStickMode = false; //Joystick On
    }
    newData = false;
  }

}
