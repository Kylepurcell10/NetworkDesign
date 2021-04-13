import socket
import math
import random
import struct
import time
import Functions

#Local IP to be used in communications
IP = "127.0.0.1"
#Using port 20001
Port = 20001
#buffer of size 1024
bufferSize = 1024
#address is a combination of the IPaddress and the Port number
addr = (IP,Port)

#Function that handles the sending of packets to the server and receiving the ackowledgement data back
def rdtSend(clientSocket,addr,sendSeqNum,data,packetErrorProbability = 0,packetDropProbability = 0):

    #identifier of if the full process has been completed
    successfulSend = 0

    #Make the packet with the correct sequence number, the Checksum , and the first 1024 bits of data from the image
    packet = Functions.makePacket(sendSeqNum, Functions.makeChecksum(data), data)

    #loop as long as the file has not been successfully sent
    while (not(successfulSend)):

        #Send the packet
        clientSocket.sendto(packet,addr)
        print ("Sending the Packet...")

        #Start the timer for the packet
        startTime = time.time()

         #Set the timeout value for the socket to be 0.05 seconds
        clientSocket.settimeout(0.05)
        try:
            #Try and gather the data for a packet, otherwise (exception break) there will be a timeout
            print ("Timer Started.")
            #Get the ackowledgement from the server
            ACKPacket,addr = clientSocket.recvfrom(bufferSize)
            #Timer is active only for receive function which takes care of the entire operation
            clientSocket.settimeout(None)

            if (Functions.errorCondition(packetDropProbability)):
                #If dataBitError is true a packet will be dropped at the rate of the variable packetDropProbability
                # This will force it out of the loop and discard the packet
                print ("Acknowledgement Packet Dropped")
                #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                while(time.time() < (startTime + 0.05)):
                            pass
                print ("Timed Out. \n")
                #Comes out of current loop and starts again since condition will be while(1).
                successfulSend = 0

            #this statement will execute if a packet was not intentionally dropped
            else:
                #get the packets respective sequence number, its checksum, and its ackowledgement
                packetSeqNum,senderChecksum,ACKData=Functions.extractData(ACKPacket)

                #If there is user predefined data bit errors, the function will modift the ackowledgement.
                if (Functions.errorCondition(packetErrorProbability)):
                        #function to actually corrupt the data
                        ACKData = Functions.dataError(ACKData)
                        print ("ACK Corrupted.")
                #This statement provides what the ackoledgement should have been so that it can be compared, and the program can figure out the paket needs to be discarded
                refrenceAck ="ACK"+str(sendSeqNum)
                #Finds the checksum using the corrupted received acknowledgement
                ACKChecksum = Functions.makeChecksum(ACKData)
                #Decodes from byte to integer for the comparison
                ACKData = ACKData.decode("UTF-8")

            #if packet is corrupted or has unexpected acknowledgement it resends the packet
                if (ACKData != refrenceAck) or (ACKChecksum != senderChecksum ):
                        print ("ACK: {0}, Sequence #: {1}".format(ACKData,sendSeqNum))
                        print("Resending the Packet")
                        #Loop continues until satisfies condition, Basically resends the packet.
                        successfulSend = 0
                        #If the socket takes longer than the allotted timout tiem, it fails and exits the loop
                        while(time.time() < (startTime + 0.05)):
                            pass
                        print ("Timed Out. \n")

            #If theres nothing wrong with the packet, print to the screen the ackowledgement and the sequence number, and then update the sequence number
                elif (ACKData == refrenceAck) and (ACKChecksum == senderChecksum ):
                        print ("ACK: {0}, Sequence #: {1}".format(ACKData,sendSeqNum))
                        #updates sequence number
                        sendSeqNum = 1 - sendSeqNum
                        #successful data transfer
                        successfulSend = 1
                        print ("Timer Stopped.")

        except(socket.timeout):
            print ("Timed Out. \n")
#Comes out of current loop and starts again since condition will be while(1).
            successfulSend = 0
#returns updated sequence number
    return sendSeqNum


##USER INPUT REQUIRED

#To corrupt data packet, Set one of these value to a number from 0 - 99
#packetErrorProbability controls the probability of a bit error within X% of packets
packetErrorProbability = 0
#packetDropProbability is the probability that a packet is dropped in the data transfer
packetDropProbability = 0

#Create the actual socket itself
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#Open the file that is going to be transfered
fileName = 'Trash.bmp'
file = open(fileName,'rb')

#Calculate the size of the file
fileSize = Functions.fileSize(file)

#determine how many times a packet will need to be sent in order for the file to be completely transfered
loop = Functions.looptimes(fileSize,bufferSize)

#change loop from integer to byte in order to send data from client to server
loop_bytes = struct.pack("!I", loop)
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
#Sequence Number is set to 0 initially
sendSeqNum = 0
#sending the file size to Server
sendSeqNum = rdtSend(clientSocket, addr, sendSeqNum, loop_bytes)


print('Client File Transfer Starts...')

#Program runs the data transfer 'loop' number of times
for i in range(0,loop):
    print("\nLoop :",i + 1)
    #reading the file, 1021 bytes at a time with 1 byte being the sequence number and 2 bytes being the checksum
    ImgPkt = file.read(bufferSize - 3)
    #This loop is only here to ensure that corruption doesnt happen on the last two packets otherwise the sockets could fail or stall
    if(i >= (loop - 2)):
        #Error probability manually set to zero (No corruption) if true.
        packetErrorProbability = 0
        #Packet Dropping probability manually set to zero (No corruption) if true.
        packetDropProbability = 0
        #calls the function to send the packet
    sendSeqNum = rdtSend(clientSocket,addr,sendSeqNum,ImgPkt,packetErrorProbability,packetDropProbability)
    #Iterate the loop
    i = i + 1

#Close the file
file.close()
#Close the socket
clientSocket.close()
