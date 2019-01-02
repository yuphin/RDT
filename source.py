import socket
from datetime import datetime
from time import sleep

# create socket and connect to interface-1 of broker
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# message size to be sent
sampleSize = 500
# send the emulation delay data along with the message- not used for now
netem = 1

soc.connect(("127.0.0.1", 8080))
try:
    for i in range(0, sampleSize):
        # get current time
        #currentTime = datetime.utcnow().strftime("%Y %m %d %H %M %S %f")
        # generate time
        soc.send(('hi'+str(i)).encode('utf-8'))
        # sleep for 8 milliseconds before sending a message again
        sleep(0.08)
except socket.error:
    print("Connection failed: Destination port not open.")
