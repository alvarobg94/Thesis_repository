import socket
import time
import threading
i=0
global c_flag
c_flag=True


# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# get local machine name
host = '10.16.172.249'                          
port = 9999
time.sleep(2)
# connection to hostname on the port.
s.connect((host, port))                               

# Receive no more than 1024 bytes..
def threaded_client():
    global c_flag
    while c_flag:      
        msg = s.recv(1024) 
        if msg:                                    
            print (msg.decode('utf-8')+'from the server\r\n')
        else:
            print("no message")
            c_flag=False
            
            

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