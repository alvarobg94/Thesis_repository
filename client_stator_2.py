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
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.setup(10,GPIO.OUT)
GPIO.setup(9,GPIO.OUT)

#Establish the magnets right and left for both directions
magnet1r =GPIO.PWM(14,10000)
magnet1r.start(0)
magnet1l =GPIO.PWM(15,10000)
magnet1l.start(0)
magnet2r =GPIO.PWM(17,10000)
magnet2r.start(0)
magnet2l =GPIO.PWM(27,10000)
magnet2l.start(0)
magnet3r =GPIO.PWM(23,10000)
magnet3r.start(0)
magnet3l =GPIO.PWM(24,10000)
magnet3l.start(0)
magnet4r =GPIO.PWM(10,10000)
magnet4r.start(0)
magnet4l =GPIO.PWM(9,10000)
magnet4l.start(0)

flag1_w = threading.Event()
flag2_w = threading.Event()
flag3_w = threading.Event()
flag1_r = threading.Event()
flag2_r = threading.Event()
flag3_r = threading.Event()




# create a socket object
client_stator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# create an adc object
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

# get local machine name
host = sys.argv[1]                         
port = 9999
time.sleep(3)
# connection to hostname on the port.
client_stator.connect((host, port))                               

# Receive no more than 1024 bytes..
def threaded_client():
    global c_flag,vector
    cl_vector_s=[-1]*4
    values = [0]*3
    data_actuators_s=[0]*4
    while c_flag:
        ### measure and send   
        if data_actuators_s != cl_vector_s:                                    
            flag1_r.wait()
            flag1_r.clear()
            flag2_r.wait()
            flag2_r.clear()
            flag3_r.wait()
            flag3_r.clear()
            values[0]=vector[0]
            values[1]=vector[1]
            values[2]=vector[2]
        #set all the sensors to read another time
            flag1_w.set()
            flag2_w.set()
            flag3_w.set()
            
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
        
        # magnet1r.ChangeDutyCycle(data_actuators_s[0])
        # magnet1l.ChangeDutyCycle(data_actuators_s[1])
        # magnet2r.ChangeDutyCycle(data_actuators_s[2])
        # magnet2l.ChangeDutyCycle(data_actuators_s[3])
        # magnet3r.ChangeDutyCycle(data_actuators_s[4])
        # magnet3l.ChangeDutyCycle(data_actuators_s[5])
        # magnet4r.ChangeDutyCycle(data_actuators_s[6])
        # magnet4l.ChangeDutyCycle(data_actuators_s[7])
        
def thr_ada1():
    global vector
    vector=[0]*3
    flag1_w.set()
    while c_flag:
        # Read all the ADC channel values in a list.
        flag1_w.wait()
        flag1_w.clear()   
        vector[0] =adc.read_adc(0, gain=GAIN, data_rate=860)
        flag1_r.set()

def thr_ada2():
    global vector
    vector=[0]*3
    flag2_w.set()
    while c_flag:
        # Read all the ADC channel values in a list.
        flag2_w.wait()
        flag2_w.clear()
        vector[1] =adc.read_adc(1, gain=GAIN, data_rate=860)
        flag2_r.set()

def thr_ada3():
    global vector
    vector=[0]*3
    flag3_w.set()
    while c_flag:
        # Read all the ADC channel values in a list.
        flag3_w.wait()
        flag3_w.clear() 
        vector[2] =adc.read_adc(2, gain=GAIN, data_rate=860)
        flag3_r.set()

threads=[]
for func in [thr_ada1, thr_ada2, thr_ada3, threaded_client]:
    t = threading.Thread(name=str(i),target=func)
    t.daemon = True
    threads.append(t)
    t.start()
    i=i+1
    
print('threads open')
while c_flag:
    time.sleep(1)
    print("client connected")
    
 
print('closing threads') 
for c in threads:
        c.join()