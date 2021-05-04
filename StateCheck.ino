float DCMotorPosition1 = 0.0;
float DCMotorPosition2 = 0.0;

float JevoisXaxis = 0.0;
float JevoisYaxis = 0.0;

String StrDCMotorPosition1;
String StrDCMotorPosition2;

String StrJevoisXaxis;
String StrJevoisYaxis;

boolean ManualEntryMode = false;
boolean JoystickMode = false;
boolean JevoisMode = false;
boolean PatternMode = false;
boolean MotorPositionCondition1 = false;
boolean MotorPositionCondition2 = false;
boolean JevoisConditionX = false;
boolean JevoisConditionY = false;



boolean newData = false;
char startMarker = '<';
char endMarker = '>';
const byte numChars = 32;
char receivedChars[numChars];
char rc;
static byte index = 0;

void setup() {
  Serial.begin(115200);

}

void loop() {
  recvWithStartEndMarkers();
  F_CheckSerialProtocol();
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
void F_CheckSerialProtocol()
{
  if (newData == true)
  {
    if (receivedChars[0] == 'M' && receivedChars[1] == 'M' && receivedChars[2] == '1') 
    {
      ManualEntryMode = true;//Manual Entry On
      Serial.println("MM1");
    }
    else if (receivedChars[0] == 'M' && receivedChars[1] == 'M' && receivedChars[2] == '0')
    {
      ManualEntryMode = false;//Manual Entry OFF
      Serial.println("MM0");
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'S' && receivedChars[2] == 'M' && receivedChars[3] == '1')
    {
      JoystickMode = true; //Joystick On
      Serial.println("JSM1");
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'S' && receivedChars[2] == 'M' && receivedChars[3] == '0')
    {
      JoystickMode = false; //Joystick Off
      Serial.println("JSM0");
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'M' && receivedChars[2] == '1') 
    {
      JevoisMode = true;//jEVOIS On
      Serial.println("JM1");
    }
    else if (receivedChars[0] == 'J' && receivedChars[1] == 'M' && receivedChars[2] == '0')
    {
      JevoisMode = false;//JEVOIS OFF
      Serial.println("JM0");
    }
    else if (receivedChars[0] == 'P' && receivedChars[1] == 'M' && receivedChars[2] == '1') 
    {
      PatternMode = true;//Pattern On
      Serial.println("PM1");
    }
    else if (receivedChars[0] == 'P' && receivedChars[1] == 'M' && receivedChars[2] == '0')
    {
      PatternMode = false;//Pattern OFF
      Serial.println("PM0");
    }
    else if (ManualEntryMode == true && receivedChars[0] == '1' && receivedChars[1] == 'p')
    {
      StrDCMotorPosition1 = receivedChars;
      StrDCMotorPosition1.remove(0, 2);
      DCMotorPosition1 = StrDCMotorPosition1.toInt();
      MotorPositionCondition1 = true;
    }
    else if (ManualEntryMode == true && receivedChars[0] == '2' && receivedChars[1] == 'p')
    {
      StrDCMotorPosition2 = receivedChars;
      StrDCMotorPosition2.remove(0, 2);
      DCMotorPosition2 = StrDCMotorPosition2.toInt();
      MotorPositionCondition2 = true;
    }
    else if (JevoisMode == true && receivedChars[0] == 'J' && receivedChars[1] == 'x')
    {
      StrJevoisXaxis = receivedChars;
      StrJevoisXaxis.remove(0, 2);
      JevoisXaxis = StrJevoisXaxis.toInt();
      //Serial.print(JevoisXaxis);
      JevoisConditionX = true;
    }
    else if (JevoisMode == true && receivedChars[0] == 'J' && receivedChars[1] == 'y')
    {
      StrJevoisYaxis = receivedChars;
      StrJevoisYaxis.remove(0, 2);
      JevoisYaxis = StrJevoisYaxis.toInt();
      //Serial.println(JevoisYaxis);
      JevoisConditionY = true;
    }
    
    newData = false;
  }

}
