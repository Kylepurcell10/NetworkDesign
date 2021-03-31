import socket
import math
import random
import struct
import time

start = time.time()                    #This is used to find the start time of the program, elapsed time can be found by end time - start time

IP = "127.0.0.1"                   #Localhost is the IP address of this machine
Port = 20001                       #Port Number is assigned to 5005
bufferSize = 1024                     #bufferSize is set to 1024. packet size is 1024 with sequence number 1 byte, checksum 2 bytes, data 1021 bytes.
addr = (IP,Port)

#'''This function is used to find the file size with the help of seek function.'''
def fileSize(file):
    file.seek(0,2)                                                  # moves the file pointer to the EOF
    fileSize = file.tell()                                          #gets file size
    file.seek(0,0)                                                  # moves the file pointer the the beginning of the file
    return fileSize                                                 #returns the file size in integer


#'''This function is used to find how many loops the program has to run to transfer the file.'''
def looptimes(fileSize, bufferSize):
    loopTimes = (fileSize / (bufferSize - 3))                        #Filesize is divided by (buffersize (1024)-3) to find the loopTimes, because 3 bytes will be the headers for the packet
    loop = math.ceil(loopTimes)                                     #Changing loopTimes to next integer
    return (loop)                                                   #returns the loop value in integer


#'''This function updates the sequence number'''
def updateSeqNum(seqNum):
    return 1 - seqNum                                                #returns 1-seqNum in integer


#This function is used to find the Checksum for the data
def makeChecksum(data):
    checksumAdd=0                                             #inital checksum value is zero
    for i in range(0, len(data), 2):                                  #Loop starts from 0 to len(data)-1, iterated +2 times.
        firstTwoBits = data[i : (i + 2)]                               #taking 16 bits (2 bytes) value from 1024 bytes
        if len(firstTwoBits) == 1:
            twoByteInt = struct.unpack("!B",firstTwoBits)[0]   #If len(data)=1 it has to be unpacked with standard size 1
        elif len(firstTwoBits) == 2:
            twoByteInt = struct.unpack("!H",firstTwoBits)[0]   #If len(data)=2 it has to be unpacked with standard size 2
        checksumAdd = checksumAdd + twoByteInt    #checksum addition
        while (checksumAdd >> 16) == 1:                           #loop goes on until condition becomes 'false'
            checksumAdd = (checksumAdd & 0xffff) + (checksumAdd >>16)  #Wrapup function
    return checksumAdd                                        #returns checksum for the data in integer


#'''This function is used to find the Bit_Error has to happen or not'''
def errorCondition(packetErrorProbability = 0):
    dataBitError = False                                          #dataBitError has been initialised as 'False'
    randNum = random.random()                                    #This generates a random probability value (0.00 to 1.00)
    if (randNum < (packetErrorProbability / 100)):                                 #converting percentage(packetErrorProbability) to probability [(0 to 100) into (0.00 to 1.00)] in order to compare with randNum
        dataBitError = True                                       #If condition is 'True' it corrupts data
    return dataBitError                                           #returns dataBitError as 'True' or 'False'


#'''This Function is used to corrupt the data'''
def dataError(data):
    return (b'XX'+ data[2:])                                        #Replacing the first two bytes of data with alphabet character 'X' in order to corrupt, returns in byte


#'''This Function is used to Extract Data (Sequence number,checksum, data) from packet'''
def extractData(packet):                                            #Extracts the packet
    dataLen = len(packet) - len("!BH")                                  #this is used to find the length of the data, (length of the sequence number (1byte) and checksum(2bytes) are fixed)
    packetFormat = "!BH"+str(dataLen) + "s"                                  #This is the packet format. example if data length is 1021 bytes then it should be "!BH1021s".
    return struct.unpack(packetFormat,packet)                            #returns the unpacked values of packet.


#'''This Function is used to make packet (Sequence number + checksum + data -> together forms a packet)'''
def makePacket(seqNums,chksums,data):
    packetFormat = "!BH" + str(len(data)) + "s"                                #This is the packet format. example if data length is 1021 bytes then it should be "!BH1021s".
    packet = struct.pack(packetFormat,seqNums,chksums,data)                #Packs sequence number, checksum,data and forms a packet
    return packet                                                   #returns packet in bytes
