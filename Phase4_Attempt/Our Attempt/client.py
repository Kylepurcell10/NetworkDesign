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

#Function used to implement the rdt send
def rdtSendPacket(clientSocket,addr,sendSeqNum,data,packetErrorProbability=0,packetDropProbability=0):
    successfulSend = 0                                                                     #send_sucessful is set to '0' initially
    packet = Functions.makePacket(sendSeqNum,Functions.checksum(data),data)                      #Packet is created with the sequence number,checksum,data

    while (not(successfulSend)):                                                           #loop goes on until condition becomes 'false'

        clientSocket.sendto(packet,addr)                                                        #sending the packet to server
        print ("Sending the Packet...")
        startTime = time.time()                                                            #startTime gives the starting time for the timer

        clientSocket.settimeout(0.03)                                                           #UDP Socket timer is added here, In this case 30 milliseconds is set as timer.If timed-out before operation, it goes to the timer exception.
        try:                                                                                #This is used for timer. if timed-out, it comes out of try loop and goes to exception.
            print ("Timer Started.")
            ACKPacket,addr = clientSocket.recvfrom(bufferSize)                                   #Client receiving the Acknowledgement packet
            clientSocket.settimeout(None)                                                       #It is equivalent to sock.setblocking(0), timer is actived only for receive function which takes care of entire operation according to the FSM.

            if (Functions.errorCondition(packetDropProbability)):                                         #If dataBitError is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.
                print ("Acknowledgement Packet Dropped")
                while(time.time() < (startTime + 0.03)):                                   #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                            pass
                print ("Timed Out. \n")
                successfulSend = 0                                                         #Comes out of current loop and starts again since condition will be while(1).

            else:                                                                           #If dataBitError is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
                packetSeqNum,senderChecksum,ACKData=Functions.extractData(ACKPacket)          #Extracts the sequence number, checksum value, data from a packet

                if (Functions.errorCondition(packetErrorProbability)):                                     #If dataBitError is true, it starts to corrupt data intentionally
                        ACKData = Functions.corruptData(ACKData)                         #Function to corrupt data
                        print ("ACK Corrupted.")

                refrenceAck ="ACK"+str(sendSeqNum)                                            #This is the referenced Acknowledgement with respect to the sequence number. (string "ACK" also added to the sequence number for user convention and to avoid confusion)
                ACKChecksum = Functions.checksum(ACKData)                                 #Finds the checksum for received acknowledgement
                ACKData = ACKData.decode("UTF-8")                                         #Decodes from byte to integer for the comparison

                #Comparing Acknowledgement
                if (ACKData != refrenceAck) or (ACKChecksum != senderChecksum ):           #if packet is corrupted or has unexpected acknowledgement it resends the packet
                        print ("ACK: {0}, Sequence #: {1}".format(ACKData,sendSeqNum))
                        print("Resending the Packet")
                        successfulSend = 0                                                 #Loop continues until satisfies condition, Basically resends the packet.
                        while(time.time() < (startTime + 0.03)):                           #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                            pass
                        print ("Timed Out. \n")


                elif (ACKData == refrenceAck) and (ACKChecksum == senderChecksum ):        #if packet is not corrupted and has expected acknowledgement it does nothing. *updates sequence number for next loop
                        print ("ACK: {0}, Sequence #: {1}".format(ACKData,sendSeqNum))
                        sendSeqNum = 1 - sendSeqNum                                               #updating sequence number
                        successfulSend = 1                                                 #Comes out of while loop.
                        print ("Timer Stopped.")

        except(socket.timeout):
            print ("Timed Out. \n")
            successfulSend = 0                                                               #Comes out of current loop and starts again since condition will be while(1).

    return sendSeqNum                                                                         #returns updated sequence number


#To corrupt data packet, Set value from 0 - 99 in packetErrorProbability
packetErrorProbability = 0                                                        #packetErrorProbability is the error probability and can be set from 0-99
packetDropProbability = 0                                                          #packetDropProbability is the packet dropping probability and can be set from 0-99

clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              #Socket with IPV4, UDP
f = open('/src/Projects/Network_Design/Network_Design_Phases/NetworkDesign/Phase4_Attempt/Our Attempt/Trash.bmp','rb')                                          #opening a new file, this file will be transferred to the server
#change to abolsute path

fileSize = Functions.fileSize(f)                                   #File size is calculated

loop = Functions.looptimes(fileSize,bufferSize)                    #finding the loop value
loop_bytes = struct.pack("!I", loop)                                #change loop from integer to byte inorder to send data from client to server
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
sendSeqNum = 0                                                        #Sequence Number is set to 0 initially
sendSeqNum = rdtSendPacket(clientSocket,addr,sendSeqNum,loop_bytes)   #sending the file size to Server


print('Client File Transfer Starts...')

for i in range(0,loop):                                             #it runs 'loop' times
    print("\nLoop :",i + 1)                                           #Prints the Current loop. For easier way, initial print value starts from 1 (i+1, where i is 0)
    ImgPkt = f.read(bufferSize - 3)                                  #reading the file, 1021 bytes at a time.
    if(i >= (loop - 2)):                                               #This is used to make sure corruption is not made at last loop, if not client or server keeps on waiting for ack/data.
        packetErrorProbability = 0                                                    #Error probability manually set to zero (No corruption) if true.
        packetDropProbability = 0                                                    #Packet Dropping probability manually set to zero (No corruption) if true.
    sendSeqNum = rdtSendPacket(clientSocket,addr,sendSeqNum,ImgPkt,packetErrorProbability,packetDropProbability)    #calls the function rdt_send to send the packet
    i = i + 1                                                           #Loop iteration

f.close()                                                           #File closed
clientSocket.close()                                                        #Socket Closed

end = time.time()                                                   #Gets the End time

