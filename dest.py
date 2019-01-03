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
def rdt_rcv(rcvpkt,addr):
    
    msgs = rcvpkt.split(';')
    global expectedSeq
    mutex.acquire()
    if notCorrupt(msgs[0]+';'+msgs[1],msgs[2]) and hasSeqNum(msgs[0],expectedSeq):
        global rcvStr
        # send the ACK
        pkt = make_packet(expectedSeq,'ACK')
        sock.sendto(pkt.encode('utf-8'),(UDP_IP,UDP_PORT_SENDER))
        # append to the resulting string       
        rcvStr += msgs[1]
        expectedSeq+=1
        # for testing purposes
        print(msgs[1])
        mutex.release()        
        
    else:
        pkt = make_packet(expectedSeq-1, 'ACK')
        mutex.release()
        sock.sendto(pkt.encode('utf-8'), addr)
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
UDP_PORT_SENDER = 1015
#set up router sockets    
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))   
while True:
    data, addr = sock.recvfrom(1024)
    Thread(target=rdt_rcv, args=(data.decode('utf-8'),addr)).start()  
