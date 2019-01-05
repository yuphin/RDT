import socket
from datetime import datetime, timedelta
from select import select
from threading import Thread,Lock
from timeit import default_timer as timer
import hashlib
import sys

def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a.encode('ascii')
def make_packet(nextSeq,message):
    checksum = hashlib.md5(seqToStr(nextSeq)+message).digest()
    return seqToStr(nextSeq)+message+checksum
def rdt_rcv(rcvpkt,addr,msock):
    
    msgs = [rcvpkt[0:4], rcvpkt[4:-16], rcvpkt[-16:]]
    global expectedSeq
    mutex.acquire()    
    if notCorrupt(msgs[0]+msgs[1],msgs[2]) and hasSeqNum(msgs[0],expectedSeq):
        global rcvStr
        # send the ACK
        pkt = make_packet(expectedSeq,b'ACK')
        msock.sendto(pkt,addr)
        ending = msgs[1][-3:] == b'END'
        if ending:
            end = timer()
            print(round((end-start)*1000, 2), " ms")
            msgs[1] = msgs[1][:-3]
        # append to the resulting string       
        rcvStr += msgs[1]
        if ending and len(sys.argv) >= 2:
            with open(sys.argv[1], "wb") as f:
                f.write(rcvStr)
        expectedSeq+=1
        expectedSeq %= 10000
        # for testing purposes
        #print(msgs[1].decode("iso-8859-1"))
        mutex.release()        
        
    else:
        pkt = make_packet(expectedSeq-1, b'ACK')
        mutex.release()
        msock.sendto(pkt, addr)
def notCorrupt(data,checksum):
    chksm = hashlib.md5(data).digest()
    return chksm == checksum
def hasSeqNum(seqNum,expectedSeq):
    return int(seqNum.decode('ascii')) == expectedSeq


mutex = Lock()
resetMutex = Lock()
expectedSeq = 0
rcvStr = b''
start = None
reset = True
#destination ip and ports
UDP_IP = "10.10.3.2"
UDP_PORT = 20787
UDP_IP2 = "10.10.5.2"
UDP_PORT2 = 20787
#set up router sockets    
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock2.bind((UDP_IP2, UDP_PORT2))
while True:
    ready_socks, _, _ = select([sock,sock2], [], [])
    if reset:
        reset = False
        start = timer()
    for msock in ready_socks:
        data, addr = msock.recvfrom(1024)
        Thread(target=rdt_rcv, args=(data,addr,msock)).start()
