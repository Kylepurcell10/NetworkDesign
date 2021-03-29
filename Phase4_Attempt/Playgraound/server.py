from Globals import*                                                        #Common variables
import Send_Receive                                                         #To Send/Receive function
import Functions                                                            #Functions like checksum, filesize, bit error, etc.

'''To corrupt acknowledgemnt packet, Set value from 0 - 99 in E_prob'''
E_Prob = 0                                                                  #E_Prob is the error probability and can be set from 0-99
P_Drop = 0                                                                  #P_Drop is the packet dropping probability and can be set from 0-99

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)                      #Socket with IPV4, UDP
sock.bind(addr)                                                             #Binding the socket
print("Server Started")

p = open('Received Image.jpg', 'wb')                                        #opening a new file to copy the transferred image

receiver_sequence = 0                                                       #Server side Sequence number is initialised to zero
loopTimes,address,receiver_sequence = Send_Receive.RdtReceivePkt(sock,buffer_size,receiver_sequence) #Receiving the file size from client
loop= struct.unpack("!I", loopTimes)[0]                                     #changing loop from byte to integer
print ("No. of Loops to send the entire file: ", loop)
print("write/Receiving process starting soon")                              #Receiving File from Client

for i in range(0,loop):                                                     #Loop to write entire transferred image in the new file, it runs 'loop' times
    print("Loop :",i+1)                                                     #Prints the Current loop. For easier way, initial print value starts from 1 (i+1, where i is 0)
    if(i>= (loop-2)):                                                       #This is used to make sure corruption is not made at last loop, if not client or server keeps on waiting for ack/data.
        E_Prob=0                                                            #Error probability manually set to zero (No corruption) if true.
        P_Drop=0                                                            #Packet Dropping probability manually set to zero (No corruption) if true.
    ImgPkt,address,receiver_sequence = Send_Receive.RdtReceivePkt(sock,buffer_size,receiver_sequence,E_Prob,P_Drop)   #Calls the function RdtReceivePkt to receive the packet
    p.write(ImgPkt)                                                         #If packet received successful, It writes to the file
    i=i+1                                                                   #Loop Iteration
#File Received from Client at the end of Loop

Received_File_Size = Functions.File_size(p)                                 #Calculating Received Image file size

p.close()                                                                   #closing the file
sock.close()                                                                #closing the socket

end = time.time()                                                           #Finding the end-time
Elapsed_time = end -  start                                                 #Elapsed time
print ("Server: File Received\nReceived File size: {0}\nTime taken in Seconds: {1}s".format(Received_File_Size,Elapsed_time))
