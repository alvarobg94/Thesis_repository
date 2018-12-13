import socket                                         
import threading
import time
import paramiko
import sys
import json
global c_flag
import time
import numpy as np
import csv

c_flag=1
s_flag=1
cl_vector_s=[-1]*4
cl_vector_r=[-1]*8
#server bind socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = socket.gethostbyname(socket.gethostname())
port = 9999                                          
serversocket.bind((host, port)) 
global NOISE
NOISE=100
########### SSH pi in the rotor
# PARAMETERS 
SSH_ADDRESS = "thesis"
SSH_USERNAME = "pi"
SSH_PASSWORD = "thesis"
SSH_COMMAND = "python ~/raspberry_rotor/rotor5.py "+socket.gethostbyname(socket.gethostname())
#SSH creation
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_stdin = ssh_stdout = ssh_stderr = None
# Order 
try:
    ssh.connect(SSH_ADDRESS, username=SSH_USERNAME, password=SSH_PASSWORD)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(SSH_COMMAND)
except Exception as e:
    sys.stderr.write("SSH connection error: {0}".format(e))
    print('ssh error')
############# SSH pi in the estator
# PARAMETERS
SSH_ADDRESS2 = "thesis2"
SSH_USERNAME2 = "pi"
SSH_PASSWORD2 = "thesis2"
SSH_COMMAND2 = "python ~/raspberry_stator/stator5.py "+socket.gethostbyname(socket.gethostname())
# SSH creation
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_stdin = ssh_stdout = ssh_stderr = None
 #Order
try:
    ssh2.connect(SSH_ADDRESS2, username=SSH_USERNAME2, password=SSH_PASSWORD2)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh2.exec_command(SSH_COMMAND2)
except Exception as e:
    sys.stderr.write("SSH connection error: {0}".format(e))
    print('ssh error')


# queue up to the 2 requests
serversocket.listen(2)  

                                         
def threaded_server():
    i=0
    t2=0
    t2a=0

    global data_arr
    while c_flag:
        data_actuation_s=[0]*4
        data_actuation_r=[0]*8
        states=[0]*7
        states_nc=[0]*7
        state_vector=[]
        time_series=[]
        tnext=0
        # establish a connection
        r_socket,addr_r = serversocket.accept()
        print("Got a connection from %s the rotor" % str(addr_r))
        s_socket,addr_s = serversocket.accept() 
        print("Got a connection from %s the stator" % str(addr_s))  
        # receive calibrated data
        data_sensor_rj = r_socket.recv(4096)
        data_sensor_sj = s_socket.recv(4096)
        load_sensor_r = json.loads(data_sensor_rj.decode())
        load_sensor_s = json.loads(data_sensor_sj.decode())
        cal_r=load_sensor_r.get("adc_values_r_cal")
        cal_s=load_sensor_s.get("adc_values_s_cal")
        data_send_r = json.dumps({"act_values_r": data_actuation_r})
        data_send_s = json.dumps({"act_values_s": data_actuation_s})
        r_socket.send(data_send_r.encode())
        s_socket.send(data_send_s.encode())
        j=0
        i=0
        while c_flag:
            i=i+1
            t1=time.time()
            ### SENSING
            #tcom=time.time()
            data_sensor_sj = s_socket.recv(1024)
            data_sensor_rj = r_socket.recv(1024)
            load_sensor_r = json.loads(data_sensor_rj.decode())
            load_sensor_s = json.loads(data_sensor_sj.decode())
            data_sensor_r=load_sensor_r.get("adc_values_r")
            data_sensor_s=load_sensor_s.get("adc_values_s")
            for k in range(7):
                if k <4:
                    states_nc[k]=data_sensor_r[k]
                    states[k]=states_nc[k]-cal_r[k]
                else:
                    states_nc[k]=data_sensor_s[k-4]
                    states[k]=states_nc[k]-cal_s[k-4]
                states[k] = states[k]*4.096/2048
                states[k] = states[k]*1.5/2
            state_vector.extend(states)
            #print(states)
            #### ACTUATING
            ### Control computation
            for p in range(4):
                data_actuation_s[p] = NOISE*float(np.random.rand(1,1,1))  #4 external magnets
            ##                   |-pair 1-|  |-pair 2-| |--pair 3-|
            for p in range(8):
                data_actuation_r[p] = NOISE*float(np.random.rand(1,1,1))
            #### end of control computation
            ### data send has to be a value from 0 to 100
            data_send_r = json.dumps({"act_values_r": data_actuation_r})
            data_send_s = json.dumps({"act_values_s": data_actuation_s})
            r_socket.send(data_send_r.encode())
            s_socket.send(data_send_s.encode())
            t2a=t2
            t2=time.time()-t1
            if t2==0:
                t2=t2a
            print(t2)
            tnext=tnext+t2
            time_series.append(tnext)   
            
    
        close_msg_r = json.dumps({"act_values_r": cl_vector_r})
        r_socket.send(close_msg_r.encode())
        close_msg_s = json.dumps({"act_values_s": cl_vector_s})
        s_socket.send(close_msg_s.encode())  
        time.sleep(0.2)
        print("cerrando socket")
        r_socket.close()
        s_socket.close()
        print("socket cerrado")
        state_data=[0]*7
        length=len(state_vector)
        n_samples=int(length/7)
        state_data= [[0 for x in range(8)] for y in range(n_samples)] 
        c=0
        for v in range(n_samples):
            for w in range(8):
                if w==0:
                    state_data[v][w]=time_series[v]
                else:
                    state_data[v][w]=state_vector[c]
                    c=c+1

        with open('data_vector.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerows(state_data)

        print(state_data)
        print(tnext/n_samples)

# Put the server in a thread
threads=[]
for i in range(1):
    t = threading.Thread(name=str(i),target=threaded_server)
    t.daemon = True
    threads.append(t)
    t.start()
time.sleep(5)
while s_flag:
    command=input("Introduce your command")
    if command=="c":
        c_flag=0
    if command=="s":
        c_flag=0
        time.sleep(1)
        s_flag=0
        
        


print('closing threads')
for c in threads:
    print('ENDing threads')
    c.join()     
print('END')