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
    print("Trying to connect to broker...")
    soc.connect(("10.10.1.2", 20800))
    print("Connected")
    try:
        #○pen the file
        with open(sys.argv[1], "rb") as f:
            msg = f.read()
        #send the message
        soc.send(msg)
        #send terminating command-END
        terminate()
    except socket.error:
        print("Connection failed: Destination port not open.")

