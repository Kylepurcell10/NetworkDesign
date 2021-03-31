import socket
import binascii
import struct
import sys
import hashlib
import base64
import time
from asyncio.tasks import sleep

#IP Address for local communications
IP = "127.0.0.1"
#Local Port for client and server
Port = 20001
#buffer to receive information from client
bufferSize  = 1024

# Integer, Integer, 8 letter char array, 32 letter char array
unpacker = struct.Struct('I I 8s 32s')

#Function used to implement the rdt send
def rdtSend(currentSequence , currentAck , data):

    #Creating the checksum 
    values = (currentACK, currentSequence, data)
    UDPData = struct.Struct('I I 8s')
    packedData = UDPData.pack(*values)
    checksumVal = hashlib.md5(packedData).hexdigest().encode('utf-8')
    #This is where it gets the UDP packet
    sendPacket = makepacket(currentACK, currentSequence,  data, checksumVal)
    UDPSend(sendPacket)

#Function used to make the checksum
def makepacket(currentACK, currentSequence, data, checksumVal):

    #Creating the checksum 
    values = (currentACK, currentSequence, data, checksumVal)
    packetData = struct.Struct('I I 8s 32s')
    packet = packetData.pack(*values)
    return packet

#Function to send the UDP Packet to the server
def UDPSend(sendPacket):
        senderSocket.sendto(sendPacket, (IP, Port))

#Function that checks the packet for corruption
def dataError(receivePacket):
    # Calculate new checksum of the  [ ACK, SEQ, DATA ]
    checksum = makeChecksum(receivePacket[0], receivePacket[1], receivePacket[2])
    # Compare calculated chechsum with checksum value in packet
    if receivePacket[3] == checksum:
        print('CheckSums is OK')
        return False
    else:
        print('CheckSums Do Not Match')
        return True

#Function used to make the checksum
def makeChecksum(ACK, SEQ, DATA):
    values = (ACK, SEQ, DATA)
    packer = struct.Struct('I I 8s')
    packedData = packer.pack(*values)
    checksum = hashlib.md5(packedData).hexdigest().encode('utf-8')
    return checksum

#Function to tell if the packet is acknowledged
def isACK(receivePacket, ACKVal):
    
    if (receivePacket[0] == ACKVal):
        return True
    else:
        return False

# Create the actual UDP socket for the server
senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("UDP IP:", IP)
print("UDP port:", Port)

# Open the file and begin reading it with packet size of 1024
filename = 'Cat.bmp'
file = open(filename , 'rb')
# current data item being processed
data = file.read(bufferSize)

currentSequence = 0
currentACK = 0

#This will be used to send the data
while (data):

    #This keeps sending data item until both sequences have been acknowledged by the server
    rdtSend(currentSequence, currentACK , data)
    
    packet, addr = senderSocket.recvfrom(bufferSize)
    print(packet)

    print("Received from: ", addr) 
    receivePacket = unpacker.unpack(packet)

    if(dataError(receivePacket) == False and isACK(receivePacket ,  currentACK) == True):
        currentACK = currentACK + 1
        currentSequence  = (currentSequence + 1) % 2
        data = file.read(bufferSize)
        print("sending more data")
    else:
        print("Resending packet")


file.close()
senderSocket.close
