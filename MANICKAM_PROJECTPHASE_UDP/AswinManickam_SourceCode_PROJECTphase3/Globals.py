import socket
import struct
import datetime


start = datetime.datetime.now()        #This is used to find the start time of the program, elapsed time can be found by start time - end time
'''Importing IP address, port number, Buffersize'''
UDP_IP = "localhost"
UDP_PORT = 5005
buffer_size = 1024                     #Buffer_size is set to 1024. packet size is 1024 with sequence number 1 byte, checksum 2 bytes, data 1021 bytes.
addr = (UDP_IP,UDP_PORT)


