from socket import *


bufferSize = 1024
clientAddressPort = ("127.0.0.1", 20001)

UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
UDPServerSocket.bind(clientAddressPort)

print("O servidor UDP está pronto para receber")


data,addr = UDPServerSocket.recvfrom(bufferSize)
print ("Received File:",data.strip())
file = open("recebido.txt",'wb')


try:
    while data:
        file.write(data)
        UDPServerSocket.settimeout(2)
        data,addr = UDPServerSocket.recvfrom(bufferSize)
except timeout:
    file.close()
    print ("File Downloaded")

file = open("recebido.txt","rb") 
data = file.read(bufferSize)

while data:
    if(UDPServerSocket.sendto(data, addr)):
        print ("sending ...")
        data = file.read(bufferSize)

UDPServerSocket.close()
file.close()







