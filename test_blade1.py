import time
import threading
import RPi.GPIO as GPIO
import Adafruit_ADS1x15
import csv
#import matplotlib.pyplot as plt

global c_flag
global dc
dc=0
c_flag=1
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#GPIO ports to control the magnets, set them as output information
GPIO.setup(14,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
magnet1r =GPIO.PWM(14,10000)
magnet1r.start(0)
magnet1l =GPIO.PWM(15,10000)
magnet1l.start(0)

        #magnet1r.ChangeDutyCycle(data_actuators_r[0])
        #magnet1l.ChangeDutyCycle(data_actuators_r[1])

adc = Adafruit_ADS1x15.ADS1015()

def threaded_User():
	global dc
	global c_flag
	while c_flag:
		command=raw_input("Introduce your command")
		print("your command is "+command)
		if(command=="s"): 
			c_flag=0
		if(command=="a"): 
			dc=100
		if(command=="n"): 
			dc=0
		



GAIN = 1
tnext=0
t=[]
d=[]
i=0
adc.start_adc(0, gain=GAIN)
th = threading.Thread(name=str(i),target=threaded_User)
th.daemon = True
th.start()
t0 = time.time()
while c_flag:
    t1=time.time()
    i=i+1# Read the last ADC conversion value and print it out.
    value =adc.get_last_result()
    value=value*4.096/2048
    value=value*1.5/2
    magnet1r.ChangeDutyCycle(dc)
    time.sleep(0.001)
    t2=time.time()-t1
    tnext=tnext+t2
    t.append(tnext)
    d.append(value)
adc.stop_adc()
print("loop finished, writing csv")   
# Stop continuous conversion.  After this point you can't get data from get_last_result!
b=zip(t,d)
with open('test.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(b)
f.close()
print("all done, csv generated")

#plt.plot(t,d)
#plt.show()

