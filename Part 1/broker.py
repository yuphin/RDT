import socket
from threading import Thread
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

#handle display
residueString = ""
'''
def dispatch(residueString):
    messageStrs = message.split('\n')
    sourceTime = messageStrs[0]
    messageStrs[1] = residueString + messageStrs[1]
    residueString = messageStrs[-1]
    for messageStr in messageStrs[1:-1]:
        routeTo(sourceTime + "\n" + messageStr)
'''
def dispatch(m):
    strs = m.decode('utf-8').split(';')
    connectedSocket.settimeout(300)
    for msg in strs:
        routeTo(msg)
while True:
    try:
        connectedSocket, connectedAddress = tcpSocket.accept()
        print("accepted connection from ", connectedAddress)

        message = connectedSocket.recv(200)
        if message:
            Thread(target=dispatch,args=(message,)).start()
    except socket.timeout:
        print("Socket inactive for 5 minutes, timeout")
        break

connectedSocket.close()
tcpSocket.close()
udpSocket1.close()
udpSocket2.close()
