import socket
import math
import random
import struct
import time
import Functions

#Start the timer to see how long the program takes to execute
start = time.time()

#Local IP to be used in communications
IP = "127.0.0.1"
#Using port 20001
Port = 20001
#buffer of size 1024
bufferSize = 1024
#address is a combination of the IPaddress and the Port number
addr = (IP,Port)


def rdtReceive (serverSocket,bufferSize,receiveSeqNum,packetErrorProbability = 0,packetDropProbability = 0):
    #this will be the loop identifier, determines if the transfer is complete and if the loop will end
    successfulReceive = 0
    while (not(successfulReceive)):

        #Receive the packet from the client
        data, address = serverSocket.recvfrom(bufferSize)

    #If the probability of dropping a packet causes this If statement to render "true" then the packet will be discarded and will exit the loop
        if (Functions.errorCondition(packetDropProbability)):
          print ("Data Packet Dropped\n")
          #Restarts the loop by recieving The correct data from the server
          successfulReceive = 0

    #This else statement will execute in all circumstances where the packet is not dropped
        else:
            #Extracts the sequence number, the checksum , and the image packet
            seqNum, makeChecksum, imagePacket = Functions.extractData(data)

    #This statement will be true if the manually selected packet Error probability renders the statement true, then the actual image packet will be manually corrupted
    #using the dataError(packet) function
            if (Functions.errorCondition(packetErrorProbability)):
                #The actual corruption of data
                imagePacket = Functions.dataError(imagePacket)
                print ("\nData Corrupted")


            #determine the checksum from the packet that was sent
            receiverChecksum = Functions.makeChecksum(imagePacket)

        #if the packet has a matching checksum and sequence number, assign the corresponding ACK, create the checksum, and then send the repsonse to the client
            if ((receiverChecksum == makeChecksum) and (seqNum == receiveSeqNum)):
                #identify the ackowledgement
                    Ack = receiveSeqNum
                    #Convert the Ack from int to string and then encoding to bytes
                    Ack = b'ACK' + str(Ack).encode("UTF-8")
                    #Server sends the sequence number, the checksum, and the ackowledgement back to the client
                    senderACK = Functions.makePacket(seqNum,Functions.makeChecksum(Ack),Ack)
                    print("Sequence #: {0}, Receiver Sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seqNum,receiveSeqNum,makeChecksum,receiverChecksum))
                    #update the expected sequence
                    receiveSeqNum = 1 - seqNum
                    #end the loop
                    successfulReceive = 1

        #If the packet is in fact corrupted(wrong checksum or wrong sequence number), send back the ack for the previous packet and request the data again
            elif ((receiverChecksum != makeChecksum) or (seqNum != receiveSeqNum)):
                #last acked sequence numvber
                    Ack = 1 - receiveSeqNum
                    #Convert the Ack from int to string and then encoding to bytes
                    Ack = b'ACK' + str(Ack).encode("UTF-8")
                    #Server sends the sequence number, the checksum, and the ackowledgement back to the client
                    senderACK = Functions.makePacket(1 - receiveSeqNum,Functions.makeChecksum(Ack),Ack)
                    print("Server Requested to Resend the Packet")
                    print("Sequence #: {0}, Receiver Sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seqNum,receiveSeqNum,makeChecksum,receiverChecksum))
                    #Loop continues until satisfies condition
                    successfulReceive = 0
                    #sending the Acknowledgement packet to the client
            serverSocket.sendto(senderACK,address)

    return imagePacket,address,receiveSeqNum

#To corrupt data packet, Set one of these value to a number from 0 - 99
#packetErrorProbability controls the probability of a bit error within X% of packets
packetErrorProbability = 0
#packetDropProbability is the probability that a packet is dropped in the data transfer
packetDropProbability = 0

#Create the actual socket itself
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#Bind the socket to the address (IP and port)
serverSocket.bind(addr)
print("Server Ready to Receive")

#open the file that is going to be written into from the data coming from the client
fileName = 'Received_Image.jpg'
file = open(fileName, 'wb')

#Server side Sequence number is initialised to zero
receiverSequence = 0
 #Receiving the amount of loop times required to transmit the data
loopTimes, address, receiverSequence = rdtReceive(serverSocket,bufferSize,receiverSequence)
#convert the loopTime to an int
loop = struct.unpack("!I", loopTimes)[0]
print ("No. of Loops to send the entire file: ", loop)
print("Reading from client...")

#Program runs the data transfer 'loop' number of times
for i in range(0,loop):
    #Prints the current loop number
    print("Loop #:", i + 1)
    #This loop is only here to ensure that corruption doesnt happen on the last two packets otherwise the sockets could fail or stall
    if(i >= (loop - 2)):
        packetErrorProbability = 0
        packetDropProbability = 0
        #Recieve the packet
    packet, address, receiverSequence = rdtReceive(serverSocket,bufferSize,receiverSequence,packetErrorProbability,packetDropProbability)
    #If the packet was good it will be written to the file
    file.write(packet)
    #Iterate the loop
    i = i + 1


#Calculating Received Image file size
receivedFileSize = Functions.fileSize(file)

#Close the file
file.close()
#close the socket
serverSocket.close()

#find the time at the end of the transfer
end = time.time()
#Calculate the total time it took for the entire transfer
elapsedTime = end - start
print ("Server: File Received\nReceived File size: {0}\nTime taken in Seconds: {1}".format(receivedFileSize,elapsedTime))

