import socket                                         
import threading
import time
import paramiko
import sys
import json
global c_flag

c_flag=1
s_flag=1
#server bind socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
host = 'HP-Alvaro'                       
port = 9999                                          
serversocket.bind((host, port)) 

############ SSH objects here


#ssh1.ssh_command(ssh1,"python threaded_client")
#Second ssh for the other pi
SSH_ADDRESS = "thesis"
SSH_USERNAME = "pi"
SSH_PASSWORD = "thesis"
SSH_COMMAND = "python threaded_client.py"
#
### CODE BELOW ##

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_stdin = ssh_stdout = ssh_stderr = None
#

try:
    ssh.connect(SSH_ADDRESS, username=SSH_USERNAME, password=SSH_PASSWORD)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(SSH_COMMAND)
except Exception as e:
    sys.stderr.write("SSH connection error: {0}".format(e))

# queue up to 2 requests
serversocket.listen(2)  
##Subprocess turning on the raspberry code

                                         
def threaded_server():
    i=0
    global data_arr
    while c_flag:
        # establish a connection
        clientsocket,addr = serversocket.accept() 
        print("Got a connection from %s" % str(addr)) 
        first_mes = clientsocket.recv(4096)
        print(first_mes.decode('utf-8'))
        j=0
        while c_flag:
            i+=1
            data_actuation = ([100-j,100-j,100-j,100-j])
            j+=1
            if(j>100):
                j=0a
            data_send = json.dumps({"act_values": data_actuation})
            clientsocket.send(data_send.encode())
            data = clientsocket.recv(4096)
            data_json = json.loads(data.decode())
            data_sensor=data_json.get("adc_values")
            print(data_sensor)
            time.sleep(0.1)
    endmsg="CLOSE"
    close_msg = json.dumps({"act_values": endmsg})
    clientsocket.send(close_msg.encode()) 
    msg = clientsocket.recv(1024)
    if msg.decode('utf-8') == "closing":  
        clientsocket.close

threads=[]
for i in range(1):
    t = threading.Thread(name=str(i),target=threaded_server)
    t.daemon = True
    threads.append(t)
    t.start()


print('threads open')
time.sleep(2)
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
       
