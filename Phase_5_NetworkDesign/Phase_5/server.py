import Functions                                                            #Functions like checksum, filesize, bit error, etc.
import socket
import struct
import time

startTime = time.time()                    #This is used to find the start time of the program, elapsed time can be found by end time - start time

'''Importing IP address, port number, Buffersize'''
IP = "127.0.0.1"                #Localhost is the IP address of this machine
Port = 20001                        #Port Number is assigned to 20001
bufferSize = 1024                     #bufferSize is set to 1024. packet size is 1024 with sequence number 1 byte, checksum 2 bytes, data 1021 bytes.
addr = (IP,Port)

'''For the GBN Sliding window, set the Window Size value'''
windowSize = 5                        #Set the window size for the Go-Back-N protocol. This window size is only for the client program for the sliding window. Server side window size is always 1. client window size also included in server program ONLY to avoid intentional packet corrupt/drop for the last window.

'''This function is the basically the Server's RDT function to receive the file.'''
def rdtReceive (receivingSocket,bufferSize,currentSequence,packetErrorProbability=0,packetDropProbability=0,numLoops=0,windowSize = 0):
    packet_received = 0                                                                                 #Receive_sucessful is set to '0' initially

    while (not(packet_received)):                                                                       #loop goes on until condition becomes 'false'

        data, address = receivingSocket.recvfrom(bufferSize)                                                         #Packet is received from client

        if (Functions.errorCondition(packetDropProbability)) and (currentSequence < numLoops - windowSize):                          #If Data_bit_error is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.Also, packet is not dropped for the last window.
          print ("Error: Packet Dropped\n")
          packet_received=0                                                                             #Comes out of current loop and starts again since condition will be while(1).

        else:                                                                                              #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            packetSequence, checksum, clientPacketData = Functions.extractData(data)                                           #Extracts the sequence number, checksum value, data from a packet

            if (Functions.errorCondition(packetErrorProbability)) and (currentSequence < numLoops - windowSize):                     #If Data_bit_error is true, it starts to corrupt packet intentionally.Also, ack packet is not corrupted for the last window.
                clientPacketData = Functions.dataError(clientPacketData)                                                  #Function to corrupt data
                print ("Error: Data Corrupted\n")


            ReceivedChecksum = Functions.makeChecksum(clientPacketData)                                                      #Receiver Checksum in integer

            if ((ReceivedChecksum == checksum) and (packetSequence == currentSequence)):                                    #if packet is not corrupted and has expected sequence number, sends Acknowledgement with sequence number  *updates sequence number for next loop
                    Ack = currentSequence                                                                       #sends sequence number as ACK
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                                #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.makePacket(packetSequence+1,Functions.makeChecksum(Ack),Ack)                  #Server sends Ack with expected packetSequence (Next Sequence Number), checksum, Ack
                    print("Sequence Number: {0},\nReceiver_sequence: {1},\nChecksum from Client: {2},\nChecksum for Received File: {3}\n".format(packetSequence,currentSequence,checksum,ReceivedChecksum))
                    currentSequence = 1 + packetSequence                                                               #update sequence number to the next expected seqNum
                    packet_received = 1                                                                 #Comes out of while loop

            elif ((ReceivedChecksum != checksum) or (packetSequence != currentSequence)):                                   #if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
                    Ack = currentSequence - 1                                                                   #last acked sequence numvber
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                                #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.makePacket(currentSequence,Functions.makeChecksum(Ack),Ack)                 #Server sends Ack with packetSequence, checksum, Ack
                    #print("Sequence Number: {0},Receiver_sequence: {1}\n".format(packetSequence,currentSequence))
                    packet_received = 0                                                                 #Loop continues until satisfies condition
            receivingSocket.sendto(Sender_Ack,address)                                                                #sending the Acknowledgement packet to the client

    return clientPacketData,address,currentSequence                     
    
#To corrupt acknowledgemnt packet, Set one of these value to a number from 0 - 99
#packetErrorProbability controls the probability of a bit error within X% of packets
packetErrorProbability = 0
#packetDropProbability is the probability that a packet is dropped in the data transfer
packetDropProbability = 0

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)                      #Socket with IPV4, UDP
serverSocket.bind(addr)                                                             #Binding the socket
print("Server Started")
filename = 'C:/src/Projects/Network_Design/Network_Design_Phases/NetworkDesign/Phase_5_NetworkDesign/Phase_5/Received_Image.jpg'
file = open(filename, 'wb')                                        #opening a new file to copy the transferred image

receiverSequence = 0                                                       #Server side Sequence number is initialised to zero
loopTimes,address,receiverSequence = rdtReceive(serverSocket,bufferSize,receiverSequence) #Receiving the file size from client
numLoops = struct.unpack("!I", loopTimes)[0]                                     #changing loop from byte to integer
print ("No. of Loops to send the entire file: ", numLoops)
print("write/Receiving process starting soon")                              #Receiving File from Client

while receiverSequence <= numLoops:
    packet,address,receiverSequence = rdtReceive(serverSocket,bufferSize,receiverSequence,packetErrorProbability,packetDropProbability,numLoops,windowSize)      #Calls the function rdtReceive to receive the packet
    file.write(packet)                                                         #writes/stores the received data to a file

#File Received from Client at the end of Loop

receivedFileSize = Functions.fileSize(file)                                 #Calculating Received Image file size

file.close()                                                                   #closing the file
serverSocket.close()                                                                #closing the socket

endTime = time.time()                                                           #Finding the end-time
elapsedTime = endTime -  startTime                                                #Elapsed time
print ("Server: File Received\nReceived File size: {0}\nTime taken in Seconds: {1}s".format(receivedFileSize,elapsedTime))

