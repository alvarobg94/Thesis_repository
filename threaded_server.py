import socket                                         
import threading
import time
import paramiko
import sys
global c_flag

c_flag=1
s_flag=1
#server bind socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
host = '10.16.172.249'                         
port = 9999                                          
serversocket.bind((host, port)) 

SSH_ADDRESS = "192.168.0.1"
SSH_USERNAME = "pi"
SSH_PASSWORD = "thesis"
SSH_COMMAND = "python threaded_ssh_client"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_stdin = ssh_stdout = ssh_stderr = None

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
    while c_flag:
        # establish a connection
        clientsocket,addr = serversocket.accept()          
        print("Got a connection from %s" % str(addr))    
        while c_flag:
            i+=1;
            msg=str(i)
            print('sending message' +str(i)+'\r\n')
            clientsocket.send(msg.encode('utf-8'))
            time.sleep(1)
        
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
       
