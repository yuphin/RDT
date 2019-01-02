import socket
import sys
from threading import Thread
from threading import  Timer
base = 0
nextSeq = 0
N = 9
timer = None
messageList = []
def timeout():
    print("Resend...")
def make_packet(nextSeq,message,checksum):
    return [nextSeq,checksum,message]
def rdt_send(message):
    global nextSeq
    global timer
    if(nextSeq  < base + N):
        totalLength = sys.getsizeof(message)+sys.getsizeof(nextSeq)+28
        checksum = int(bin(~(totalLength)),2)
        messageList[nextSeq] = make_packet(nextSeq,message,checksum)
        #udpSocket1.sendto(message.encode('utf-8'), ("127.0.0.1", 202))
        if(base == nextSeq):
            timer = Timer(0.8,timeout)
            timer.start()
        nextSeq+=1
def routeTo(msg):
    #routing logic is XORing ASCII values of characters and looking at the LSB
    route = 0
    for ch in msg:
        route ^= ord(ch)
    route = route & 0x01

    #route the message across the respective socket
    if route:
        udpSocket1.sendto(msg.encode('utf-8'), ("127.0.0.1", 202))
    else:
        udpSocket2.sendto(msg.encode('utf-8'), ("127.0.0.1", 300))


#set up sockets for routing
udpSocket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket1.bind(("127.0.0.1", 100))
udpSocket2.bind(("127.0.0.1", 101))

#set up socket for interface-1 and start listening
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.bind(("127.0.0.1", 80))
tcpSocket.listen(1)

#separate thread for sending the data to routers
def dispatch(m):
    strs = m.decode('utf-8').split(';')
    connectedSocket.settimeout(300)
    for msg in strs:
        routeTo(msg)

reconnect = True
rdt_send("mesg")
while True:
    try:
        if reconnect:
            reconnect = False
            connectedSocket, connectedAddress = tcpSocket.accept()
            print("Accepted connection from ", connectedAddress)

        message = connectedSocket.recv(200)
        if message:
            Thread(target=dispatch,args=(message,)).start()
        else:
            print("All messages sent, waiting for reconnection...")
            reconnect = True

    except socket.timeout:
        print("Socket inactive for 5 minutes, timeout")
        break

connectedSocket.close()
tcpSocket.close()
udpSocket1.close()
udpSocket2.close()
