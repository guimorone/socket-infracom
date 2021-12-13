from socket import *
from rdt import *

RDTSocket = RDTClient()
 
while(1):
    data = RDTSocket.always_rcv()
    print(data.decode())


    