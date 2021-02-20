import socket

# Message to send to the server from the client is defined by user input
message      = input("Enter Message to send to Server: ")
# The message is then encoded
modifiedMessage     = message.encode("utf8")
# IP addresss and local port that will be used for communications
IPaddress           = "127.0.0.1"
Port                = 20001
# Maximum size of data that can be stored from message passing
bufferSize          = 2048

# Creating the UDP clinet socket
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending the encoded message to the server
ClientSocket.sendto(modifiedMessage, (IPaddress , Port))
# Receiving the message from the Server
ServerMessage = ClientSocket.recvfrom(bufferSize)
# Concatonating the server message and an introduction phrase
finalizedMessage = "The Message from the Server is: " + ServerMessage[0].decode("utf8","strict")
# Printing the phrase
print(finalizedMessage)