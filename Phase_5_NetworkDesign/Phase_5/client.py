import Functions                                                    #Functions like checksum, filesize, bit error, etc.
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

'''This function is the basically the client's RDT function to send the file.'''

def rdtSend(file,sendingSocket,addr,seq_nmbr,data,packetErrorProbability=0,packetDropProbability=0,window_size=0,base=0,loop=0,image_buffer=[],time_buffer=[]):

    if (seq_nmbr < (base+window_size)):                                                                #check for empty slots in the windows
        while ((seq_nmbr < base+window_size) and (seq_nmbr <= loop)):                                  #condition for GBN protocol (Sliding window)
            if (seq_nmbr > 0):                                                                         #Initially file size is sent through sequence number 0
                data = file.read(bufferSize-4)                                                           #print("File Read")
            packet = Functions.makePacket(seq_nmbr,Functions.makeChecksum(data),data)                         #Packet is created with the sequence number,checksum,data
            image_buffer[seq_nmbr % window_size] = packet                                              #Buffer size of window size is created and data is added to the buffer.
            sendingSocket.sendto(packet,addr)                                                               #sends the data
            print ("Packet Number_Sliding Window: ",seq_nmbr)
            time_buffer[seq_nmbr % window_size] = time.time()                                          #Time Buffer stores the start time for each packet
            seq_nmbr+=1                                                                                #sequence numbe is updated by 1
        print ("Start_Timer")
    try:                                                                                               #This is used for timer. if timed-out, it comes out of try loop and goes to exception.
        sendingSocket.settimeout(0.03)                                                                      #UDP Socket timer is added here, In this case 30 milliseconds is set as timer.If timed-out before operation, it goes to the timer exception.
        Ack_pkt,addr = sendingSocket.recvfrom(bufferSize)                                                  #Client receiving the Acknowledgement packet
        sendingSocket.settimeout(None)                                                                      #It is equivalent to sock.setblocking(0), timer is actived only for receive function which takes care of entire operation according to the FSM.

        if (Functions.errorCondition(packetDropProbability)) and (seq_nmbr< loop-window_size):                       #If Data_bit_error is true, it starts to Drop packet intentionally ! Basically The received packet not utilised/used. Also, ack packet is not dropped for the last window.
            while(time.time() < (time_buffer[base % window_size] + 0.03)):                             #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                pass
            print ("############################ ACKNOWLEDGEMENT PACKET DROPPED !!! ################################\n")
            #raise OSError                                                                             #raise OSError
        else:                                                                                          #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            pkt_seq_nmbr,sender_chksum,ack_data=Functions.extractData(Ack_pkt)                         #Extracts the sequence number, checksum value, data from a packet

            if (Functions.errorCondition(packetErrorProbability)) and (seq_nmbr< loop-window_size):                   #If Data_bit_error is true, it starts to corrupt data intentionally. Also last window packets are not corrupted.
                ack_data = Functions.dataError(ack_data)                                            #Function to corrupt data
                print ("############################ ACK CORRUPTED ################################")

            Ack_checksum = Functions.makeChecksum(ack_data)                                                #Finds the checksum for received acknowledgement
            ack_data = ack_data.decode("UTF-8")                                                        #Decodes from byte to integer for the comparison
            ack_data_int = int(ack_data[3:len(ack_data)])                                              #Gets the integer value alone from the ACK. for example, if string 'ACK500' is the input then the output will be integer of 500
            #print ("Ack from Server: ",ack_data_int)

            '''Comparing Acknowledgement'''
            if ( ack_data_int >= base) and (Ack_checksum == sender_chksum ):                           #if packet is not corrupted and has expected sequence number
                base=ack_data_int +1                                                                   #base value is the next value to the ack value
                print ("ACK OKAY: ",ack_data)
                print ("Updated Base: ",base)
                print ("Stop Timer\n")

            elif (Ack_checksum != sender_chksum ):                                                     #if packet is corrupted, it resends the packet
                print ("Ack NOT OKAY:{} \n".format(ack_data))                                          #Do Nothing

    except (socket.timeout,OSError):
        print ("############################ SOCKET TIMED OUT !!! ################################")
        print ("Base: ",base)
        for i in range (base,seq_nmbr):                                                                #Resends the entire packet
            time_buffer[i % window_size] = time.time()                                                 #Restarting the timer, updating start time for the packet
            sendingSocket.sendto(image_buffer[i % window_size],addr)                                        #Sending the data
            print ("Sending the packet: ",i)
        print ("\n")
    return seq_nmbr,base                                                                                   #returns updated sequence number, base value


#To corrupt acknowledgemnt packet, Set one of these value to a number from 0 - 99
#packetErrorProbability controls the probability of a bit error within X% of packets
packetErrorProbability = 0
#packetDropProbability is the probability that a packet is dropped in the data transfer
packetDropProbability = 0

Time_buffer=[None]*Window_Size                                      #Time_Buffer stores the start time for the packets
print ("window_Size: ",Window_Size)                                 #prints the window size
image_buffer=[None]*Window_Size                                     #Stores the data in the buffer
ClientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              #Socket with IPV4, UDP
filename = 'Trash.bmp'
file = open(filename,'rb')                                           #opening a new file, this file will be transferred to the server

fileSize = Functions.fileSize(file)                                   #File size is calculated

loop = Functions.looptimes(fileSize,bufferSize)                    #finding the loop value
loop_bytes = struct.pack("!I", loop)                                #change loop from integer to byte inorder to send data from client to server
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
seq_nmbr = 0                                                        #Sequence Number is set to 0 initially
base=0                                                              #Here base is set to 0
print('Client File Transfer Starts...')

while (base <= loop):                                               #Loop runs until sequence number is equal to loop value. Sequence number starts from 1.
    seq_nmbr,base = rdtSend(file,ClientSocket,addr,seq_nmbr,loop_bytes,packetErrorProbability,packetDropProbability,Window_Size,base,loop,image_buffer,Time_buffer) #calls the function rdt_send to send the packet

file.close()                                                           #File closed
ClientSocket.close()                                                        #Socket Closed

end = time.time()                                                   #Gets the End time
Elapsed_time = end - start                                          #Gets the elapsed time
print ("Client: File Sent\nFile size sent to server: {0}\nTime taken in Seconds:{1}s\n".format(fileSize,Elapsed_time))