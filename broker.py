import socket
import sys
import threading
from threading import Thread,Lock
from threading import  Timer
from select import select
import hashlib
base = 0
nextSeq = 0
N = 9
routeSwitch = 1
timer = None
# destination ip and ports
UDP_IP = "127.0.0.1"
UDP_PORT = 1010
UDP_PORT2 = 1011
#SENDER SOCKET
UDP_PORT_SENDER = 1015
UDP_PORT_SENDER2 = 1016
# list that holds the packets from TCP stream
messageList = []
reconnect = True
mutex = Lock()
ackMutex = Lock()
routeMutex = Lock()
def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a
#Timeout callback
def timeout():
    global timer
    timer = Timer(0.8, timeout)
    timer.start()
    mutex.acquire()
    for i in range(base,nextSeq):
        udpSendingSocket.sendto(messageList[i].encode('utf-8'), (UDP_IP, UDP_PORT))
    mutex.release()
    print("Resending from this thread: ", threading.current_thread())
#Create packet with data checksum and  ; as delimiter
def make_packet(nextSeq,message):
    msg = seqToStr(nextSeq)+';'+message
    msg = msg + ";" + hashlib.md5(msg.encode('utf-8')).hexdigest()
    return msg
def refuse_data(message):
    # just add the data to the global messageList
    mereconnectssage = message.decode('utf-8')

    pkt = make_packet(nextSeq, message)
    messageList.append(pkt)
def routeTo(pkt):
    route = 0
    for ch in pkt:
        route ^= ord(ch)
    route = route & 0x01

    if route:
        print('a is a')
        udpSendingSocket.sendto(pkt.encode('utf-8'), (UDP_IP, UDP_PORT))
    else:
        print('b is b')
        udpSendingSocket2.sendto(pkt.encode('utf-8'), (UDP_IP, UDP_PORT2))
def rdt_send(message):
    global nextSeq
    global timer
    if(nextSeq  < base + N):
        message = message.decode('utf-8')
        if message[-3:] == "END":
            message = message[0:-3]
        pkt = make_packet(nextSeq,message)
        messageList.append(pkt)
        connectedSocket.settimeout(300)
        routeMutex.acquire()
        routeTo(pkt)
        routeMutex.release()
        mutex.acquire()
        if (base == nextSeq and timer is  None):
            timer = Timer(0.8, timeout)
            timer.start()
        nextSeq +=1
        mutex.release()
    else:
        refuse_data(message)
def notCorrupt(data,checksum):
    chksm = hashlib.md5(data.encode('utf-8')).hexdigest()
    return chksm == checksum
def rdt_rcv(rcvpkt):
    msgs = rcvpkt.split(';')
    if notCorrupt(msgs[0]+';'+msgs[1],msgs[2]):
        global base
        global timer
        ackMutex.acquire()
        base = int(msgs[0])+1
        if msgs[1] == "END":
            global reconnect
            reconnect = True
        ackMutex.release()
        mutex.acquire()
        if base == nextSeq:
            timer.cancel()
            timer = None
        else:
            timer.cancel()
            timer = Timer(0.8, timeout)
            timer.start()
        mutex.release()

#set up socket for interface-1 and start listening
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.bind(("127.0.0.1", 8080))
tcpSocket.listen(1)
udpSendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSendingSocket.bind((UDP_IP, UDP_PORT_SENDER))
udpSendingSocket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSendingSocket2.bind((UDP_IP, UDP_PORT_SENDER2))

while True:
    try:
        if reconnect:
            reconnect = False
            connectedSocket, connectedAddress = tcpSocket.accept()
            print("Accepted connection from ", connectedAddress)
        message = connectedSocket.recv(200)
        if message:
            Thread(target=rdt_send,args=(message,)).start()
        else:
            print("All messages sent, waiting for reconnection...")
            reconnect = True
        if not reconnect:
            ready_socks, _, _ = select([udpSendingSocket, udpSendingSocket2], [], [])
            for sock in ready_socks:
                ack, addr = sock.recvfrom(200)
                # ACK Section
                Thread(target=rdt_rcv, args=(ack.decode('utf-8'),)).start()
    except socket.timeout:
        print("Socket inactive for 5 minutes, timeout")
        break

connectedSocket.close()
tcpSocket.close()
udpSendingSocket.close()

