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

# Create the actual UDP socket for the server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("UDP IP:", IP)
print("UDP port:", Port)

def rdtSend(data):
    global currentSequence, currentACK

    # Create the Checksum
    values = (currentACK, currentSequence, data)
    UDPData = struct.Struct('I I 8s')
    packedData = UDPData.pack(*values)
    #Creates a 32 bit checksum
    checksumVal = hashlib.md5(packedData).hexdigest().encode('utf-8')
    # gets the constructed UDP packet
    sendPacket = makepacket(currentACK, data, checksumVal)
    # send the UDP packet
    UDPSend(sendPacket)

    # Make_packet function 
def makepacket(currentACK, data, checksumVal):

    # Build the UDP Packet
    values = (currentACK, currentSequence, data, checksumVal)
    packetData = struct.Struct('I I 8s 32s')
    packet = packetData.pack(*values)
    return packet

def UDPSend(sendPacket):
        sock.sendto(sendPacket, (IP, Port))


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

def makeChecksum(ACK, SEQ, DATA):
    values = (ACK, SEQ, DATA)
    packer = struct.Struct('I I 8s')
    packedData = packer.pack(*values)
    checksum = hashlib.md5(packedData).hexdigest().encode('utf-8')
    return checksum

def isACK(receivePacket, ACKVal):
    
    # checks ACK is of value ACKVal
    if (receivePacket[0] == ACKVal and receivePacket[1] == currentSequence):
        return True
    else:
        return False



currentSequence = 0;
currentACK = 0;

# Open the file and begin reading it with packet size of 1024
file = open('Cat.jpg' , 'rb')
# current data item being processed
data = file.read(bufferSize)

while (data):

    # send the data item
    rdtSend(data)
    try:
        packet, addr = sock.recvfrom(bufferSize)
    except:
        pass

    print("Received from: ", addr) 
    receivePacket = unpacker.unpack(packet)

    if( dataError(receivePacket) == False and isACK(receivePacket ,  + 1) == True):
        currentAck = currentACK + 1;
        currentSequence  = (currentSequence + 1) % 2;
        data = file.read(bufferSize);


file.close()
sock.close
