import socket
from datetime import datetime, timedelta
from select import select
from threading import Thread

#handle end-to-end delay calculation and check message integrity
def display(msg, time):
    '''
    msgSplit = msg.split('-')
    #check message integrity
    if len(msgSplit) == 3 and msg.endswith('_'):

        try:
            #get timestamp from datetime variable-python3 feature
            sentTime = datetime.strptime(msgSplit[0], "%Y %m %d %H %M %S %f").timestamp()
        except ValueError:
            #throw exception if the date data is not intact
            return
            #calculate the time in milliseconds
        elapsed = time*1000 - sentTime*1000
        print(elapsed)
    '''
    print(msg)

#set up router sockets
UDP_IP = "127.0.0.1"
UDP_PORT = 1010
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print(data.decode('utf-8'))