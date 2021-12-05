from socket import *
from rdt import *

RDTSocket = RDT()
 
file = open("teste.txt","rb") 
data = file.read(RDTSocket.bufferSize)


while data:
    RDTSocket.send_pkg(data)
    data = file.read(RDTSocket.bufferSize)



file.close()
file = open("recebidoClient.txt", "wb")

data = RDTSocket.receive()

file.write(data)
file.close()

RDTSocket.close_connection()
    