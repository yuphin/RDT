import socket
import signal
from datetime import datetime
from time import sleep
import sys

def terminate():
    soc.send(b"END")
    soc.close()

if len(sys.argv) != 2:
    print ("Correct usage: source.py file_to_be_sent")

else:
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)
    # create socket and connect to interface-1 of broker
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # message size to be sent
    sampleSize = 5000
    # send the emulation delay data along with the message- not used for now
    netem = 1
    print("Trying to connect to broker...")
    soc.connect(("127.0.0.1", 8080))
    print("Connected")
    try:
        with open(sys.argv[1], "rb") as f:
            msg = f.read()
        soc.send(msg)
        #for i in range(0, sampleSize):
            # get current time
            #currentTime = datetime.utcnow().strftime("%Y %m %d %H %M %S %f")
            # generate time
            #soc.send(('asdasdsadsadsadsa--hihihihi'+str(i)+'-').encode('utf-8'))
            #soc.send(msg)
            # sleep for 8 milliseconds before sending a message again
        terminate()
    except socket.error:
        print("Connection failed: Destination port not open.")

