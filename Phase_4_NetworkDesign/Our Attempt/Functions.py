import socket
import math
import random
import struct
import time

#This function determines the size of the file and helps determine how many packets will need to be sent
def fileSize(file):
    # moves the pointer for the file to the end of the file 
    file.seek(0,2)
    #determines the file size
    fileSize = file.tell()
    # moves the file pointer the the beginning of the file so it can be transfered
    file.seek(0,0)
    return fileSize


#Determines how many loops(or packets) need to occur(or be sent)
def looptimes(fileSize, bufferSize):
    #Filesize is divided by (buffersize (1024)-3) to find the loopTimes, because 3 bytes will be used for SEQ & Checksum
    loopTimes = (fileSize / (bufferSize - 3))
    #increments the loop (becaasue we are starting at loop 1 and not 0)
    loop = math.ceil(loopTimes)
    return (loop)


#This function updates the sequence number
def updateSeqNum(seqNum):
    return 1 - seqNum


#Creates the checksum
def makeChecksum(data):
    #initalize to 0
    checksumAdd=0
    #Loop starts from 0 to len(data)-1, iterated +2 times.
    for i in range(0, len(data), 2):
        #taking 16 bits (2 bytes) value from 1024 bytes
        firstTwoBits = data[i : (i + 2)]
        if len(firstTwoBits) == 1:
            #If len(data)=1 it has to be unpacked with standard size 1
            twoByteInt = struct.unpack("!B",firstTwoBits)[0]
        elif len(firstTwoBits) == 2:
            #If len(data)=2 it has to be unpacked with standard size 2
            twoByteInt = struct.unpack("!H",firstTwoBits)[0]
            #checksum addition
        checksumAdd = checksumAdd + twoByteInt
        #loop goes on until condition becomes 'false'
        while (checksumAdd >> 16) == 1:
            #Wrapup function
            checksumAdd = (checksumAdd & 0xffff) + (checksumAdd >>16)
            #returns checksum for the data in integer
    return checksumAdd


#This function is used to determine if a bit error is going to occur based on user input
def errorCondition(packetErrorProbability = 0):
    #initialize the error condition as false
    dataBitError = False
    #This generates a random number from 0 to 1
    randNum = random.random()
    #compares the packet error probability with the random number and then performs if the random number is less than the error
    #probability
    if (randNum < (packetErrorProbability / 100)):
        dataBitError = True

    return dataBitError


#This function corrupts the data given the input
def dataError(data):
    #Replaces the first two bytes of the data with the letter X to produce an error
    return (b'XX'+ data[2:])


#This function extracts the data from the packet being received
def extractData(packet):
    #this is used to find the length of the data, (length of the sequence number (1byte) and checksum(2bytes) are fixed)
    dataLen = len(packet) - len("!BH")
    #Identify the packet format
    packetFormat = "!BH"+str(dataLen) + "s"
    #returns the unpacked values of packet.
    return struct.unpack(packetFormat,packet)


#This function assembes the actual packet with the sequence number, checksum and data
def makePacket(seqNums,chksums,data):
    #Identify the packet format
    packetFormat = "!BH" + str(len(data)) + "s"
    #Packs sequence number, checksum,data and forms a packet
    packet = struct.pack(packetFormat,seqNums,chksums,data)
    #returns packet in bytes
    return packet
