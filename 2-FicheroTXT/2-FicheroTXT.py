import serial;
import time;
import pandas as pd


#---------------- FUNCION PARA LEER Y GUARDAR VALORES ---------------- 
def cogerValoresyEscribirlos():   
    val = SerialArduino.readline().decode('ascii')
    val = val.rstrip("\r\n")
    print(val)        
    val += "\r"
    
    with open("datosAcelerometro.csv","a") as f: 
        f.write(val)
    with open("datosAcelerometro.txt","a") as f: 
        f.write(val)        


#------------------- DECLARACION DEL PUERTO SERIE -------------------        
#Definimos el puerto serie:
SerialArduino = serial.Serial('COM3',115200)
#Damos un tiempo (1seg) al puerto para que se conecte:
time.sleep(1)

#------------------- PROCESO DE CALIBRACION DEL SENSOR ------------------- 
aux = "a"
print("\n-------------- CALIBRACION --------------\n")
print("Para calibrar mandar algo por el Puerto Serie:\n")
print("IMPORTANTE!! Debe estar en reposo\n")
input()
SerialArduino.write(aux.encode('ascii'))
print("-------------- Sensor calibrado --------------\n")


#---------------- COMIENZO DE LA CAPTURA DE DATOS --------------------------

#Por si acaso tenemos que dejar un tiempo entre la calibracion y la captura de
#los datos, le dejamos al usuario que lo indique por la consola cuando quiere
#empezar a capturar datos:
input("Manda algo por la consola si quieres empezar a tomar datos\n\n")
SerialArduino.write(aux.encode('ascii'))

#Tiempos de referencia:
tiempoInicio = time.time()
tiempoActual = tiempoInicio
tiempoTomadeDatos = 5.0 #segundos

# Borramos los contenidos del fichero de texto (si es que había contenidos)
# y añadimos encabezados:
file = open("datosAcelerometro.csv","w")
file.write("AcelX;AcelY;AcelZ;Norma\r")
file.close()
file = open("datosAcelerometro.txt","w")
file.write("AcelX;AcelY;AcelZ;Norma\r")
file.close()

# Quitamos los contenidos del buffer del puerto Serie, para que por ejemplo no
# no guarde el mensaje de reset del propio ESP32
SerialArduino.reset_input_buffer()

#Capturamos datos durante (tiempoTomadeDatos) segundos:
while ((tiempoActual - tiempoInicio)< tiempoTomadeDatos):
    
    cogerValoresyEscribirlos()    
        
    tiempoActual = time.time()

 
SerialArduino.close()    
