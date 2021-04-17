import Functions                                                   
import socket
import struct
import time

#Start the timer to see how long the program takes to execute for client side
startTime = time.time()  

#Local IP to be used in communications
IP = "127.0.0.1"
#Using port 20001
Port = 20001
#buffer of size 1024
bufferSize = 1024
#address is a combination of the IPaddress and the Port number
addr = (IP,Port)

#Set the window size for the Go-Back-N protocol for the client side
windowSize = 5                      

#Function that handles the sending of packets to the server and receiving the ackowledgement data back
def rdtSend(file,clientSocket,addr,senderSeqNum,data,packetErrorProbability=0,packetDropProbability=0,windowSize=0,base=0,loop=0,imageBuffer=[],timeBuffer=[]):

    #Checks windows for empty slots
    if (senderSeqNum < (base + windowSize)):

        #This is the condition for the GBN                                                         
        while ((senderSeqNum < base+windowSize) and (senderSeqNum <= loop)): 

            #This will send the file size thru the first sequence number                                
            if (senderSeqNum > 0):                                                                         
                data = file.read(bufferSize-4) 

            #Creates the packet                                                       
            packet = Functions.makePacket(senderSeqNum,Functions.makeChecksum(data),data)  

            #Creates the window using the buffer size and adds the data
            imageBuffer[senderSeqNum % windowSize] = packet     

            #Sends the packet
            clientSocket.sendto(packet,addr)                                                            
            print ("Packet # Sliding Window: ",senderSeqNum)

            #startTime is stored in timeBuffer for each packet
            timeBuffer[senderSeqNum % windowSize] = time.time() 

            #Sequence number incremented                                   
            senderSeqNum+=1                                                                              
        print ("Timer Started")
    try:                           

        #Set the timeout value for the socket to be 0.03 seconds                                                                  
        clientSocket.settimeout(0.03)  

        #Get the ackowledgement from the server                                                              
        ACKPacket,addr = clientSocket.recvfrom(bufferSize)    
        
        #Timer is active only for receive function which takes care of the entire operation                                              
        clientSocket.settimeout(None)                                                                     

        if (Functions.errorCondition(packetDropProbability)) and (senderSeqNum< loop-windowSize):
            #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
            while(time.time() < (timeBuffer[base % windowSize] + 0.03)):                          
                pass
            #If dataBitError is true a packet will be dropped at the rate of the variable packetDropProbability and the sequence number is greater than the window size
            #This will force it out of the loop and discard the packet
            print ("ERROR: Acknowledgement Packet Dropped\n")

        #this statement will execute if a packet was not intentionally dropped                                                                              
        else:
            #get the packets respective sequence number, its checksum, and its ackowledgement                                                                                          
            packetSeqNum,senderChecksum,ACKData=Functions.extractData(ACKPacket)                         #Extracts the sequence number, checksum value, data from a packet

            #If there is user predefined data bit errors, the function will modift the ackowledgement and the sequence number is greater than the window size.
            if (Functions.errorCondition(packetErrorProbability)) and (senderSeqNum< loop-windowSize):  
                 #function to actually corrupt the data                
                ACKData = Functions.dataError(ACKData)                                            
                print ("ERROR: ACK Corrupted. ")
            
            #Finds the checksum using the corrupted received acknowledgement
            ACKChecksum = Functions.makeChecksum(ACKData)
            #Decodes from byte to integer for the comparison                                                
            ACKData = ACKData.decode("UTF-8")  
            #Gets the integer value from ACK
            ACKDataInt = int(ACKData[3:len(ACKData)])                                            

            #If theres nothing wrong with the packet, print to the screen the ackowledgement and then update the sequence number
            if (ACKDataInt >= base) and (ACKChecksum == senderChecksum ):                        
                base=ACKDataInt +1                                                                 
                print ("ACK Verified, ACK Data: ", ACKData)
                print ("Updated Base: ", base)
                print ("Timer has Stopped\n")

            #if packet is corrupted, it resends the packet
            elif (ACKChecksum != senderChecksum):                                                     
                print ("{} is not acknowledged \n".format(ACKData))                                       

    except (socket.timeout,OSError):
        print ("ERROR: Socket Timed Out.  ")
        print ("Base is still: ",base)
        #Resends packet
        for i in range (base,senderSeqNum):        
            #This restarts the time and updates the start time for the packet                                   
            timeBuffer[i % windowSize] = time.time()           
            #Sends the data                                   
            clientSocket.sendto(imageBuffer[i % windowSize],addr)             
            print ("Sending the packet: ",i)
        print ("\n")\
    #returns updated sequence number and base value
    return senderSeqNum,base                                                                                   


#To corrupt data packet, Set one of these value to a number from 0 - 99
#packetErrorProbability controls the probability of a bit error within X% of packets
packetErrorProbability = 0
#packetDropProbability is the probability that a packet is dropped in the data transfer
packetDropProbability = 0

#timeBuffer stores the start time for the packets
timeBuffer=[None]*windowSize  
#Prints the window size                                     
print ("Window Size: ",windowSize)   
#Stores the data in the buffer                          
imageBuffer=[None]*windowSize   
#Create the actual socket itself             
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)     

#Open the file that is going to be transfered
filename = 'C:/src/Projects/Network_Design/Network_Design_Phases/NetworkDesign/Phase_5_NetworkDesign/Phase_5/cat.bmp'
file = open(filename,'rb')                                      

#Calculate the size of the file
fileSize = Functions.fileSize(file)                                  

#determine how many times a packet will need to be sent in order for the file to be completely transfered
loop = Functions.looptimes(fileSize,bufferSize)   
#change loop from integer to byte in order to send data from client to server               
loopBytes = struct.pack("!I", loop)                               
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
#Sequence Number is set to 0 initially
senderSeqNum = 0    
#Base is set to 0 initially                                              
base = 0                                                              
print('Client File Transfer Starts...')

#Loop runs until sequence number is equal to loop value. Sequence number starts from 1.
while (base <= loop):                                              
    #Calls the function rdtSend to send the packet
    senderSeqNum,base = rdtSend(file,clientSocket,addr,senderSeqNum,loopBytes,packetErrorProbability,packetDropProbability,windowSize,base,loop,imageBuffer,timeBuffer) 

#Close the file
file.close()
#Close the socket
clientSocket.close()

#find the time at the end of the transfer
endTime = time.time() 
#Calculate the total time it took for the entire transfer                                                  
elapsedTime = endTime - startTime                                          
print ("Client: File Sent\nFile size sent to server: {0}\nTime taken in Seconds:{1}s\n".format(fileSize,elapsedTime))