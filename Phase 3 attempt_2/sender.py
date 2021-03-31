import base64
import random
import sys
import time
import binascii
from socket import *

class server():
    def __init__(self):
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverName = "localhost"
        self.serverRPort = 7380
        self.serverSPort = 7356
        self.clientSocket.bind(('', self.serverRPort))
        self.chunk_size = 1024
        self.ck_size=0
        self.resend=1
        self.seq = 0
        self.x_percent = 1
        self.corruption = False
    
    def send_msg(self, msg):
        self.clientSocket.sendto(msg,(self.serverName, self.serverSPort))
    	time.sleep(.001)
    
    def make_chunks(self,data):
        file_size = len(data)
        no_pkts = file_size/self.chunk_size
        rem1 = file_size % self.chunk_size
        if(rem1):
            no_pkts = no_pkts+1
        print (no_pkts)
        pkt = []
        for i in range (0,no_pkts):
            pkt.append(data[i*self.chunk_size:(i+1)*self.chunk_size])
            #print i
        print ("starting..")
        self.send_msg("no of packets")
        print ("sending file size")
        self.send_msg(str(no_pkts))
        self.send_msg("chunk size")
        self.send_msg(str(self.chunk_size))
        return pkt

    def checksum(self, pkt):
        sum = 0
        data_hex = binascii.hexlify(pkt)
        for i in data_hex:
            sum = sum + int(i,16)
            #sum = str(sum)
        #print "sum is "+sum
        return (sum)
            
    def make_packets(self,data):
        check_sum=self.checksum(data)
        self.ck_size = len(str(check_sum))
        #print "Sent checksum"
        pkt =str(self.seq)+str(check_sum)+data
        return(pkt)

    def serverSend(self):
        print ("Choose 1 options out of 3. Enter 1/2/3")
        print ("1. No Error\n2. Ack Error\n3. Data Error")
        option = input('--> ')
        self.send_msg("option")
        self.send_msg(str(option))
        count = 0
        #r_count = 0

        if(int(option) == 2 or int(option) == 3):
            print ("Enter the % of corruption")
            self.x_percent = input("--> ")
    	if(int(option) == 3):
            self.send_msg(self.x_percent)
        with open("high snow.jpg","rb") as file1:
        	str1 = base64.b64encode(file1.read())
        	pkts = self.make_chunks(str1)
        	while 1:
			print ("Sending pkts now..")
                start_time = time.time()
            	for x in pkts:
                #count=count+1
                #print"packet count is "+str(count)
                    x = self.make_packets(x)
                    #print "length of packet is "+str(len(x))
                    self.resend =1
                while(self.resend):
                    self.send_msg("Checksum")
                    self.send_msg(str(self.ck_size))
                    self.send_msg("packet size")
                    self.send_msg(str(len(x)))
                    self.send_msg(x)
                    #print "Sent packet"
                    #r_count = r_count+1
                    #print "resend count is "+str(r_count)
                    ack, clientAddress = self.clientSocket.recvfrom(2048)
                    ack = int(ack)
                        if(int(option) == 2):
                            #print "I am at ack"
                        lim = 100/int(self.x_percent)
                        if(random.randint(0,lim)==1):
                            ack = ~ack
                            #print ack
                            #print "ack mrecieved "+ str(ack)
                        if(self.seq == ack):
                            self.resend =0
                            #print "Match"
                            if (self.seq == 0):
                                self.seq = 1
                            else:
                                self.seq = 0
                                
            		file1.close()
			end_time = time.time()
        		print ("Time taken is %s" %(end_time-start_time))
            		break