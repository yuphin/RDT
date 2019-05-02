import socket

incomingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
outgoingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
incomingSocket.bind(("127.0.0.1", 202))
outgoingSocket.bind(("127.0.0.1", 201))
incomingSocket.settimeout(300)

while True:
	try:
		message = incomingSocket.recv(250)
		if message:
			outgoingSocket.sendto(message, ("127.0.0.1", 81))
			incomingSocket.settimeout(300)

	except socket.timeout:
		print("Socket inactive for 5 minutes, timeout")
		break

incomingSocket.close()
outgoingSocket.close()

