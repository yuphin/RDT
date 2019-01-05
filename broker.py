import socket
import sys
import threading
from threading import Thread,Lock
from threading import  Timer
from select import select
import hashlib
base = 0
nextSeq = 0
N = 10
routeSwitch = 1
timer = None
# destination ip and ports
UDP_IP = "10.10.3.2"
UDP_PORT = 20787
UDP_IP2 = "10.10.5.2"
UDP_PORT2 = 20787
# source ip and ports
UDP_SENDER_IP = "10.10.2.1"
UDP_SENDER_IP2 = "10.10.4.1"
UDP_PORT_SENDER = 20888
UDP_PORT_SENDER2 = 20888
# list that holds the packets from TCP stream
messageList = [None]*6000
reconnect = True
mutex = Lock()
ackMutex = Lock()
routeMutex = Lock()
def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a.encode('ascii')
#Timeout callback
def timeout():
    global timer
    timer = Timer(0.15, timeout)
    timer.start()
    for i in range(base,nextSeq):
        routeTo(messageList[i])
    print("Resending from", base, "to(including)", nextSeq-1)
#Create packet with data checksum
def make_packet(nextSeq,message):
    msg = seqToStr(nextSeq)+message
    msg = msg+hashlib.md5(msg).digest()
    return msg
def refuse_data(message):
    # just add the data to the global messageList
    mereconnectssage = message


    mutex.acquire()
    pkt = make_packet(nextSeq, message)
    messageList[nextSeq]=pkt
    mutex.release()

def routeTo(pkt):
    route = 0
    for ch in pkt[-16:]:
        route ^= ch
    route = route & 0x01
    if route:
        udpSendingSocket.sendto(pkt, (UDP_IP, UDP_PORT))
    else:
        udpSendingSocket2.sendto(pkt, (UDP_IP2, UDP_PORT2))
def rdt_send():
    global nextSeq
    global timer
    mutex.acquire()
    if(nextSeq  < (base + N)%10000 or (nextSeq >= 10000 - N and nextSeq < (base + N))):
        mutex.release()
        if message[-3:] == b"END":
            message = message[0:-3]
        mutex.acquire()
        pkt = make_packet(nextSeq,message)
        mutex.release()
        connectedSocket.settimeout(300)
        routeTo(pkt)
        mutex.acquire()
        print(nextSeq)
        messageList[nextSeq] = pkt
        if (base == nextSeq and timer is  None):
            timer = Timer(0.15, timeout)
            timer.start()
        nextSeq +=1
        nextSeq %= 10000
        mutex.release()
    else:
        pass
def notCorrupt(data,checksum):
    chksm = hashlib.md5(data).digest()
    return chksm == checksum

def rdt_rcv(rcvpkt):
    msgs = [rcvpkt[0:4], rcvpkt[4:-16], rcvpkt[-16:]]
    if notCorrupt(msgs[0]+msgs[1],msgs[2]):
        global base
        global timer
        ackMutex.acquire()
        base = (int(msgs[0].decode('ascii'))+1)%10000
        print("gotten", str(int(msgs[0].decode('ascii'))))
        ackMutex.release()
        mutex.acquire()
        if base == nextSeq:
            timer.cancel()
            timer = None
        else:
            timer.cancel()
            timer = Timer(0.15, timeout)
            timer.start()
        mutex.release()
def handleTCPStream(message):
    tcpList.append(message)
#set up socket for interface-1 and start listening
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.bind(("10.10.1.2", 20800))
tcpSocket.listen(1)
udpSendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSendingSocket.bind((UDP_SENDER_IP, UDP_PORT_SENDER))
udpSendingSocket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSendingSocket2.bind((UDP_SENDER_IP2, UDP_PORT_SENDER2))
connectedSocket, connectedAddress = tcpSocket.accept()
print("Accepted connection from ", connectedAddress)
while True:
    try:
        if reconnect:
            reconnect = False
            connectedSocket, connectedAddress = tcpSocket.accept()
            print("Accepted connection from ", connectedAddress)
        message = connectedSocket.recv(970)
        if message:
            Thread(target=handleTCPStream,args=(message,)).start()
        
        if tcpList:
            Thread(target=rdt_send).start()
        ready_socks, _, _ = select([udpSendingSocket, udpSendingSocket2], [], [])
        for sock in ready_socks:
            ack, addr = sock.recvfrom(200)
            # ACK Section
            Thread(target=rdt_rcv, args=(ack,)).start()
    except socket.timeout:
        print("Socket inactive for 5 minutes, timeout")
        break

connectedSocket.close()
tcpSocket.close()
udpSendingSocket.close()
