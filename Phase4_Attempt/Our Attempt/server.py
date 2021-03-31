import socket
import math
import random
import struct
import time
import Functions

start = time.time()                    #This is used to find the start time of the program, elapsed time can be found by end time - start time

IP = "127.0.0.1"                   #Localhost is the IP address of this machine
Port = 20001                       #Port Number is assigned to 5005
bufferSize = 1024                     #bufferSize is set to 1024. packet size is 1024 with sequence number 1 byte, checksum 2 bytes, data 1021 bytes.
addr = (IP,Port)


def rdtReceivePacket (serverSocket,bufferSize,receiveSeqNum,packetErrorProbability=0,packetDropProbability=0):
    successfulReceive = 0                                                                  #Receive_sucessful is set to '0' initially
    while (not(successfulReceive)):                                                        #loop goes on until condition becomes 'false'

        data, address = serverSocket.recvfrom(bufferSize)                                          #Packet is received from client

        if (Functions.errorCondition(packetDropProbability)):                                             #If dataBitError is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.
          print ("Data Packet Dropped\n")
          successfulReceive = 0                                                              #Comes out of current loop and starts again since condition will be while(1).

        else:                                                                               #If dataBitError is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            seqNum,checksum,imagePacket=Functions.extractData(data)                            #Extracts the sequence number, checksum value, data from a packet

            if (Functions.errorCondition(packetErrorProbability)):                                         #If dataBitError is true, it starts to corrupt packet intentionally
                imagePacket = Functions.corruptData(imagePacket)                                   #Function to corrupt data
                print ("\nData Corrupted")


            receiverChecksum = Functions.checksum(imagePacket)                                       #Receiver Checksum in integer

            if ((receiverChecksum == checksum) and (seqNum == receiveSeqNum)):                     #if packet is not corrupted and has expected sequence number, sends Acknowledgement with sequence number  *updates sequence number for next loop
                    Ack = receiveSeqNum                                                        #sends sequence number
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                 #Converting (Ack) from int to string and then encoding to bytes
                    senderACK = Functions.makePacket(seqNum,Functions.checksum(Ack),Ack)     #Server sends Ack with Seq_num, checksum, Ack
                    print("Sequence #: {0}, Receiver Sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seqNum,receiveSeqNum,checksum,receiverChecksum))
                    receiveSeqNum = 1 - seqNum                                                  #update sequence number to the next expected seqNum
                    successfulReceive = 1                                                  #Comes out of while loop

            elif ((receiverChecksum != checksum) or (seqNum != receiveSeqNum)):                    #if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
                    Ack = 1 - receiveSeqNum                                                    #last acked sequence numvber
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                 #Converting (Ack) from int to string and then encoding to bytes
                    senderACK = Functions.makePacket(1 - receiveSeqNum,Functions.checksum(Ack),Ack) #Server sends Ack with Seq_num, checksum, Ack
                    print("Server Requested to Resend the Packet")
                    print("Sequence #: {0}, Receiver Sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seqNum,receiveSeqNum,checksum,receiverChecksum))
                    successfulReceive = 0                                                  #Loop continues until satisfies condition
            serverSocket.sendto(senderACK,address)                                                 #sending the Acknowledgement packet to the client

    return imagePacket,address,receiveSeqNum

#To corrupt acknowledgemnt packet, Set value from 0 - 99 in packetErrorProbability
packetErrorProbability = 0                                                  #packetErrorProbability is the error probability and can be set from 0-99
packetDropProbability = 0                                                   #packetDropProbability is the packet dropping probability and can be set from 0-99

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)                      #Socket with IPV4, UDP
serverSocket.bind(addr)                                                             #Binding the socket
print("Server Ready to Receive")
fileName = '/src/Projects/Network_Design/Network_Design_Phases/NetworkDesign/Phase4_Attempt/Our Attempt/Received_Image.jpg'
file = open(fileName, 'wb')                                                 #opening a new file to copy the transferred image

receiverSequence = 0                                                       #Server side Sequence number is initialised to zero
loopTimes,address,receiverSequence = rdtReceivePacket(serverSocket,bufferSize,receiverSequence) #Receiving the file size from client
loop = struct.unpack("!I", loopTimes)[0]                                     #changing loop from byte to integer
print ("No. of Loops to send the entire file: ", loop)
print("Writing/Receiving process starting soon")                              #Receiving File from Client

for i in range(0,loop):                                                     #Loop to write entire transferred image in the new file, it runs 'loop' times
    print("Loop #:", i + 1)                                                     #Prints the Current loop. For easier way, initial print value starts from 1 (i+1, where i is 0)
    if(i >= (loop - 2)):                                                       #This is used to make sure corruption is not made at last loop, if not client or server keeps on waiting for ack/data.
        packetErrorProbability = 0                                                            #Error probability manually set to zero (No corruption) if true.
        packetDropProbability = 0                                                            #Packet Dropping probability manually set to zero (No corruption) if true.
    packet, address, receiverSequence = rdtReceivePacket(serverSocket,bufferSize,receiverSequence,packetErrorProbability,packetDropProbability)   #Calls the function rdtReceivePacket to receive the packet
    file.write(packet)                                                      #If packet received successful, It writes to the file
    i = i + 1                                                                   #Loop Iteration
#File Received from Client at the end of Loop

receivedFileSize = Functions.fileSize(file)                                 #Calculating Received Image file size

file.close()                                                                #closing the file
serverSocket.close()                                                                #closing the socket

end = time.time()                                                           #Finding the end-time
elapsedTime = end - start                                                 #Elapsed time
print ("Server: File Received\nReceived File size: {0}\nTime taken in Seconds: {1}".format(receivedFileSize,elapsedTime))

