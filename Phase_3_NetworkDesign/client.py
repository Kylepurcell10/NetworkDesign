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

#Prints both the IP and Port number
print("UDP IP:", IP)
print("UDP port:", Port)

#Function used to implement the rdt 2.2 protocol
def rdtSend(data):
    global currentSequence, currentACK

    #creating the checksum 
    values = (currentACK, currentSequence, base64.b64encode(data.encode('utf-8')))
    UDPData = struct.Struct('I I 8s')
    packedData = UDPData.pack(*values)
    checksumVal = hashlib.md5(packedData).hexdigest().encode('utf-8')
    #This is where it gets the UDP packet
    sendPacket = makepacket(currentACK, data, checksumVal)
    UDPSend(sendPacket)

#Function used to make the checksum
def makeChecksum(ACK, SEQ, DATA):
    values = (ACK, SEQ, DATA)
    packer = struct.Struct('I I 8s')
    packedData = packer.pack(*values)
    checksum = hashlib.md5(packedData).hexdigest().encode('utf-8')
    return checksum

#Function that parces the file into packets to be sent
def makepacket(currentACK, data, checksumVal):
    global currentSequence

    #This is where ther UDP packet is made
    values = (currentACK, currentSequence, base64.b64encode(data.encode('utf-8')), checksumVal)
    packetData = struct.Struct('I I 8s 32s')
    packet = packetData.pack(*values)
    return packet

#Function to send the UDP Packet to the server
def UDPSend(sendPacket):
    print('Packet sent: ', sendPacket)
    sock.sendto(sendPacket, (IP, Port))


#Function that checks the packet for corruption
def dataError(receivePacket):
    #This calculates the new Checksum
    checksum = makeChecksum(receivePacket[0], receivePacket[1], receivePacket[2])
    #This calculated checksum is then compared to the one in the packet
    if receivePacket[3] == checksum:
        print('CheckSums is OK')
        return False
    else:
        print('CheckSums Do Not Match')
        return True


#Function to tell if the packet is acknowledged
def isACK(receivePacket, ACKVal):
    global currentSequence, currentACK
    
    if receivePacket[0] == ACKVal and receivePacket[1] == currentSequence:
        return True
    else:
        return False

#Function used to check the received rdt packet from the server
def rdtReceive(receivePacket):
    global currentACK
    global currentSequence
    global data

    #If the packet does not have an error and is acknowledged, then the next packet's variables
    #will be adjusted as needed; otherwise the packet wil be resent
    if not dataError(receivePacket) and isACK(receivePacket, currentACK + 1):
        # Return TRUE for Client to send next packet
        currentSequence = (currentSequence + 1) % 2
        return True
    else:
        #If there is a packet error or no acknowledgement, it will resend the previous packet
        print('Invalid packet: ', receivePacket)
        rdtSend(data)
        return False

dataList = ['trashbin.jpg']
#This list of the data being transferred
#In this case the JPEG image is used 

#This will be used to send the data from the data list
for data in dataList:
    success = False

    #This keeps sending data item until both sequences have been acknowledged by the server
    while success == False:
        # send the data item
        rdtSend('b' + data)
        print('Data sent: ', data)

        #Executes when a packet has timed out and starts resending if so
        try:
            packet, addr = sock.recvfrom(bufferSize) 
        except socket.timeout:
            print('Packet timed out! Resending packet...\n\n')
            continue
        #Prints both the IP and port number and the recieved message in bytes
        receivePacket = unpacker.unpack(packet)
        print("Received from: ", addr)
        print("Received message: ", receivePacket)
        success = rdtReceive(receivePacket)

        if success:
            print('RDT2.2 UDP Packet Communication successful\n')