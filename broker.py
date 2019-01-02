import socket
import sys
from threading import Thread,Lock
from threading import  Timer
import hashlib
base = 0
nextSeq = 0
N = 9
timer = None
UDP_IP = "127.0.0.1"
UDP_PORT = 1010
messageList = []
reconnect = True
mutex = Lock()
def seqToStr(num):
    a = str(num)
    a = ("0"*(4- len(a))) + a
    return a
def timeout():
    print("Resend...")
def make_packet(nextSeq,message,checksum):
    return seqToStr(nextSeq)+';'+message+';'+checksum

def rdt_send(message):
    global nextSeq
    global timer
    print(nextSeq)
    if(nextSeq  < base + N):
        message = message.decode('utf-8')
        checksum = hashlib.md5(message.encode('utf-8')).hexdigest()
        pkt = make_packet(nextSeq,message,checksum)
        messageList.append(pkt)
        connectedSocket.settimeout(300)
        udpSocket.sendto(pkt.encode('utf-8'), (UDP_IP, UDP_PORT))
        mutex.acquire()
        nextSeq += 1
        mutex.release()


#set up socket for interface-1 and start listening
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.bind(("127.0.0.1", 8080))
tcpSocket.listen(1)
udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

    except socket.timeout:
        print("Socket inactive for 5 minutes, timeout")
        break

connectedSocket.close()
tcpSocket.close()
udpSocket.close()

