import serial;
import time;
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.style.use('ggplot')

#---------------- FUNCION PARA LEER Y GUARDAR VALORES ---------------- 
def cogerValoresyEscribirlos():   
    val = SerialArduino.readline().decode('ascii')
    val = val.rstrip("\r\n")
   # print(val)        
    val += "\r"
    
    with open("datosAcelerometro.csv","a") as f: 
        f.write(val)
    #with open("datosAcelerometro.txt","a") as f: 
        #f.write(val) 


 #---------------- FUNCION PARA PLOTEAR ----------------        
def plotear(i, temp, AcelXmean, AcelYmean, AcelZmean, Anormamean):
    tiempoInicio = time.time()
    tiempoActual = tiempoInicio
    
    file = open("datosAcelerometro.csv","w")
    file.write("AcelX;AcelY;AcelZ;Norma;\r")
    file.close()
    
    while ((tiempoActual - tiempoInicio)< tiempoTomadeDatos):   
        #Nos guardamos los datos durante tiempoTomadeDatos segundos
        cogerValoresyEscribirlos()            
        tiempoActual = time.time()
        
        if ((tiempoActual - tiempoInicio) >= tiempoTomadeDatos):
            #Actualizamos contador que nos sirve para ir iterando las gráficas:
            i=i+1
            #Cargamos los últimos datos en la variable df 
            df = pd.read_csv("datosAcelerometro.csv", sep=';')
            
            #Calculamos medias actualizadas:
            AcelXmean.append(df["AcelX"].mean()); AcelYmean.append(df["AcelY"].mean())
            AcelZmean.append(df["AcelZ"].mean()); Anormamean.append(df["Norma"].mean())
            
            #Calculamos Desviaciones tipicas actualizadas:
            AcelXstd.append(df["AcelX"].std());   AcelYstd.append(df["AcelY"].std())
            AcelZstd.append(df["AcelZ"].std());   Anormastd.append(df["Norma"].std())
            
            #Actualizamos eje X común
            temp.append(tiempoActual-tiempoCero)
            
            #Limpiamos la gráfica anterior para plotear una encima sin problemas:
            ax.clear()
            
            #Ploteamos gráficas:
            ax.plot(temp, AcelXmean, label="Media")
            ax.plot(temp, AcelXstd, label="Desviación típica")
            
            # Format plot
            #plt.xticks(rotation=45, ha='right')
            #plt.subplots_adjust(bottom=0.30)
            plt.title('Aceleración en X', fontsize=12, fontweight='bold')
            plt.ylabel('Valor [g]', fontsize=12, fontweight='bold', color='k')
            plt.xlabel('Tiempo [s]', fontsize=12, fontweight='bold', color='k')
            plt.legend()
            #plt.axis([1, None, 0, 1.1]) #Use for arbitrary number of trials
            #plt.axis([1, 100, 0, 1.1]) #Use for 100 trial demo
        
        
    
    

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

#---------------------- SET-UP DE LAS GRÁFICAS ----------------------------
# Figura:
fig, ax = plt.subplots()
# Inicilizamos las líneas que se plotean:
#   Medias:
AcelXmean = []; AcelYmean = []; AcelZmean = []; Anormamean = []
#   Desviaciones típicas:
AcelXstd  = []; AcelYstd  = []; AcelZstd  = []; Anormastd  = []
# Eje X común (el tiempo)
temp    = []

# Un contador, útil para la gráfica (nos servirá para actualizar temp)
i=0

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

#Capturamos datos durante (tiempoTomadeDatos) segundos:
# fargs = (temp, AcelXmean, AcelYmean, AcelZmean, Anormamean),        
ani = animation.FuncAnimation(fig, plotear, fargs = (temp, AcelXmean, AcelYmean, AcelZmean, Anormamean),  interval=0)
plt.show()
 
#SerialArduino.close()    
