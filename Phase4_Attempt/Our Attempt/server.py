import socket
import math
import random
import struct
import time
import Functions
from Globals import*
import Send_Receive


def RdtReceivePkt (sock,buffer_size,Rx_seq_num,E_Prob=0,P_Drop=0):
    receive_successful = 0                                                                  #Receive_sucessful is set to '0' initially
    while (not(receive_successful)):                                                        #loop goes on until condition becomes 'false'

        data, address = sock.recvfrom(buffer_size)                                          #Packet is received from client

        if (Functions.Error_Condition(P_Drop)):                                             #If Data_bit_error is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.
          print ("DATA PACKET DROPPED\n")
          receive_successful=0                                                              #Comes out of current loop and starts again since condition will be while(1).

        else:                                                                               #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            seq_num,checksum,Img_Pkt=Functions.ExtractData(data)                            #Extracts the sequence number, checksum value, data from a packet

            if (Functions.Error_Condition(E_Prob)):                                         #If Data_bit_error is true, it starts to corrupt packet intentionally
                Img_Pkt = Functions.Data_Corrupt(Img_Pkt)                                   #Function to corrupt data
                print ("\nData Corrupted")


            Rx_checksum = Functions.checksum(Img_Pkt)                                       #Receiver Checksum in integer

            if ((Rx_checksum == checksum) and (seq_num == Rx_seq_num)):                     #if packet is not corrupted and has expected sequence number, sends Acknowledgement with sequence number  *updates sequence number for next loop
                    Ack = Rx_seq_num                                                        #sends sequence number
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                 #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.MakePkt(seq_num,Functions.checksum(Ack),Ack)     #Server sends Ack with Seq_num, checksum, Ack
                    print("Sequence Number: {0},Receiver_sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seq_num,Rx_seq_num,checksum,Rx_checksum))
                    Rx_seq_num = 1-seq_num                                                  #update sequence number to the next expected seqNum
                    receive_successful = 1                                                  #Comes out of while loop

            elif ((Rx_checksum != checksum) or (seq_num != Rx_seq_num)):                    #if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
                    Ack = 1 - Rx_seq_num                                                    #last acked sequence numvber
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                 #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.MakePkt(1 - Rx_seq_num,Functions.checksum(Ack),Ack) #Server sends Ack with Seq_num, checksum, Ack
                    print("Server Requested to Resend the Packet")
                    print("Sequence Number: {0},Receiver_sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seq_num,Rx_seq_num,checksum,Rx_checksum))
                    receive_successful = 0                                                  #Loop continues until satisfies condition
            sock.sendto(Sender_Ack,address)                                                 #sending the Acknowledgement packet to the client

    return Img_Pkt,address,Rx_seq_num

'''To corrupt acknowledgemnt packet, Set value from 0 - 99 in E_prob'''
packetErrorProbability = 0                                                  #E_Prob is the error probability and can be set from 0-99
packetDropProbability = 0                                                   #P_Drop is the packet dropping probability and can be set from 0-99

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)                      #Socket with IPV4, UDP
sock.bind(addr)                                                             #Binding the socket
print("Server Started")
fileName = 'Received_Image.jpg'
file = open(fileName, 'wb')                                                 #opening a new file to copy the transferred image

receiver_sequence = 0                                                       #Server side Sequence number is initialised to zero
loopTimes,address,receiver_sequence = Send_Receive.RdtReceivePkt(sock,buffer_size,receiver_sequence) #Receiving the file size from client
loop= struct.unpack("!I", loopTimes)[0]                                     #changing loop from byte to integer
print ("No. of Loops to send the entire file: ", loop)
print("write/Receiving process starting soon")                              #Receiving File from Client

for i in range(0,loop):                                                     #Loop to write entire transferred image in the new file, it runs 'loop' times
    print("Loop :",i+1)                                                     #Prints the Current loop. For easier way, initial print value starts from 1 (i+1, where i is 0)
    if(i>= (loop-2)):                                                       #This is used to make sure corruption is not made at last loop, if not client or server keeps on waiting for ack/data.
        packetErrorProbability=0                                                            #Error probability manually set to zero (No corruption) if true.
        packetDropProbability=0                                                            #Packet Dropping probability manually set to zero (No corruption) if true.
    packet, address, receiver_sequence = Send_Receive.RdtReceivePkt(sock,buffer_size,receiver_sequence,packetErrorProbability,packetDropProbability)   #Calls the function RdtReceivePkt to receive the packet
    file.write(packet)                                                      #If packet received successful, It writes to the file
    i=i+1                                                                   #Loop Iteration
#File Received from Client at the end of Loop

Received_File_Size = Functions.File_size(file)                                 #Calculating Received Image file size

file.close()                                                                #closing the file
sock.close()                                                                #closing the socket

end = time.time()                                                           #Finding the end-time
Elapsed_time = end -  start                                                 #Elapsed time
print ("Server: File Received\nReceived File size: {0}\nTime taken in Seconds: {1}s".format(Received_File_Size,Elapsed_time))

