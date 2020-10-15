import serial;
import time;
import numpy as np
import matplotlib.pyplot as plt
from drawnow import *

plt.style.use('ggplot')

# --------------- FUNCION PARA CREAR LAS FIGURAS ---------------------

def FigsAceleraciones():
    plt.subplot(2,2,1)
    plt.ylim(-2,2)
    plt.title('Aceleración en X', fontsize=12, fontweight='bold', color='k')
    plt.ylabel('Valor [g]', fontsize=12, fontweight='bold', color='k')
    plt.xlabel('Tiempo [s]', fontsize=12, fontweight='bold', color='k')
    plt.plot(temp, AcelXmean, label = 'media')
    plt.plot(temp, AcelXstd, label = 'desv. est.')
    plt.legend()
    
    plt.subplot(2,2,2)
    plt.ylim(-2,2)
    plt.title('Aceleración en Y', fontsize=12, fontweight='bold', color='k')
    plt.ylabel('Valor [g]', fontsize=12, fontweight='bold', color='k')
    plt.xlabel('Tiempo [s]', fontsize=12, fontweight='bold', color='k')
    plt.plot(temp, AcelYmean, label = 'media')
    plt.plot(temp, AcelYstd, label = 'desv. est.')
    plt.legend()
    
    plt.subplot(2,2,3)
    plt.ylim(-2,2)
    plt.title('Aceleración en Z', fontsize=12, fontweight='bold', color='k')
    plt.ylabel('Valor [g]', fontsize=12, fontweight='bold', color='k')
    plt.xlabel('Tiempo [s]', fontsize=12, fontweight='bold', color='k')
    plt.plot(temp, AcelZmean, label = 'media')
    plt.plot(temp, AcelZstd, label = 'desv. est.')
    plt.legend()
    
    plt.subplot(2,2,4)
    plt.ylim(-2,2)
    plt.title('Norma de la aceleración', fontsize=12, fontweight='bold', color='k')
    plt.ylabel('Valor [g]', fontsize=12, fontweight='bold', color='k')
    plt.xlabel('Tiempo [s]', fontsize=12, fontweight='bold', color='k')
    plt.plot(temp, Anormamean, label = 'media')
    plt.plot(temp, Anormastd, label = 'desv. est.')
    plt.legend()
    
#------------------- DECLARACION DEL PUERTO SERIE -------------------        
#Definimos el puerto serie:
try:
    SerialArduino = serial.Serial('COM3',115200)
except:
    print('No se ha podido conectar al puerto serie')
    
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

#---------------------- SET-UP DE LAS GRÁFICAS ----------------------------
# Curva definida por nuestros datos a lo largo del tiempo:
AcelX     = []
AcelXmean = []
AcelXstd  = []

AcelY     = []
AcelYmean = []
AcelYstd  = []

AcelZ     = []
AcelZmean = []
AcelZstd  = []

Anorma     = []
Anormamean = []
Anormastd  = []

# Eje X común (el tiempo)
temp = []

# Borramos los contenidos del fichero de texto (si es que había contenidos)
# y añadimos encabezados:
file = open("datosAcelerometro.csv","w")
#file.write("AcelX;AcelY;AcelZ;Norma\r")
file.close()
file = open("datosAcelerometro.txt","w")
#file.write("AcelX;AcelY;AcelZ;Norma\r")
file.close()

# Quitamos los contenidos del buffer del puerto Serie, para que por ejemplo no
# no guarde el mensaje de reset del propio ESP32
SerialArduino.reset_input_buffer()

#Tiempos de referencia:
tiempoCero = time.time()
tiempoTomadeDatos = 5.0 #segundos

while True:
     while (SerialArduino.inWaiting()==0): #Espera aquí hasta que lleguen datos
         pass #pass -> una vez que llegan datos, continua al código de debajo
     
     #Variables para controlar el tiempo de recogida de datos:
     tiempoInicio = time.time()
     tiempoActual = tiempoInicio
     while (tiempoTomadeDatos >= (tiempoActual - tiempoInicio)):
         val = SerialArduino.readline().decode('ascii')
         
         #Descomponemos la info del sensor en cada una de las variables
         data = val.split(';')
         AcelX.append(data[0])
         AcelY.append(data[1])
         AcelZ.append(data[2])
         Anorma.append(data[3])        
         
         #Si queremos escribir un CSV o TXT:
         val2 = val.rstrip("\r\n")
         with open("datosAcelerometro.csv","a") as f: 
            f.write(val2)
        #with open("datosAcelerometro.txt","a") as f: 
            #f.write(val)
         
         #Actualizamos tiempo:
         tiempoActual = time.time()
     
     # Procesamos los datos:
     #  1) los pasamos a numpy arrays
     #  2) extraemos la media y desv. tip.
     npAX = np.array(AcelX).astype(np.float)
     npAY = np.array(AcelY).astype(np.float)
     npAZ = np.array(AcelZ).astype(np.float)
     npAN = np.array(Anorma).astype(np.float)
     
     AcelX = []; AcelY = []; AcelZ = []; Anorma = []
     
     AcelXmean.append(npAX.mean()); AcelXstd.append(npAX.std())
     AcelYmean.append(npAY.mean()); AcelYstd.append(npAY.std())
     AcelZmean.append(npAZ.mean()); AcelZstd.append(npAZ.std())
     Anormamean.append(npAN.mean()); Anormastd.append(npAN.std())
     
     temp.append(tiempoActual - tiempoCero)
     
     drawnow(FigsAceleraciones) 
     
SerialArduino.close()    
