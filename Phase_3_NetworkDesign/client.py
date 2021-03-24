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
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# packet sequence
currentSequence = 0
# packet acknowledgement
currentACK = 0
# File to be sent over the network, this can be changed to any of the .bmp files that are included
filename = '/src/Projects/Network_Design/Network_Design_Phases/NetworkDesign/Phase_3_NetworkDesign/trashbin.jpg'
# Open the file and begin reading it with packet size of 1024
file = open(filename , 'rb')
# current data item being processed
data = file.read(bufferSize)

print("UDP IP:", IP)
print("UDP port:", Port)


def rdtSend(data):
    global currentSequence, currentACK

    # Create the Checksum
    values = (currentACK, currentSequence, base64.b64encode(data.encode('utf-8')))
    UDPData = struct.Struct('I I 8s')
    packedData = UDPData.pack(*values)
    checksumVal = hashlib.md5(packedData).hexdigest().encode('utf-8')
    # gets the constructed UDP packet
    sendPacket = makepacket(currentACK, data, checksumVal)
    # send the UDP packet
    UDPSend(sendPacket)

def makeChecksum(ACK, SEQ, DATA):
    values = (ACK, SEQ, DATA)
    packer = struct.Struct('I I 8s')
    packedData = packer.pack(*values)
    checksum = hashlib.md5(packedData).hexdigest().encode('utf-8')
    return checksum

# Make_packet function 
def makepacket(currentACK, data, checksumVal):
    global currentSequence

    # Build the UDP Packet
    values = (currentACK, currentSequence, base64.b64encode(data.encode('utf-8')), checksumVal)
    packetData = struct.Struct('I I 8s 32s')
    packet = packetData.pack(*values)
    return packet

def UDPSend(sendPacket):
    print('Packet sent: ', sendPacket)
    # Send the UDP Packet to the server
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



def isACK(receivePacket, ACKVal):
    global currentSequence, currentACK
    
    # checks ACK is of value ACKVal
    if receivePacket[0] == ACKVal and receivePacket[1] == currentSequence:
        return True
    else:
        return False


def rdtReceive(receivePacket):
    global currentACK
    global currentSequence
    global data

    # if the packet does not have an error and is acknowledged, then adjust variables for next packet
    # otherwise resend packet
    if not dataError(receivePacket) and isACK(receivePacket, currentACK + 1):
        # Return TRUE for Client to send next packet
        currentSequence = (currentSequence + 1) % 2
        return True
    else:
        # packet error or no acknowledgement, resend the previous packet
        print('Invalid packet: ', receivePacket)
        rdtSend(data)
        return False


dataList = ['trashbin.jpg']
#This list can be changed to anything else
#In this case the JPEG image is used 

# send the data items in data list consequetively
for data in dataList:
    success = False

    # send the data item until both sequences have been acknowledged by the server (success == True)
    while success == False:
        # send the data item
        rdtSend('b' + data)
        print('Data sent: ', data)

        # Receive Data
        try:
            packet, addr = sock.recvfrom(bufferSize) 
        except socket.timeout:
            print('Packet timed out! Resending packet...\n\n')
            continue

        receivePacket = unpacker.unpack(packet)
        print("Received from: ", addr)
        print("Received message: ", receivePacket)
        success = rdtReceive(receivePacket)

        if success:
            print('rdt2.2 UDP Packet communication successful\n')