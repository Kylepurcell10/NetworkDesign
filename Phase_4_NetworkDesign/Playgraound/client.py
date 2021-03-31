from Globals import *                                               #Common variables
import Functions                                                    #Functions like checksum, filesize, bit error, etc.
import Send_Receive                                                 #To Send/Receive function

'''To corrupt data packet, Set value from 0 - 99 in E_prob'''
E_Prob = 0                                                          #E_prob is the error probability and can be set from 0-99
P_Drop = 0                                                          #P_Drop is the packet dropping probability and can be set from 0-99

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              #Socket with IPV4, UDP
f = open('Lion.jpg','rb')                                           #opening a new file, this file will be transferred to the server

fileSize = Functions.File_size(f)                                   #File size is calculated

loop = Functions.looptimes(fileSize,buffer_size)                    #finding the loop value
loop_bytes = struct.pack("!I", loop)                                #change loop from integer to byte inorder to send data from client to server
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
seq_nmbr = 0                                                        #Sequence Number is set to 0 initially
seq_nmbr = Send_Receive.RdtSendPkt(sock,addr,seq_nmbr,loop_bytes)   #sending the file size to Server

print('Client File Transfer Starts...')

for i in range(0,loop):                                             #it runs 'loop' times
    print("\nLoop :",i+1)                                           #Prints the Current loop. For easier way, initial print value starts from 1 (i+1, where i is 0)
    ImgPkt = f.read(buffer_size-3)                                  #reading the file, 1021 bytes at a time.
    if(i>= (loop-2)):                                               #This is used to make sure corruption is not made at last loop, if not client or server keeps on waiting for ack/data.
        E_Prob=0                                                    #Error probability manually set to zero (No corruption) if true.
        P_Drop=0                                                    #Packet Dropping probability manually set to zero (No corruption) if true.
    seq_nmbr = Send_Receive.RdtSendPkt(sock,addr,seq_nmbr,ImgPkt,E_Prob,P_Drop)    #calls the function rdt_send to send the packet
    i=i+1                                                           #Loop iteration

f.close()                                                           #File closed
sock.close()                                                        #Socket Closed

end = time.time()                                                   #Gets the End time
Elapsed_time = end - start                                          #Gets the elapsed time
print ("Client: File Sent\nFile size sent to server: {0}\nTime taken in Seconds:{1}s\n".format(fileSize,Elapsed_time))
