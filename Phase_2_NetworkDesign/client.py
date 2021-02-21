import socket

# IP addresss and local port that will be used for communications
IPaddress           = "127.0.0.1"
Port                = 20001
# Creating the UDP clinet socket
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ClientSocket.connect((IPaddress, Port))

# Maximum size of data that can be stored from message passing
bufferSize          = 1024
# Open the file that is going to be edited
fileToReceive = open('receive.bmp' , 'wb')
#receive the first packet and set that as the current stream of packets
dataStream = ClientSocket.recv(bufferSize)

#while packets are coming in, write them to the file and then gather a new packet
while(dataStream):
    fileToReceive.write((dataStream))
    dataStream = ClientSocket.recv(bufferSize)

#ackowledge that all the data has been received, close both the socket and the file.
print("received the data")
fileToReceive.close()
ClientSocket.close