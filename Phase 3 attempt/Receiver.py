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
# Bind the socket to the local IP address and port 
sock.bind((IP, Port))

def makepacket(currentACK, currentSequence, data, checksumVal):
    # Build the UDP Packet
    values = (currentACK, currentSequence, data, checksumVal)
    packetData = struct.Struct('I I 8s 32s')
    packet = packetData.pack(*values)
    return packet


def makeChecksum(ACK, SEQ, DATA):
    values = (ACK, SEQ, DATA)
    packer = struct.Struct('I I 8s')
    packedData = packer.pack(*values)
    checksum = hashlib.md5(packedData).hexdigest().encode('utf-8')
    return checksum

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

dataFile = open('receive.bmp' , 'wb')
print("Listening")
currentAck = 0
data, addr = sock.recvfrom(bufferSize) 

while (data):

    packet = unpacker.unpack(data)
    print("Received from:", addr)
    print(packet)

    # Compare Checksums to test for error in data
    if not dataError(packet):
        dataFile.write(data)

        # Built checksum [ACK, SEQ, DATA]
        ACK = packet[0]
        SEQ = packet[1]
        DATA = b''
        checksumVal = makeChecksum(ACK, SEQ, DATA)

        
        packet = makepacket(packet[0], packet[1], b'', checksumVal)
        print('Packeting')

        # Send the UDP Packet
        sock.sendto(packet, addr)
        print('Sent')
        try:
            data, addr = sock.recvfrom(bufferSize)
        except:
            pass

    else:
        print('Checksums Do Not Match, Packet error')

        # Built checksum [ACK, SEQ, DATA]
        checksumVal = makeChecksum(packet[0] + 1, (packet[1] + 1) % 2, b'')

        packet = makepacket(packet[0] + 1, (packet[1] + 1) % 2, b'', checksumVal)
        print('Packeting')

        # Send the UDP Packet
        sock.sendto(packet, addr)
        print('Sent')

dataFile.close()
sock.close