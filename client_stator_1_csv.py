import socket
import time
import sys
import threading
import json
import numpy as np
import Adafruit_ADS1x15
import RPi.GPIO as GPIO
i=0
global c_flag
c_flag=True
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#GPIO ports to control the magnets, set them as output information
GPIO.setup(14,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)


#Establish the magnets right and left for both directions
magnet1r =GPIO.PWM(14,10000)
magnet1r.start(0)
magnet1l =GPIO.PWM(15,10000)
magnet1l.start(0)
magnet2r =GPIO.PWM(17,10000)
magnet2r.start(0)
magnet2l =GPIO.PWM(27,10000)
magnet2l.start(0)




# create a socket object
client_stator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# create an adc object
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

# get local machine name
host = sys.argv[1]                         
port = 9999
time.sleep(1)
# connection to hostname on the port.
client_stator.connect((host, port))                               

# Receive no more than 1024 bytes..
def threaded_client():
    global c_flag
    cl_vector_s=[-1]*4
    values = [0]*3
    data_actuators_s=[0]*4
    for i in range(3):
                values[i] =adc.read_adc(i, gain=GAIN,data_rate=860)
    data = json.dumps({"adc_values_s_cal": values})
    client_stator.send(data.encode())
    data_act_s = client_rotor.recv(1024) 
    actuation_s = json.loads(data_act_s.decode())
    data_actuators_s=actuation_s
    .get("act_values_s")
    while c_flag:
        ### measure and send   
        if data_actuators_s != cl_vector_s:                                    
            for i in range(3):
                values[i] =adc.read_adc(i, gain=GAIN,data_rate=860)
            data = json.dumps({"adc_values_s": values})
            client_stator.send(data.encode())
        else:
            print("Closing")
            c_flag=False
            break
             
            ### Receive and actuate
        data_act_s = client_stator.recv(1024) 
        actuation_s= json.loads(data_act_s.decode())
        data_actuators_s=actuation_s.get("act_values_s")
        print(data_actuators_s)
        ###### actuate
        
        magnet1r.ChangeDutyCycle(data_actuators_s[0])
        magnet1l.ChangeDutyCycle(data_actuators_s[1])
        magnet2r.ChangeDutyCycle(data_actuators_s[2])
        magnet2l.ChangeDutyCycle(data_actuators_s[3])
        

threads=[]
for i in range(1):
    t = threading.Thread(name=str(i),target=threaded_client)
    t.daemon = True
    threads.append(t)
    t.start()
    
print('threads open')
while c_flag:
    time.sleep(1)
    print("client connected")
    
 
print('closing threads') 
for c in threads:
        c.join()