import socket
from datetime import datetime, timedelta
from select import select
from threading import Thread,Lock
import hashlib

def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a.encode('ascii')
def make_packet(nextSeq,message):
    checksum = hashlib.md5(seqToStr(nextSeq)+message).digest()
    return seqToStr(nextSeq)+message+checksum
def rdt_rcv(rcvpkt,addr):
    
    msgs = [rcvpkt[0:4], rcvpkt[4:-16], rcvpkt[-16:]]
    global expectedSeq
    mutex.acquire()    
    if notCorrupt(msgs[0]+msgs[1],msgs[2]) and hasSeqNum(msgs[0],expectedSeq):
        global rcvStr
        # send the ACK
        pkt = make_packet(expectedSeq,b'ACK')
        sock.sendto(pkt,(UDP_IP,UDP_PORT_SENDER))
        # append to the resulting string       
        rcvStr += msgs[1]
        expectedSeq+=1
        expectedSeq %= 10000
        # for testing purposes
        print(msgs[1].decode("iso-8859-1"))
        mutex.release()        
        
    else:
        pkt = make_packet(expectedSeq-1, b'ACK')
        mutex.release()
        sock.sendto(pkt, addr)
def notCorrupt(data,checksum):
    chksm = hashlib.md5(data).digest()
    return chksm == checksum
def hasSeqNum(seqNum,expectedSeq):
    return int(seqNum.decode('ascii')) == expectedSeq


mutex = Lock()
expectedSeq = 0
rcvStr = b''
UDP_IP = "127.0.0.1"
UDP_PORT = 1010
UDP_PORT_SENDER = 1015
#set up router sockets    
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))   
while True:
    data, addr = sock.recvfrom(1024)
    Thread(target=rdt_rcv, args=(data,addr)).start()  
