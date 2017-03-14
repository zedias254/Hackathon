#include <EmonLib.h>
#include "EmonLib.h"

EnergyMonitor emon1;
double Irms = 0;
int pin_current = A1;
char string=1;
int relaypin = 3; 

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  //http://blog.filipeflop.com/sensores/medidor-de-corrente-sct013-com-arduino.html
  //Pino, calibracao - Cur Const= Ratio/BurdenR. 2000/33 = 60
  emon1.current(pin_current, 29);
  pinMode(relaypin, OUTPUT);
  digitalWrite(relaypin,HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
  Irms = emon1.calcIrms(1480);
  Serial.println(Irms);
  //int readval = analogRead(pin_current);
  //Serial.println(readval);
  if (Serial.available() > 0) {
        // read the incoming byte:
        string = Serial.read();
        if(string == '1'){
          digitalWrite(relaypin,LOW);
        }else{
          digitalWrite(relaypin,HIGH);
        }
  }

  delay(500); 

}
