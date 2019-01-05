import socket
import sys
import threading
from threading import Thread,Lock
from threading import  Timer
from select import select
import hashlib
#base number
base = 0
#next sequence number, as in go back n
nextSeq = 0
# window size
N = 10
#global timer variable
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
# message buffer that our UDP protocol fills in
messageList = []
# list(buffer) that holds the packets from TCP stream
tcpList = []
# buffer Index as mentioned in the report
tcpIndex = 0
tcpMutex = Lock()
reconnect = True
#mutexes
mutex = Lock()
ackMutex = Lock()
routeMutex = Lock()
#4 byte sequence number, since our payload is around 1000 byte and the file we're getting is 5MB, 4 bytes of characters are enough 
def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a.encode('ascii')
#Timeout callback
def timeout():
    global timer
    timer = Timer(0.15, timeout)
    timer.start()
    #Resend from base to the next sequence number
    for i in range(base,nextSeq):
        routeTo(messageList[i])
    print("Resending from", base, "to(including)", nextSeq-1)
#Create packet with data checksum
def make_packet(nextSeq,message):
    # prepend sequence number to the message
    msg = seqToStr(nextSeq)+message
    #Checksum is an md5 hash, for both sequence number and the data
    msg = msg+hashlib.md5(msg).digest()
    return msg
#Route the packet
def routeTo(pkt):
    # XOR the checksum to determine which path is going to be taken
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
    global tcpIndex
    # if the next packet to be sent is in the window range...
    if(nextSeq  < (base + N)%10000):
        tcpMutex.acquire()
        #Mutexes are locked because we are accessing the global TCP buffer index
        message = None
        if tcpIndex < len(tcpList):
            message  = tcpList[tcpIndex]
        else:
            # If the TCP buffer isn't ready, simply return
            tcpMutex.release()
            return
        tcpIndex+=1
        tcpMutex.release()
        # Create checksum
        checksum = hashlib.md5(message).digest()
        mutex.acquire()
        #Create packet
        pkt = make_packet(nextSeq,message)
        #Fill the message buffer
        messageList.append(pkt)
        #connectedSocket.settimeout(300)
        routeTo(pkt)
        # If the current packet we are sending is equal to the base num, start the timer
        if (base == nextSeq and timer is  None):
            timer = Timer(0.15, timeout)
            timer.start()
        nextSeq +=1
        nextSeq %= 10000
        mutex.release()
    else:
        pass
#Simply compare the payload checksum with the message checksum
def notCorrupt(data,checksum):
    chksm = hashlib.md5(data).digest()
    return chksm == checksum
#Utility function, explained below
def isGreaterSeqNum(seqNum,expectedSeq):
    num = int(seqNum.decode('ascii'))
    return num >= expectedSeq
def rdt_rcv(rcvpkt):
    msgs = [rcvpkt[0:4], rcvpkt[4:-16], rcvpkt[-16:]]
    global base
    # If the data is not corrupt and the ACK num we are getting is greater than or equal to the base number
    if notCorrupt(msgs[0]+msgs[1],msgs[2]) and isGreaterSeqNum(msgs[0],base):
        global timer
        ackMutex.acquire()
        #Increment the base
        base = (int(msgs[0].decode('ascii'))+1)%10000
        print("gotten", str(int(msgs[0].decode('ascii'))))
        ackMutex.release()
        mutex.acquire()
        #If the base is equal to the next sequence number stop the timer
        if base == nextSeq:
            timer.cancel()
            timer = None
        else:
        #Else, restart the timer
            timer.cancel()
            timer = Timer(0.15, timeout)
            timer.start()
        mutex.release()
#Simply add the TCP stream data to the buffer
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
        #Read TCP stream
        message = connectedSocket.recv(950)
        if message:
            #Dispatch a thread for TCP stream data
            Thread(target=handleTCPStream,args=(message,)).start()
        
        if tcpList:
            #If the TCP buffer is not empty, dispatch a thread for sending data.
            Thread(target=rdt_send).start()
        #Select from either of the sockets
        ready_socks, _, _ = select([udpSendingSocket, udpSendingSocket2], [], [])
        for sock in ready_socks:
            ack, addr = sock.recvfrom(200)
            # Upon receiving ACK, dispatch it
            Thread(target=rdt_rcv, args=(ack,)).start()
    except socket.timeout:
        print("Socket inactive for 5 minutes, timeout")
        break

connectedSocket.close()
tcpSocket.close()
udpSendingSocket.close()
