from socket import *
import sys
import time
import base64
import binascii
import random

class client():
    def __init__(self):
        self.serverRPort = 7356
        self.serverSPort = 7380
        self.serverName = "localhost"
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('', self.serverRPort))
        self.seq=0
        self.ACK=0
        self.allok =1
        self.allok1 = 1
        self.check_sum=0
        self.corruption = False
        self.x_percent =1
        print ("Server is ready to recieve!")
    
    def checksum(self, data):
        sum = 0
        #print "I am at checksome"
        data_hex = binascii.hexlify(data)
        for i in data_hex:
            sum = sum + int(i,16)
        if(sum != self.check_sum):
            self.allok1 =0
        else:
            self.allok1 = 1
        return 0
    
    def make_corrupt(self,data):
        lim = 100/int(self.x_percent)
        #rand_int = random.randint(0,lim)
        if(random.randint(0,lim) == 1):
            data="377485854985"
            self.ACK=~self.ACK
            if(self.seq == 0):
                self.seq=1
            else:
                self.seq=0
            #print "corrupted ack is "+str(self.ACK)
        return(data)
        

    def extract_header(self, pkt,ck_size):
        print ("I am extracting")
        sequence=int(pkt[0])
        self.ACK=sequence
	#print "my ack is "+str(self.ACK)
        if(sequence!=self.seq):
            self.allok=0
        else:
	    self.allok=1
            #print "all ok"
	    #print "my sequence is "+str(self.seq)
            if(self.seq == 0):
                self.seq=1
            else:
                self.seq=0
        self.check_sum = int(pkt[1:ck_size+1])
        data = pkt[ck_size+1:]
        if (self.corruption):
            data = self.make_corrupt(data)
        #print "length of data is " + str(len(data))
        return(data)

    def send_msg(self, msg):
        self.serverSocket.sendto(msg,(self.serverName, self.serverSPort))
    	time.sleep(.001)


    def clientRecv(self):
        msg, clientAddress = self.serverSocket.recvfrom(2048)
        print (msg)
        if (msg == "option"):
            option, clientAddress = self.serverSocket.recvfrom(2048)
            print (option)
        if(int(option)==3):
            self.x_percent, clientAddress = self.serverSocket.recvfrom(2048)
            self.corruption = True
        msg1, clientAddress = self.serverSocket.recvfrom(2048)
        print (msg1)
        if (msg1 == "no of packets"):
                no_pkts, clientAddress = self.serverSocket.recvfrom(2048)
                print (no_pkts)
        msg2, clientAddress = self.serverSocket.recvfrom(2048)
        print (msg2)
        if (msg2 == "chunk size"):
            chunk_size, clientAddress = self.serverSocket.recvfrom(2048)
            print (chunk_size)
        no_pkts = int(no_pkts)
        chunk_size = int(chunk_size)
        count = 0
        fin_data =[]
        while 1:
            msg3, clientAddress = self.serverSocket.recvfrom(2048)
            if (msg3 == "Checksum"):
                ck_size, clientAddress = self.serverSocket.recvfrom(2048)
                #print ck_size
                ck_size = int(ck_size)
        
            msg4, clientAddress = self.serverSocket.recvfrom(2048)
            if (msg4 == "packet size"):
                pkt_size, clientAddress = self.serverSocket.recvfrom(2048)
                #print pkt_size
                pkt_size = int(pkt_size)
                
            pkt, addr = self.serverSocket.recvfrom(pkt_size)
            if(pkt):
                pkt = self.extract_header(pkt,ck_size)
                self.checksum(pkt)
                self.send_msg(str(self.ACK))
                if(self.allok and self.allok1):
                    fin_data.append(pkt)
                    count = count+1
            if(count == no_pkts):
                break
        str1 = ''.join(fin_data)
        with open("snow.jpg","wb") as file2:
            file2.write(base64.decodestring(str1))
            file2.close()
        print ("File downloaded")
        

			 		
obj2 = client()
obj2.clientRecv()