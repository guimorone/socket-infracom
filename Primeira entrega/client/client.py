from socket import *

serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024

UDPClientSocket = socket(AF_INET, SOCK_DGRAM)
UDPClientSocket.bind(serverAddressPort)

file = open("teste.txt","rb") 
data = file.read(bufferSize)

while data:
    if(UDPClientSocket.sendto(data, serverAddressPort)):
        print ("sending ...")
        data = file.read(bufferSize)



file.close()
file = open("recebido.txt", "wb")

UDPClientSocket.bind(("127.0.0.1", 20000))

data,addr = UDPClientSocket.recvfrom(bufferSize)

try:
    while data:
        file.write(data)
        UDPClientSocket.settimeout(2)
        data,addr = UDPClientSocket.recvfrom(bufferSize)
except timeout:
    file.close()
    UDPClientSocket.close()
    print ("File Downloaded")
