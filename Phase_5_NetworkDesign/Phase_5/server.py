import Functions
import socket
import struct
import time

#This is used to find the start time of the program, elapsed time can be found by end time - start time
startTime = time.time()

#Local IP to be used in communications
IP = "127.0.0.1"
#Using port 20001
Port = 20001
#buffer of size 1024
bufferSize = 1024
#address is a combination of the IPaddress and the Port number
addr = (IP,Port)
#Set the window size for the Go-Back-N protocol. This window size is only for the client program for the sliding window. Server side window size is always 1. client window size also included in server program ONLY to avoid intentional packet corrupt/drop for the last window.
windowSize = 5


#this is the servers data receive function
def rdtReceive (receivingSocket,bufferSize,currentSequence,packetErrorProbability=0,packetDropProbability=0,numLoops=0,windowSize = 0):
    #Indicate that the packet has not been successfully received
    successfulReceive = 0                                                                                 

    #Loop until the paket has been received
    while (not(successfulReceive)):

        #Obtain the data from the client
        data, address = receivingSocket.recvfrom(bufferSize)                                                         

#If the probability of dropping a packet causes this "if" statement to render "true" then the packet will be discarded and will exit the loop
        if (Functions.errorCondition(packetDropProbability)) and (currentSequence < numLoops - windowSize):
          print ("Error: Packet Dropped\n")
          #Restarts the loop by recieving The correct data from the server
          successfulReceive=0

#This else statement will execute in all circumstances where the packet is not dropped
        else:
            #Extracts the sequence number, the checksum , and the client data
            packetSequence, checksum, clientPacketData = Functions.extractData(data)                                           

    #This statement will be true if the manually selected packet Error probability renders the statement true, then the actual image packet will be manually corrupted
    #using the dataError(packet) function
            if (Functions.errorCondition(packetErrorProbability)) and (currentSequence < numLoops - windowSize):
                #The actual corruption of data                     
                clientPacketData = Functions.dataError(clientPacketData)                                                  
                print ("Error: Data Corrupted\n")


    #determine the checksum from the packet that was sent
            ReceivedChecksum = Functions.makeChecksum(clientPacketData)                                                      

#if the packet has a matching checksum and sequence number, assign the corresponding ACK, create the checksum, and then send the repsonse to the client
            if ((ReceivedChecksum == checksum) and (packetSequence == currentSequence)):          
                #sends sequence number as ACK                          
                    Ack = currentSequence              
                    #Converting (Ack) from int to string and then encoding to bytes                                                         
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                            
                    #Server sends Ack with expected packetSequence (Next Sequence Number), checksum, Ack    
                    senderAck = Functions.makePacket(packetSequence+1,Functions.makeChecksum(Ack),Ack)                  
                    print("Sequence Number: {0},\nReceiver_sequence: {1},\nChecksum from Client: {2},\nChecksum for Received File: {3}\n".format(packetSequence,currentSequence,checksum,ReceivedChecksum))
                    #update the expected sequence
                    currentSequence = 1 + packetSequence    
                    #end the loop                                                       
                    successfulReceive = 1                                                                 

#if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
            elif ((ReceivedChecksum != checksum) or (packetSequence != currentSequence)):   
                 #last acked sequence number                                
                    Ack = currentSequence - 1                  
                    #Convert the Ack from int to string and then encoding to bytes
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                            
                    #Server sends the sequence number, the checksum, and the ackowledgement back to the client
                    senderAck = Functions.makePacket(currentSequence,Functions.makeChecksum(Ack),Ack)
                    #Loop continues until satisfies condition                 
                    successfulReceive = 0                       
                    #sending the Acknowledgement packet to the client                                          
            receivingSocket.sendto(senderAck,address)                                                               

    return clientPacketData,address,currentSequence                     
    
#To corrupt acknowledgemnt packet, Set one of these value to a number from 0 - 99
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
filename = 'Received_Image.jpg'
file = open(filename, 'wb')                                        

#Server side Sequence number is initialised to zero
receiverSequence = 0                                                       
#Receiving the amount of loop times required to transmit the data
loopTimes,address,receiverSequence = rdtReceive(serverSocket,bufferSize,receiverSequence) 
#convert the loopTime to an int
numLoops = struct.unpack("!I", loopTimes)[0]                                     
print ("No. of Loops to send the entire file: ", numLoops)
print("Reading from client...")
                            
#Program runs the data transfer 'numLoops' number of times
while receiverSequence <= numLoops:
    #Calls the function rdtReceive to receive the packet
    packet,address,receiverSequence = rdtReceive(serverSocket,bufferSize,receiverSequence,packetErrorProbability,packetDropProbability,numLoops,windowSize)      
    #writes/stores the received data to a file
    file.write(packet)                                                         

#File Received from Client at the end of Loop
#Calculating Received Image file size
receivedFileSize = Functions.fileSize(file)                                 

#closing the file
file.close()                                                                   
#closing the socket
serverSocket.close()                                                                
#Finding the end-time
endTime = time.time()                                                           
#Elapsed time
elapsedTime = endTime -  startTime                                                
print ("File Received\nReceived File size: {0}\nTime taken in Seconds: {1}s".format(receivedFileSize,elapsedTime))

