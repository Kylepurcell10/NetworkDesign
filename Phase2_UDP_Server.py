import socket 
import os

BUFFER_SIZE = 4096
UDP_Port = 26411 #Port # used, in this case, my old student ID# was used
UDP_Address = '127.0.0.1' 
filename = "trash-bin-symbol.bmp"

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Creates server socket using UDP protocol
serverSocket.bind((UDP_Address, UDP_Port)) #Binds the UDP address and port# to server socket
print("UDP IP: %s" % UDP_Address)
print("UDP Port: %s" % UDP_Port)
print("Waiting to recieve byte array")
while True: #Loop that infnitely loops to keep checking UDP server
    f = open("trash-bin-symbol.bmp", 'wb')
    data, addr = serverSocket.recvfrom(BUFFER_SIZE)
    print('Client connected')
    while True:
        print('data = %s', (data)) 
        if not data:
            break
        else:
            f.write(data)
    print('Writing byte array into file')
    #Sends the aformentioned message when a message is recieved from the client by the server 
    f.close()
print('Done sending')
serverSocket.sendto('Thanks for connecting!'.encode('utf-8'), addr)
serverSocket.close()
    
