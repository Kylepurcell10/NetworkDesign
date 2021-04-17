import Functions                                                   
import socket
import struct
import time

startTime = time.time()                    
#Local IP to be used in communications
IP = "127.0.0.1"
#Using port 20001
Port = 20001
#buffer of size 1024
bufferSize = 1024
#address is a combination of the IPaddress and the Port number
addr = (IP,Port)

'''For the GBN Sliding window, set the Window Size value'''
windowSize = 5                        #Set the window size for the Go-Back-N protocol. This window size is only for the client program for the sliding window. Server side window size is always 1. client window size also included in server program ONLY to avoid intentional packet corrupt/drop for the last window.

'''This function is the basically the client's RDT function to send the file.'''

def rdtSend(file,sendingSocket,addr,seqNum,data,packetErrorProbability=0,packetDropProbability=0,windowSize=0,base=0,loop=0,imageBuffer=[],timeBuffer=[]):

    if (seqNum < (base+windowSize)):                                                                #check for empty slots in the windows
        while ((seqNum < base+windowSize) and (seqNum <= loop)):                                  #condition for GBN protocol (Sliding window)
            if (seqNum > 0):                                                                         #Initially file size is sent through sequence number 0
                data = file.read(bufferSize-4)                                                           #print("File Read")
            packet = Functions.makePacket(seqNum,Functions.makeChecksum(data),data)                         #Packet is created with the sequence number,checksum,data
            imageBuffer[seqNum % windowSize] = packet                                              #Buffer size of window size is created and data is added to the buffer.
            sendingSocket.sendto(packet,addr)                                                               #sends the data
            print ("Packet# Sliding Window: ",seqNum)
            timeBuffer[seqNum % windowSize] = time.time()                                          #Time Buffer stores the start time for each packet
            seqNum+=1                                                                                #sequence numbe is updated by 1
        print ("Timer Started")
    try:                                                                                               #This is used for timer. if timed-out, it comes out of try loop and goes to exception.
        sendingSocket.settimeout(0.03)                                                                      #UDP Socket timer is added here, In this case 30 milliseconds is set as timer.If timed-out before operation, it goes to the timer exception.
        ACKPacket,addr = sendingSocket.recvfrom(bufferSize)                                                  #Client receiving the Acknowledgement packet
        sendingSocket.settimeout(None)                                                                      #It is equivalent to sock.setblocking(0), timer is actived only for receive function which takes care of entire operation according to the FSM.

        if (Functions.errorCondition(packetDropProbability)) and (seqNum< loop-windowSize):                       #If Data_bit_error is true, it starts to Drop packet intentionally ! Basically The received packet not utilised/used. Also, ack packet is not dropped for the last window.
            while(time.time() < (timeBuffer[base % windowSize] + 0.03)):                             #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                pass
            print ("ERROR: ACKNOWLEDGEMENT PACKET DROPPED\n")
            #raise OSError                                                                             #raise OSError
        else:                                                                                          #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            packetSeqNum,senderChecksum,ACKData=Functions.extractData(ACKPacket)                         #Extracts the sequence number, checksum value, data from a packet

            if (Functions.errorCondition(packetErrorProbability)) and (seqNum< loop-windowSize):                   #If Data_bit_error is true, it starts to corrupt data intentionally. Also last window packets are not corrupted.
                ACKData = Functions.dataError(ACKData)                                            #Function to corrupt data
                print ("ERROR: ACK CORRUPTED ")

            ACKChecksum = Functions.makeChecksum(ACKData)                                                #Finds the checksum for received acknowledgement
            ACKData = ACKData.decode("UTF-8")                                                        #Decodes from byte to integer for the comparison
            ACKDataInt = int(ACKData[3:len(ACKData)])                                              #Gets the integer value alone from the ACK. for example, if string 'ACK500' is the input then the output will be integer of 500
            #print ("Ack from Server: ",ACKDataInt)

            '''Comparing Acknowledgement'''
            if (ACKDataInt >= base) and (ACKChecksum == senderChecksum ):                           #if packet is not corrupted and has expected sequence number
                base=ACKDataInt +1                                                                   #base value is the next value to the ack value
                print ("ACK Verified, ACK Data: ", ACKData)
                print ("Updated Base: ", base)
                print ("Timer has Stopped\n")

            elif (ACKChecksum != senderChecksum ):                                                     #if packet is corrupted, it resends the packet
                print ("ACK is not Verified:{} \n".format(ACKData))                                          #Do Nothing

    except (socket.timeout,OSError):
        print ("ERROR: SOCKET TIMED OUT ")
        print ("Base: ",base)
        for i in range (base,seqNum):                                                                #Resends the entire packet
            timeBuffer[i % windowSize] = time.time()                                                 #Restarting the timer, updating start time for the packet
            sendingSocket.sendto(imageBuffer[i % windowSize],addr)                                        #Sending the data
            print ("Sending the packet: ",i)
        print ("\n")
    return seqNum,base                                                                                   #returns updated sequence number, base value


#To corrupt data packet, Set one of these value to a number from 0 - 99
#packetErrorProbability controls the probability of a bit error within X% of packets
packetErrorProbability = 20
#packetDropProbability is the probability that a packet is dropped in the data transfer
packetDropProbability = 0

timeBuffer=[None]*windowSize                                      #timeBuffer stores the start time for the packets
print ("Window Size: ",windowSize)                                 #prints the window size
imageBuffer=[None]*windowSize                                     #Stores the data in the buffer
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              #Socket with IPV4, UDP
filename = 'C:/src/Projects/Network_Design/Network_Design_Phases/NetworkDesign/Phase_5_NetworkDesign/Phase_5/Trash.bmp'
file = open(filename,'rb')                                           #opening a new file, this file will be transferred to the server

fileSize = Functions.fileSize(file)                                   #File size is calculated

loop = Functions.looptimes(fileSize,bufferSize)                    #finding the loop value
loopBytes = struct.pack("!I", loop)                                #change loop from integer to byte inorder to send data from client to server
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
seqNum = 0                                                        #Sequence Number is set to 0 initially
base=0                                                              #Here base is set to 0
print('Client File Transfer Starts...')

while (base <= loop):                                               #Loop runs until sequence number is equal to loop value. Sequence number starts from 1.
    seqNum,base = rdtSend(file,clientSocket,addr,seqNum,loopBytes,packetErrorProbability,packetDropProbability,windowSize,base,loop,imageBuffer,timeBuffer) #calls the function rdt_send to send the packet

#Close the file
file.close()
#Close the socket
clientSocket.close()

endTime = time.time()                                                   #Gets the End time
elapsedTime = endTime - startTime                                          #Gets the elapsed time
print ("Client: File Sent\nFile size sent to server: {0}\nTime taken in Seconds:{1}s\n".format(fileSize,elapsedTime))