import socket

#IP Address for local communications
IP     = "127.0.0.1"
#Local Port for client and server
Port   = 20001
#buffer to receive information from client
bufferSize  = 1024
# Create the actual UDP socket for the server
ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the local IP address and port
ServerSocket.bind((IP, Port))
# Server waits listens for clients with a maximum of 5 supported clients
ServerSocket.listen(5)

# File to be sent over the network, this can be changed to any of the .bmp files that are included
filename = 'Cat.bmp'
# Open the file and begin reading it with packet size of 1024
file = open(filename , 'rb')
dataStream = file.read(bufferSize)

# Gather the client information and print where it is going
ClientSocket , ClientAddress = ServerSocket.accept()
print("Client Address is :" , ClientSocket , "Client Port is:", ClientAddress)

# Get a packet, and send it to the client, then gather a new one. Do this until there are no more packets available
while(dataStream):
    ClientSocket.send(dataStream)
    dataStream = file.read(bufferSize)

# Ackowledge that the data has been sent and close the socket and file
print("sent the data")
file.close()    
ServerSocket.close()
