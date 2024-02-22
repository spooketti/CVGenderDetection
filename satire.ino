#define failLED 5
#define transPin 2
#define winLED 3

//redefine as needed

void setup() {
 Serial.begin(9600);
}

void noGender()
{
  digitalWrite(failLED,LOW);
  analogWrite(transPin,LOW);
  digitalWrite(winLED,LOW);
}

void gender(bool isMale)
{
  if(isMale)
  {
    digitalWrite(winLED,HIGH);
    digitalWrite(failLED,LOW);
    analogWrite(transPin,LOW);
    return;
  }
  digitalWrite(winLED,LOW);
  digitalWrite(failLED,HIGH);
  analogWrite(transPin,150);
  //female

}

void loop() {
 if (Serial.available() > 0) {
    char incomingBytes = Serial.read();
    Serial.println(incomingBytes);

    switch(incomingBytes)
    {
      case 'F':
      gender(false);
      break;

      case 'M':
      gender(true);
      break;

      default:
      noGender();
      break;
    }
}
delay(10);
}
