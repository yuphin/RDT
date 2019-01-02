import socket
from datetime import datetime, timedelta
from select import select
from threading import Thread

#handle end-to-end delay calculation and check message integrity
def display(msg, time):
    msgSplit = msg.split('-')
    #check message integrity
    if len(msgSplit) == 3 and msg.endswith('_'):

        try:
            #get timestamp from datetime variable-python3 feature
            sentTime = datetime.strptime(msgSplit[0], "%Y %m %d %H %M %S %f").timestamp()
        except ValueError:
            #throw exception if the date data is not intact
            return
            #calculate the time in milliseconds
        elapsed = time*1000 - sentTime*1000
        print(elapsed)

#set up router sockets
router1Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router2Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router1Socket.bind(("127.0.0.1", 81))
router2Socket.bind(("127.0.0.1", 82))
while True:
    try:
        # check which sockets are ready for reading
        r1Socket = router1Socket
        rlist, w, x = select([router1Socket, router2Socket], [], [], 0)
        messages = []
	
        for availableSocket in rlist:
            # will run unblockingly whenever a socket has a data rata
            msg = availableSocket.recv(250)
            if msg:
                messages.append(msg)
                
	#set currentTime regardless(will be set upon packet arrival)
        currentTime = datetime.utcnow().timestamp()
        for message in messages:
            display(message.decode('utf-8'), currentTime)
        
    except socket.error:
        print("Connection failed")
