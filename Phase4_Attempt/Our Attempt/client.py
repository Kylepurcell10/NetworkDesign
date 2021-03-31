import socket
import math
import random
import struct
import time
import Functions
import Send_Receive
from Globals import*

#Function used to implement the rdt send
def RdtSendPkt(udp_sock,addr,seq_nmbr,data,E_Prob=0,P_Drop=0):
    send_successful = 0                                                                     #send_sucessful is set to '0' initially
    packet = Functions.MakePkt(seq_nmbr,Functions.checksum(data),data)                      #Packet is created with the sequence number,checksum,data

    while (not(send_successful)):                                                           #loop goes on until condition becomes 'false'

        udp_sock.sendto(packet,addr)                                                        #sending the packet to server
        print ("Sending the Packet...")
        start_time = time.time()                                                            #Start_time gives the starting time for the timer

        udp_sock.settimeout(0.03)                                                           #UDP Socket timer is added here, In this case 30 milliseconds is set as timer.If timed-out before operation, it goes to the timer exception.
        try:                                                                                #This is used for timer. if timed-out, it comes out of try loop and goes to exception.
            print ("Start_Timer")
            Ack_pkt,addr = udp_sock.recvfrom(buffer_size)                                   #Client receiving the Acknowledgement packet
            udp_sock.settimeout(None)                                                       #It is equivalent to sock.setblocking(0), timer is actived only for receive function which takes care of entire operation according to the FSM.

            if (Functions.Error_Condition(P_Drop)):                                         #If Data_bit_error is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.
                print ("ACKNOWLEDGEMENT PACKET DROPPED !!!")
                while(time.time() < (start_time + 0.03)):                                   #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                            pass
                print ("TIMED OUT !!! \n")
                send_successful = 0                                                         #Comes out of current loop and starts again since condition will be while(1).

            else:                                                                           #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
                pkt_seq_nmbr,sender_chksum,ack_data=Functions.ExtractData(Ack_pkt)          #Extracts the sequence number, checksum value, data from a packet

                if (Functions.Error_Condition(E_Prob)):                                     #If Data_bit_error is true, it starts to corrupt data intentionally
                        ack_data = Functions.Data_Corrupt(ack_data)                         #Function to corrupt data
                        print ("ACK CORRUPTED")

                refrenceAck ="ACK"+str(seq_nmbr)                                            #This is the referenced Acknowledgement with respect to the sequence number. (string "ACK" also added to the sequence number for user convention and to avoid confusion)
                Ack_checksum = Functions.checksum(ack_data)                                 #Finds the checksum for received acknowledgement
                ack_data = ack_data.decode("UTF-8")                                         #Decodes from byte to integer for the comparison

                #Comparing Acknowledgement
                if (ack_data != refrenceAck) or (Ack_checksum != sender_chksum ):           #if packet is corrupted or has unexpected acknowledgement it resends the packet
                        print ("Ack: {0}, sequence_number: {1}".format(ack_data,seq_nmbr))
                        print("Resending the Packet")
                        send_successful = 0                                                 #Loop continues until satisfies condition, Basically resends the packet.
                        while(time.time() < (start_time + 0.03)):                           #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                            pass
                        print ("TIMED OUT !!! \n")


                elif (ack_data == refrenceAck) and (Ack_checksum == sender_chksum ):        #if packet is not corrupted and has expected acknowledgement it does nothing. *updates sequence number for next loop
                        print ("Ack: {0}, sequence_number: {1}".format(ack_data,seq_nmbr))
                        seq_nmbr = 1-seq_nmbr                                               #updating sequence number
                        send_successful = 1                                                 #Comes out of while loop.
                        print ("Stop_Timer")

        except(socket.timeout):
            print ("TIMED OUT !!! \n")
            send_successful=0                                                               #Comes out of current loop and starts again since condition will be while(1).

    return seq_nmbr                                                                         #returns updated sequence number


'''To corrupt data packet, Set value from 0 - 99 in E_prob'''
E_Prob = 0                                                          #E_prob is the error probability and can be set from 0-99
P_Drop = 0                                                          #P_Drop is the packet dropping probability and can be set from 0-99

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              #Socket with IPV4, UDP
f = open('Trash.bmp','rb')                                          #opening a new file, this file will be transferred to the server
#change to abolsute path

fileSize = Functions.File_size(f)                                   #File size is calculated

loop = Functions.looptimes(fileSize,buffer_size)                    #finding the loop value
loop_bytes = struct.pack("!I", loop)                                #change loop from integer to byte inorder to send data from client to server
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
seq_nmbr = 0                                                        #Sequence Number is set to 0 initially
seq_nmbr = Send_Receive.RdtSendPkt(sock,addr,seq_nmbr,loop_bytes)   #sending the file size to Server
#Change to just RdtSendpkt

print('Client File Transfer Starts...')

for i in range(0,loop):                                             #it runs 'loop' times
    print("\nLoop :",i+1)                                           #Prints the Current loop. For easier way, initial print value starts from 1 (i+1, where i is 0)
    ImgPkt = f.read(buffer_size-3)                                  #reading the file, 1021 bytes at a time.
    if(i>= (loop-2)):                                               #This is used to make sure corruption is not made at last loop, if not client or server keeps on waiting for ack/data.
        E_Prob=0                                                    #Error probability manually set to zero (No corruption) if true.
        P_Drop=0                                                    #Packet Dropping probability manually set to zero (No corruption) if true.
    seq_nmbr = Send_Receive.RdtSendPkt(sock,addr,seq_nmbr,ImgPkt,E_Prob,P_Drop)    #calls the function rdt_send to send the packet
    #Change to just RdtSendpkt
    i=i+1                                                           #Loop iteration

f.close()                                                           #File closed
sock.close()                                                        #Socket Closed

end = time.time()                                                   #Gets the End time

