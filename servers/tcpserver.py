# Authors: Christopher L. Ayala & Coral M. Salort

import socket
import glob
import os

serverPort = 12001
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print("Ready...")
filepath = "/Users/christopherayala/Documents/ccom4205_0U1/"

while 1:
	connectionSocket, addr = serverSocket.accept()
	mensaje = connectionSocket.recv(1024)
	mensaje = mensaje.decode('utf-8')
	print(mensaje)
	pedazo = mensaje.split('\r\n')[0]
	_, filename, _ = pedazo.split(' ')
	filename = filename[1:]


	#procesesar info
	#leer archivo que se pide
	#enviar archivo que se pide
	#si lo tengo, envio archivo
	#si no lo tengo envio 404

	if(os.path.isfile(filename)):	# da TRUE si existe el file
		f = open(filepath + "index.html", 'rb')	# Abre
		content = f.read()			# Lee
		f.close()					# Cierra

		# Manda el mensaje al browser diciendo que aparecio
		connectionSocket.send(b'HTTP/1.1 200 OK\r\n\n' + content)


	else:

		# Manda mensaje al browser diciendo que no lo encontro
		connectionSocket.send(b'HTTP/1.1 404 Not Found\r\n\n')


	connectionSocket.close()
