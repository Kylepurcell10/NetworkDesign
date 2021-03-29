import socket
import struct
import time

start = time.time()                    #This is used to find the start time of the program, elapsed time can be found by end time - start time

'''Importing IP address, port number, Buffersize'''
UDP_IP = "127.0.0.1"                 #Localhost is the IP address of this machine
UDP_PORT = 20001                        #Port Number is assigned to 5005
buffer_size = 1024                     #Buffer_size is set to 1024. packet size is 1024 with sequence number 1 byte, checksum 2 bytes, data 1021 bytes.
addr = (UDP_IP,UDP_PORT)