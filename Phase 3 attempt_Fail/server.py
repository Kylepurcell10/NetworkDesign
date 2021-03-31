import socket
import binascii
import struct
import sys
import hashlib
import base64
import time
from asyncio.tasks import sleep


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

def UDPSend(sendPacket):
        receiverSocket.sendto(sendPacket, (IP, Port))

#Function used to make the checksum
def makeChecksum(ACK, SEQ, DATA):
    values = (ACK, SEQ, DATA)
    packer = struct.Struct('I I 8s')
    packedData = packer.pack(*values)
    checksum = hashlib.md5(packedData).hexdigest().encode('utf-8')
    return checksum

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
        
#IP Address for local communications
IP = "127.0.0.1"
#Local Port for client and server
Port = 20002
#buffer to receive information from client
bufferSize  = 1024

# Integer, Integer, 8 letter char array, 32 letter char array
unpacker = struct.Struct('I I 8s 32s')

# Create the actual UDP socket for the server
receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
receiverSocket.connect((IP , Port))
currentACK = 0
currentSequence = 0
dataFile = open('receive.bmp' , 'wb')
print("Listening")
packet, addr = receiverSocket.recvfrom(bufferSize)
receivedPacket = unpacker.unpack(packet)

#Where the previous functions are used to send the packets back to the client
while True:
    print("Received from:", addr)
    print("Data Received:" , receivedPacket[2])

     #This compares checksums to see if there are errors
    if not dataError(receivedPacket):
        dataFile.write(receivedPacket[2])

        # Built checksum [ACK, SEQ, DATA]
        ACK = receivedPacket[0]
        SEQ = receivedPacket[1]
        DATA = b''
        print('Packeting')
        rdtSend(currentSequence , currentACK , DATA)
        print('Sent')
        currentACK = currentACK + 1
        currentSequence = (currentSequence + 1) % 2
        
    else:
        print('Packet error')
        checksumVal = makeChecksum(packet[0] + 1, (packet[1] + 1) % 2, b'')
        packet = makepacket(packet[0] + 1, (packet[1] + 1) % 2, b'', checksumVal)
        print('Packeting')
        receiverSocket.sendto(packet, addr)
        print('Sent')

sleep(10)
packet, addr = receiverSocket.recvfrom(bufferSize)
receivedPacket = unpacker.unpack(packet)

dataFile.close()
receiverSocket.close