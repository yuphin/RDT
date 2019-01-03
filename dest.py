import socket
from datetime import datetime, timedelta
from select import select
from threading import Thread,Lock
import hashlib

def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a
def make_packet(nextSeq,message):
    checksum = hashlib.md5((seqToStr(nextSeq)+';'+message).encode('utf-8')).hexdigest()
    return seqToStr(nextSeq)+';'+message+';'+checksum
def rdt_rcv(rcvpkt,addr,msock):
    
    msgs = rcvpkt.split(';')
    global expectedSeq
    mutex.acquire()
    if notCorrupt(msgs[0]+';'+msgs[1],msgs[2]) and hasSeqNum(msgs[0],expectedSeq):
        global rcvStr
        # send the ACK
        pkt = make_packet(expectedSeq,'ACK')
        msock.sendto(pkt.encode('utf-8'),addr)
        # append to the resulting string       
        rcvStr += msgs[1]
        expectedSeq+=1
        # for testing purposes
        print(msgs[1])
        mutex.release()        
        
    else:
        pkt = make_packet(expectedSeq-1, 'ACK')
        mutex.release()
        msock.sendto(pkt.encode('utf-8'), addr)
def notCorrupt(data,checksum):
    chksm = hashlib.md5(data.encode('utf-8')).hexdigest()
    return chksm == checksum
def hasSeqNum(seqNum,expectedSeq):
    return int(seqNum) == expectedSeq


mutex = Lock()
expectedSeq = 0
rcvStr = ''
UDP_IP = "127.0.0.1"
UDP_PORT = 1010
UDP_PORT2 = 1011
#set up router sockets    
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock2.bind((UDP_IP, UDP_PORT2))
while True:
    ready_socks, _, _ = select([sock,sock2], [], [])
    for msock in ready_socks:
        data, addr = msock.recvfrom(1024)
        Thread(target=rdt_rcv, args=(data.decode('utf-8'),addr,msock)).start()
