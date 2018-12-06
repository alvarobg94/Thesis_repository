import socket                                         
import threading
import time
import paramiko
import sys
import json
global c_flag
import time

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

# ########### SSH pi in the rotor
# # PARAMETERS 
# SSH_ADDRESS = "thesis"
# SSH_USERNAME = "pi"
# SSH_PASSWORD = "thesis"
# SSH_COMMAND = "python ~/raspberry_rotor/client_rotor_1_csv.py "+socket.gethostbyname(socket.gethostname())
# #SSH creation
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh_stdin = ssh_stdout = ssh_stderr = None
# # Order 
# try:
#     ssh.connect(SSH_ADDRESS, username=SSH_USERNAME, password=SSH_PASSWORD)
#     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(SSH_COMMAND)
# except Exception as e:
#     sys.stderr.write("SSH connection error: {0}".format(e))
#     print('ssh error')
# ############# SSH pi in the estator
# # PARAMETERS
# SSH_ADDRESS2 = "thesis2"
# SSH_USERNAME2 = "pi"
# SSH_PASSWORD2 = "thesis2"
# SSH_COMMAND2 = "python ~/raspberry_stator/client_stator_1_csv.py "+socket.gethostbyname(socket.gethostname())
# # SSH creation
# ssh2 = paramiko.SSHClient()
# ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh_stdin = ssh_stdout = ssh_stderr = None
#  #Order
# try:
#     ssh2.connect(SSH_ADDRESS2, username=SSH_USERNAME2, password=SSH_PASSWORD2)
#     ssh_stdin, ssh_stdout, ssh_stderr = ssh2.exec_command(SSH_COMMAND2)
# except Exception as e:
#     sys.stderr.write("SSH connection error: {0}".format(e))
#     print('ssh error')


# queue up to the 2 requests
serversocket.listen(2)  


                                         
def threaded_server():
    i=0
    global data_arr
    while c_flag:
        data_actuation_s=[0]*4
        data_actuation_r=[0]*8
        # establish a connection
        r_socket,addr_r = serversocket.accept()
        print("Got a connection from %s the rotor" % str(addr_r))
        s_socket,addr_s = serversocket.accept() 
        print("Got a connection from %s the stator" % str(addr_s))  
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
        print(cal_r)
        print(cal_s)
        j=0
        while c_flag:
            i+=1
            t1=time.time()
            ### SENSING
            print("esperando r")
            data_sensor_rj = r_socket.recv(4096)
            print("esperando s")
            data_sensor_sj = s_socket.recv(4096)
            print("load r")
            load_sensor_r = json.loads(data_sensor_rj.decode())
            print("load s")
            load_sensor_s = json.loads(data_sensor_sj.decode())
            data_sensor_r=load_sensor_r.get("adc_values_r")
            data_sensor_s=load_sensor_s.get("adc_values_s")
            print(data_sensor_r)
            print(data_sensor_s)
            #### ACTUATING
            ### Control computation
            data_actuation_s = ([100-j,100-j,100-j,100-j])  #4 external magnets
            ##                   |-pair 1-|  |-pair 2-| |--pair 3-|
            data_actuation_r = ([100-j,100-j,100-j,100-j,100-j,100-j,100-j,100-j]) #8 rotor magnets
            j+=1
            if(j>100):
                j=0
            #### end of control computation
            ### data send has to be a value from 0 to 100
            data_send_r = json.dumps({"act_values_r": data_actuation_r})
            data_send_s = json.dumps({"act_values_s": data_actuation_s})
            r_socket.send(data_send_r.encode())
            s_socket.send(data_send_s.encode())
            t2=time.time()-t1
            print(t2)       
            
    
        close_msg_r = json.dumps({"act_values_r": cl_vector_r})
        r_socket.send(close_msg_r.encode())
        close_msg_s = json.dumps({"act_values_s": cl_vector_s})
        s_socket.send(close_msg_s.encode())  
        time.sleep(0.2)
        print("cerrando socket")
        r_socket.close()
        s_socket.close()
        print("socket cerrado")
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