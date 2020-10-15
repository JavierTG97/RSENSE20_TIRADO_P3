#include <MPU9250_asukiaaa.h>

//LED:
const int ledPIN = 17;

// IMU:
#ifdef _ESP32_HAL_I2C_H_
#define SDA_PIN 21
#define SCL_PIN 22
#endif

MPU9250_asukiaaa mySensor;
float aX, aY, aZ, aSqrt, gX, gY, gZ, mDirection, mX, mY, mZ;
float offsetX, offsetY, offsetZ, modulo2;
float aXtotal = 0.0, aYtotal = 0.0, aZtotal = 0.0;

//INTERRUPCION:
//Variable para detectar interrupción, y contador:
volatile int interruptCounter;
int cont = 0;

//Creamos un puntero que represente a un timer 
hw_timer_t * timer = NULL;

//Creamos una variable de tipo portMUX_type que nos permita sincronizar la variable volatile
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

//Interrupcion:
void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);
  interruptCounter++;
  portEXIT_CRITICAL_ISR(&timerMux); 
}

void setup() {
  Serial.begin(115200);
  //while(!Serial);
  delay(1000); //Para que le de tiempo al puerto serie a abrirse

  // SET-UP del IMU:
  #ifdef _ESP32_HAL_I2C_H_ // For ESP32
    Wire.begin(SDA_PIN, SCL_PIN);
    mySensor.setWire(&Wire);
  #endif

  mySensor.beginAccel();

  //Esperamos a que el usuario indique que se inicie la calibración:
  while (!Serial.available()){
  }
  //Esperamos a que se haya transmitido el mensaje y no queden caracteres por tanto en el buffer:
  while(Serial.available() > 0) {
    char t = Serial.read();
  }

  if (mySensor.accelUpdate() == 0) {
    offsetX = mySensor.accelX();
    offsetY = mySensor.accelY();
    aZ = mySensor.accelZ();
  } else {
    Serial.println("Cannot read accel values");
  }

  //En la siguiente líne asumimos que el oofset en el eje Z NO es suficiente como para cambiar el signo en la medición:
  if (aZ > 0){
    offsetZ = aZ - 1.0;
  }
  else {
    offsetZ = aZ + 1.0;
  }

  //Esperamos a que el usuario indique que se inicie la captura de datos:
  while (!Serial.available()){
  }

  // SET-UP del timer:
  timer = timerBegin(0, 80, true); //Por orden: asociamos el timer al canal 0, prescaler de 80 -> freq=80/80=1 MHz, y el conteo es en sentido ascendente.
  timerAttachInterrupt(timer, &onTimer, true); //Asignamos el timer a la interrip. onTimer, y la interrupción se genera tras producirse el flanco de timer correspondiente. 
  timerAlarmWrite(timer, 200000, true); //Interrupcion = 200.000 conteos (200 ms) e indicamos que cada vez que llegue a ese valor, el conteo se renueve.
  timerAlarmEnable(timer); //activamos la interrupción.

  // SET-UP del LED:
  pinMode(ledPIN , OUTPUT);

  portENTER_CRITICAL(&timerMux);
  interruptCounter=0;
  portEXIT_CRITICAL(&timerMux);
  
}

void loop() {

  //LEEMOS sensor si han pasado 200 ms:
  if (interruptCounter > 0) {

    //Inicializamos de nuevo la variable, para detectar de nuevo la itnerrupción en el if
    portENTER_CRITICAL(&timerMux);
    interruptCounter--;
    portEXIT_CRITICAL(&timerMux);

    //Actualizamos el contador (para ver si hemos llegado al segundo):
    ++cont;
    
    //Leemos address del sensor, en caso de que quisieramos lo podemos sacar tambien por la UART:
    /*
    uint8_t sensorId;
    if (mySensor.readId(&sensorId) == 0) {
      Serial.println("sensorId: " + String(sensorId));
    } 
    else {
      Serial.println("Cannot read sensorId");
    }*/

    //Leemos aceleraciones y actualizamos los sumatorios:
    if (mySensor.accelUpdate() == 0) {
      aX = mySensor.accelX(); 
      aXtotal = aXtotal + aX - offsetX;
      
      aY = mySensor.accelY(); 
      aYtotal = aYtotal + aY - offsetY;
      
      aZ = mySensor.accelZ(); 
      aZtotal = aZtotal + aZ - offsetZ;
      //aSqrt = mySensor.accelSqrt();
    } 
    else {
      Serial.println("Cannot read accel values");
    }    

    if (cont == 1){
      digitalWrite(ledPIN , LOW);
    }
    
    //Si ha pasado 1 segundo, enviamos la media de las acelarciones durante ese segundo
    if (cont==5) {
      Serial.print(aXtotal/5);
      Serial.print(";");
      Serial.print(aYtotal/5);
      Serial.print(";");
      Serial.print(aZtotal/5);
      Serial.print(";");
      
      //Calculamos tambien el modulo de la aceleracion:      
      modulo2 = aXtotal*aXtotal/25 + aYtotal*aYtotal/25 + aZtotal*aZtotal/25;
      Serial.println(sqrt(modulo2));

      //encendemos el LED:
      digitalWrite(ledPIN , HIGH);
      
      //Serial.println("");
      aXtotal = 0.0;  aYtotal = 0.0; aZtotal = 0.0;
      cont=0;
    }
  }
  
}
