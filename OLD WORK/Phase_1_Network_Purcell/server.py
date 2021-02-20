import socket

#IP Address for local communications
IP     = "127.0.0.1"
#Local Port for client and server
Port   = 20001
#buffer to receive information from client
bufferSize  = 2048
#user defined sentence to send to the client
message = input("Enter Message to send to client: ")
#after the message is defined, it is encoded
modifiedmessage = message.encode("utf8")

# Create the actual UDP socket for the server
ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the local IP address and port
ServerSocket.bind((IP, Port))

# While loop to look for incoming data from the client and also send the message to the client
while(True):

# Server Receives the address of the client as well as an encoded message
    ClientData = ServerSocket.recvfrom(bufferSize)
    ClientMessage = ClientData[0]
    ClientAddress = ClientData[1]

# Server takes the compiled message and decodes it along with printing the address of the client
    print("The Message from the Client is: ", ClientMessage.decode("utf8","strict"))
    print("the Clients IP address and Port number are: ", ClientAddress)
 # Server sends a message to the client.
    ServerSocket.sendto(modifiedmessage, ClientAddress)