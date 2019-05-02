import socket
from datetime import datetime
messageFile = open("readings.txt", 'r')
message = messageFile.read()
messageFile.close()

#create socket and connect to interface-1 of broker
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sampleSize = 600

try:
	#soc.connect(("10.10.1.2", 12345))
    soc.connect(("127.0.0.1", 80))
    for i in range(0,sampleSize):
        currentTime = datetime.utcnow().strftime("%Y %m %d %H %M %S %f")
        soc.send((currentTime + '-' + "message"+str(i)+';').encode('utf-8'))
except socket.error:
    print("Connection failed: Destination port not open.")


