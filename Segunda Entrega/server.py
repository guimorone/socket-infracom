from socket import *
from rdt import *


RDTSocket = RDT(1)

data = RDTSocket.receive()

file = open("recebido.txt",'wb')
file.write(data)
file.close()

file = open("recebido.txt","rb") 
data = file.read(RDTSocket.bufferSize)

while data:
    RDTSocket.send_pkg(data)
    data = file.read(RDTSocket.bufferSize)

RDTSocket.close_connection()
file.close()






