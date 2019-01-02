import socket
from datetime import datetime, timedelta
from select import select
from threading import Thread,Lock
import hashlib
expectedSeq = 0
rcvStr = ''
#set up router sockets
UDP_IP = "127.0.0.1"
UDP_PORT = 1010
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
mutex = Lock()
def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a
def make_packet(nextSeq,message):
    checksum = hashlib.md5(message.encode('utf-8')).hexdigest()
    return seqToStr(nextSeq)+';'+message+';'+checksum
def rdt_rcv(rcvpkt,addr):
    msgs = rcvpkt.split(';')
    global expectedSeq
    mutex.acquire()
    if notCorrupt(msgs[1],msgs[2]) and hasSeqNum(msgs[0],expectedSeq):
        global rcvStr
        # send the ACK
        pkt = make_packet(expectedSeq,'ACK')
        sock.sendto(pkt.encode('utf-8'),addr)
        # append to the resulting string
        rcvStr += msgs[1]
        expectedSeq+=1
        mutex.release()
        # for testing purposes
        print(msgs[1])
    else:
        pkt = make_packet(expectedSeq, 'ACK')
        mutex.release()
        sock.sendto(pkt.encode('utf-8'), addr)
def notCorrupt(data,checksum):
    chksm = hashlib.md5(data.encode('utf-8')).hexdigest()
    return chksm == checksum
def hasSeqNum(seqNum,expectedSeq):
    return int(seqNum) == expectedSeq
while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    Thread(target=rdt_rcv, args=(data.decode('utf-8'),addr)).start()