import serial;
import time;

#Definimos el puerto serie:
SerialArduino = serial.Serial('COM3',115200)
#Damos un tiempo (1seg) al puerto para que se conecte:
time.sleep(1)

# PROCESO DE CALIBRACIÓN DEL SENSOR:
    #Avisamos de que mande el mensaje para calibrar

print("\n---------------- CALIBRACION -----------------\n");
print("Para calibrar mandar algo por el Puerto Serie:\n");
print("IMPORTANTE!! Debe estar en reposo\n");
input();
aux = "a"
SerialArduino.write(aux.encode('ascii'))
print("-------------- Sensor calibrado --------------\n");


#COMIENZO DE LA CAPTURA DE DATOS:
while True:
    val = SerialArduino.readline()
    val = val.decode('ascii')
    
    print(val)
    
    
