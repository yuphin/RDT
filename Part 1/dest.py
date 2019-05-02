import socket
from datetime import datetime, timedelta
from select import select

def display(msg, time):
    msgSplit = msg.split('-')
    if len(msgSplit) > 1:
        try:
            sentTime = datetime.strptime(msgSplit[0], "%Y %m %d %H %M %S %f")
        except ValueError:
            return
        elapsed = time - sentTime
        delayMs = elapsed.total_seconds() * 1000
        print("Delay: ", delayMs, " ms")
    print(msgSplit[-1])

#set up router sockets
router1Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router2Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router1Socket.bind(("127.0.0.1", 81))
router2Socket.bind(("127.0.0.1", 82))

while True:
    try:
        # check which sockets are ready for reading
        rlist, w, x = select([router1Socket, router2Socket], [], [], 0)
        messages = []
        for availableSocket in rlist:
            messages.append(availableSocket.recv(250))

        currentTime = datetime.utcnow()
        for message in messages:
            display(message.decode('utf-8'), currentTime)
    except socket.error:
        print("Connection failed")
