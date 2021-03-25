import socket
import binascii
import struct
import sys
import hashlib
import base64
import time

#IP Address for local communications
IP = "127.0.0.1"
#Local Port for client and server
Port = 20001
#buffer to receive information from client
bufferSize  = 1024

# Integer, Integer, 8 letter char array, 32 letter char array
unpacker = struct.Struct('I I 8s 32s')

# Create the actual UDP socket for the server
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
# Bind the socket to the local IP address and port 
serverSocket.bind((IP, Port))

#Function used to make the packet for the client
def makepacket(currentACK, currentSequence, data, checksumVal):
    # Build the UDP Packet
    values = (currentACK, currentSequence, data, checksumVal)
    packetData = struct.Struct('I I 8s 32s')
    packet = packetData.pack(*values)
    return packet

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

#Where the previous functions are used to send the packets back to the client
while True:
    print("Listening")
    #Where the data is received
    data, addr = serverSocket.recvfrom(bufferSize) 
    packet = unpacker.unpack(data)
    print("Received from:", addr)
    print("Received message:", packet)

    #This compares checksums to see if there are errors
    if not dataError(packet):
        print('CheckSums Matches, Packets are Ok')

        ACK = packet[0] + 1
        SEQ = packet[1]
        DATA = b''
        checksumVal = makeChecksum(ACK, SEQ, DATA)

        
        packet = makepacket(packet[0] + 1, packet[1], b'', checksumVal)
        print('Packeting')

        serverSocket.sendto(packet, addr)
        print('Sent')
    else:
        print('Checksums Do Not Match, Packet error')

        checksumVal = makeChecksum(packet[0] + 1, (packet[1] + 1) % 2, b'')

        packet = makepacket(packet[0] + 1, (packet[1] + 1) % 2, b'', checksumVal)
        print('Packeting')

        serverSocket.sendto(packet, addr)
        print('Sent')