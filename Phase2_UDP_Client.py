import socket 

BUFFER_SIZE = 1024
UDP_Port = 26411 #Port # used, in this case, my old student ID# was used
UDP_Address = '127.0.0.1' #IP address used, in this case the local host IP address was used

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Creates client socket using UDP protocol
clientSocket.connect((UDP_Address, UDP_Port))
print("UDP IP:", UDP_Address) #Prints IP address used
print("UDP Port: %s" % UDP_Port) #Prints Port # used

filename = "trash-bin-symbol.bmp"
f = open(filename, 'rb')
print('Reading file into byte array')

with open('trash-bin-symbol.bmp', 'rb') as f:
        print('File read')
        byte = f.read()
        clientSocket.sendto(byte, (UDP_Address, UDP_Port))
data, addr = clientSocket.recvfrom(BUFFER_SIZE)
print(str(data))
#Sends the aformaentioned message to the IP and port #, this has to be encoded into utf-8 as it cannot be sent as is  
f.close() #Ends client socket
clientSocket.close()
#Some code was taken from the lecture slides provided

