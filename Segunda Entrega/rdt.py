from socket import *
from utils import checksum
import time

class RDT:

    def __init__(self, isServer = 0, addressPort = ("127.0.0.1", 20001), bufferSize = 1024):
        self.sender_addr = 0
        self.seq_num = 0
        self.addressPort =  addressPort
        self.bufferSize = bufferSize
        self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        self.isServer = isServer
        if isServer:
            self.UDPSocket.bind(self.addressPort)
            self.UDPSocket.settimeout(2.0)
            print("Server running")
        else:
            print("Client running")
    
    def send(self, data):
        if self.isServer:
            print("Sending to client")
            self.UDPSocket.sendto(data, self.sender_addr)
        else:
            print("Sending to server")
            self.UDPSocket.sendto(data, self.addressPort)

    def send_pkg(self, data):
        data = self.create_header(data.decode())
        ack = False

        while not ack:
            self.send(data)

            try:
                data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
            except socket.timeout:
                print("Did not receive ACK. Sending again.")
            else:
                ack = self.rcv_ack(data)

    def receive(self):
        print("Receveing package")
        self.UDPSocket.settimeout(20.0) # tempo de espera por pacote
        data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        data = self.rcv_pkg(data)

        if data != "":
            buffer = data
        
        #while data:
        #    data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        #    buffer += data.decode()

        print("Received")
        return buffer.encode()

    def send_ack(self, ack):
        if ack:
            data = self.create_header("ACK")
        else:
            data = self.create_header("NACK")
        self.send(data)


    def rcv_pkg(self, data):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        if self.checksum_(checksum, payload) and seq_num == self.seq_num:
            self.send_ack(1)
            self.seq_num = 1 - self.seq_num
            return payload
        else:
            self.send_ack(0)
            return ""
    

    def rcv_ack(self, data):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        if self.checksum_(checksum, payload) and seq_num == self.seq_num and payload == "ACK":
            self.seq_num = 1 - self.seq_num
            return True
        else:
            return False


    def checksum_(self, chcksum, payload):
        if checksum(payload) == chcksum:
            return True
        else:
            return False


    def create_header(self, data):

        chcksum = checksum(data)

        return str({
            'seq': self.seq_num,
            'checksum': chcksum,
            'payload' : data
        }).encode()

    def close_connection(self):
        print("Closing socket")
        self.UDPSocket.close()




    


