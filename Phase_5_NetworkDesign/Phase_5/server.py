import Functions                                                            #Functions like checksum, filesize, bit error, etc.
import socket
import struct
import time

start = time.time()                    #This is used to find the start time of the program, elapsed time can be found by end time - start time

'''Importing IP address, port number, Buffersize'''
IP = "127.0.0.1"                #Localhost is the IP address of this machine
Port = 20001                        #Port Number is assigned to 20001
bufferSize = 1024                     #bufferSize is set to 1024. packet size is 1024 with sequence number 1 byte, checksum 2 bytes, data 1021 bytes.
addr = (IP,Port)

'''For the GBN Sliding window, set the Window Size value'''
Window_Size = 5                        #Set the window size for the Go-Back-N protocol. This window size is only for the client program for the sliding window. Server side window size is always 1. client window size also included in server program ONLY to avoid intentional packet corrupt/drop for the last window.

'''This function is the basically the Server's RDT function to receive the file.'''
def rdtReceive (sock,bufferSize,Rx_seq_num,packetErrorProbability=0,packetDropProbability=0,loop=0,Window_Size = 0):
    packet_received = 0                                                                                 #Receive_sucessful is set to '0' initially

    while (not(packet_received)):                                                                       #loop goes on until condition becomes 'false'

        data, address = sock.recvfrom(bufferSize)                                                         #Packet is received from client

        if (Functions.errorCondition(packetDropProbability))and (Rx_seq_num< loop-Window_Size):                          #If Data_bit_error is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.Also, packet is not dropped for the last window.
          print ("############################ DATA PACKET DROPPED ################################\n")
          packet_received=0                                                                             #Comes out of current loop and starts again since condition will be while(1).

        else:                                                                                              #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            seq_num,checksum,Img_Pkt=Functions.extractData(data)                                           #Extracts the sequence number, checksum value, data from a packet

            if (Functions.errorCondition(packetErrorProbability)) and (Rx_seq_num< loop-Window_Size):                     #If Data_bit_error is true, it starts to corrupt packet intentionally.Also, ack packet is not corrupted for the last window.
                Img_Pkt = Functions.dataError(Img_Pkt)                                                  #Function to corrupt data
                print ("############################ Data Corrupted ################################\n")


            Rx_checksum = Functions.makeChecksum(Img_Pkt)                                                      #Receiver Checksum in integer

            if ((Rx_checksum == checksum) and (seq_num == Rx_seq_num)):                                    #if packet is not corrupted and has expected sequence number, sends Acknowledgement with sequence number  *updates sequence number for next loop
                    Ack = Rx_seq_num                                                                       #sends sequence number as ACK
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                                #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.makePacket(seq_num+1,Functions.makeChecksum(Ack),Ack)                  #Server sends Ack with expected Seq_num (Next Sequence Number), checksum, Ack
                    print("Sequence Number: {0},Receiver_sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seq_num,Rx_seq_num,checksum,Rx_checksum))
                    Rx_seq_num = 1 + seq_num                                                               #update sequence number to the next expected seqNum
                    packet_received = 1                                                                 #Comes out of while loop

            elif ((Rx_checksum != checksum) or (seq_num != Rx_seq_num)):                                   #if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
                    Ack = Rx_seq_num - 1                                                                   #last acked sequence numvber
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                                #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.makePacket(Rx_seq_num,Functions.makeChecksum(Ack),Ack)                 #Server sends Ack with Seq_num, checksum, Ack
                    #print("Sequence Number: {0},Receiver_sequence: {1}\n".format(seq_num,Rx_seq_num))
                    packet_received = 0                                                                 #Loop continues until satisfies condition
            sock.sendto(Sender_Ack,address)                                                                #sending the Acknowledgement packet to the client

    return Img_Pkt,address,Rx_seq_num                     
    
#To corrupt acknowledgemnt packet, Set one of these value to a number from 0 - 99
#packetErrorProbability controls the probability of a bit error within X% of packets
packetErrorProbability = 0
#packetDropProbability is the probability that a packet is dropped in the data transfer
packetDropProbability = 0

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)                      #Socket with IPV4, UDP
sock.bind(addr)                                                             #Binding the socket
print("Server Started")
filename = 'Received_Image.jpg'
file = open(filename, 'wb')                                        #opening a new file to copy the transferred image

receiver_sequence = 0                                                       #Server side Sequence number is initialised to zero
loopTimes,address,receiver_sequence = rdtReceive(sock,bufferSize,receiver_sequence) #Receiving the file size from client
loop= struct.unpack("!I", loopTimes)[0]                                     #changing loop from byte to integer
print ("No. of Loops to send the entire file: ", loop)
print("write/Receiving process starting soon")                              #Receiving File from Client

while receiver_sequence <= loop:
    ImgPkt,address,receiver_sequence = rdtReceive(sock,bufferSize,receiver_sequence,packetErrorProbability,packetDropProbability,loop,Window_Size)      #Calls the function rdtReceive to receive the packet
    file.write(ImgPkt)                                                         #writes/stores the received data to a file

#File Received from Client at the end of Loop

Received_File_Size = Functions.fileSize(file)                                 #Calculating Received Image file size

file.close()                                                                   #closing the file
sock.close()                                                                #closing the socket

end = time.time()                                                           #Finding the end-time
Elapsed_time = end -  start                                                 #Elapsed time
print ("Server: File Received\nReceived File size: {0}\nTime taken in Seconds: {1}s".format(Received_File_Size,Elapsed_time))

